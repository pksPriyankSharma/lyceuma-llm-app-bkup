# messenger/views.py
import json
import os
from uuid import uuid4
from datetime import datetime

from django.conf import settings
from django.core.files.storage import default_storage
from django.http import JsonResponse, HttpResponseNotAllowed
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_POST, require_GET
from django.views.decorators.csrf import ensure_csrf_cookie

from .models import UploadedPDF
from .tasks import process_pdf  # Celery task (will call .delay)

@ensure_csrf_cookie
def index(request):
    return render(request, 'messenger/index.html')


@require_POST
def receive_text(request):
    try:
        payload = json.loads(request.body.decode('utf-8'))
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)

    text = (payload.get('text') or '').strip()
    response = {'status': 'ok', 'received': text, 'length': len(text)}
    return JsonResponse(response)


@require_POST
def upload_pdf(request):
    uploaded_file = request.FILES.get('file')
    if not uploaded_file:
        return JsonResponse({'status': 'error', 'message': 'No file provided'}, status=400)

    filename = uploaded_file.name
    ext = os.path.splitext(filename)[1].lower()
    allowed_ext = ['.pdf']
    max_size_bytes = 20 * 1024 * 1024  # 20 MB

    content_type = uploaded_file.content_type or ''
    if ext not in allowed_ext and 'pdf' not in content_type.lower():
        return JsonResponse({'status': 'error', 'message': 'Only PDF files are allowed'}, status=400)
    if uploaded_file.size > max_size_bytes:
        return JsonResponse({'status': 'error', 'message': 'File too large (max 20 MB)'}, status=400)

    # Save file via model's FileField:
    instance = UploadedPDF(
        original_name=filename,
        size=uploaded_file.size,
        status=UploadedPDF.STATUS_PENDING
    )
    instance.file.save(f"{uuid4().hex}_{filename}", uploaded_file, save=True)

    # Kick off background indexing task (Celery)
    try:
        process_pdf.delay(instance.id)
    except Exception:
        # If Celery not running or misconfigured, still return success but mark as pending
        # Keep status PENDING - worker will pick up when available.
        pass

    return JsonResponse({
        'status': 'ok',
        'message': 'File uploaded successfully',
        'id': instance.id,
        'original_name': instance.original_name,
        'file_url': instance.file.url,
        'size': instance.size,
        'status_field': instance.status,
    })


@require_GET
def list_uploads(request):
    items = []
    for inst in UploadedPDF.objects.all():
        items.append({
            'id': inst.id,
            'display_name': inst.original_name,
            'file_url': inst.file.url,
            'size': inst.size,
            'status': inst.status,
            'embeddings_stored': inst.embeddings_stored,
            'uploaded_at': inst.uploaded_at.isoformat(),
        })
    return JsonResponse({'status': 'ok', 'files': items})


@require_GET
def file_details(request, pk):
    inst = get_object_or_404(UploadedPDF, pk=pk)
    return JsonResponse({
        'status': 'ok',
        'id': inst.id,
        'display_name': inst.original_name,
        'file_url': inst.file.url,
        'size': inst.size,
        'status_field': inst.status,
        'embeddings_stored': inst.embeddings_stored,
        'uploaded_at': inst.uploaded_at.isoformat(),
    })


@require_POST
def file_delete(request, pk):
    inst = get_object_or_404(UploadedPDF, pk=pk)
    # Delete file from storage
    try:
        storage_path = inst.file.name
        inst.file.delete(save=False)
    except Exception:
        pass
    inst.delete()
    return JsonResponse({'status': 'ok', 'message': 'File deleted'})


@require_POST
def file_rename(request, pk):
    inst = get_object_or_404(UploadedPDF, pk=pk)
    try:
        payload = json.loads(request.body.decode('utf-8'))
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
    new_name = (payload.get('new_name') or '').strip()
    if not new_name:
        return JsonResponse({'status': 'error', 'message': 'new_name required'}, status=400)
    inst.original_name = new_name
    inst.save(update_fields=['original_name'])
    return JsonResponse({'status': 'ok', 'message': 'Renamed', 'display_name': inst.original_name})
