# messenger/tasks.py
import time
from celery import shared_task

from .models import UploadedPDF

@shared_task(bind=True)
def process_pdf(self, uploaded_id):
    """
    Simulated indexing task. Replace with real ingestion later.
    """
    try:
        inst = UploadedPDF.objects.get(pk=uploaded_id)
    except UploadedPDF.DoesNotExist:
        return {'status': 'missing'}

    try:
        inst.status = UploadedPDF.STATUS_PROCESSING
        inst.save(update_fields=['status'])

        # Simulate work (replace with real extraction + embedding)
        time.sleep(5)

        inst.status = UploadedPDF.STATUS_DONE
        inst.embeddings_stored = True
        inst.save(update_fields=['status', 'embeddings_stored'])
        return {'status': 'done', 'id': uploaded_id}
    except Exception as e:
        inst.status = UploadedPDF.STATUS_FAILED
        inst.save(update_fields=['status'])
        raise
