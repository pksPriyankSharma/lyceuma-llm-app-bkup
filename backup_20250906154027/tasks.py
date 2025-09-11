# messenger/tasks.py
import time
from celery import shared_task
from django.conf import settings

from .models import UploadedPDF

@shared_task(bind=True)
def process_pdf(self, uploaded_id):
    """
    Simulated indexing task for the uploaded PDF.
    Replace the body with your actual ingestion/chunk + embedding logic.
    """
    try:
        inst = UploadedPDF.objects.get(pk=uploaded_id)
    except UploadedPDF.DoesNotExist:
        return {'status': 'missing'}

    try:
        inst.status = UploadedPDF.STATUS_PROCESSING
        inst.save(update_fields=['status'])

        # Simulate some work — replace with real ingestion (OCR, chunking, embeddings)
        # Example: split into pages, embed, store into DB or vector store.
        # For PoC we simulate with sleep and then mark embeddings_stored True.
        time.sleep(5)  # simulate CPU / I/O work

        # Simulated successful result:
        inst.status = UploadedPDF.STATUS_DONE
        inst.embeddings_stored = True
        inst.save(update_fields=['status', 'embeddings_stored'])

        return {'status': 'done', 'id': uploaded_id}
    except Exception as e:
        inst.status = UploadedPDF.STATUS_FAILED
        inst.save(update_fields=['status'])
        raise

