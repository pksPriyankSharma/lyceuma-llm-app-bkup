# messenger/models.py
from django.db import models

# messenger/models.py


class UploadedPDF(models.Model):
    STATUS_UPLOADED = 'UPLOADED' # added for file handling
    STATUS_PENDING = 'PENDING'
    STATUS_PROCESSING = 'PROCESSING'
    STATUS_DONE = 'DONE'
    STATUS_FAILED = 'FAILED'
    STATUS_CHOICES = [
        (STATUS_UPLOADED, 'Uploaded'), # added for file handling
        (STATUS_PENDING, 'Pending'),
        (STATUS_PROCESSING, 'Processing'),
        (STATUS_DONE, 'Done'),
        (STATUS_FAILED, 'Failed'),
    ]

    original_name = models.CharField(max_length=1024)
    file = models.FileField(upload_to='uploads/')
    size = models.BigIntegerField()
    uploaded_at = models.DateTimeField(auto_now_add=True)
    #status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    
    # New metadata fields for processing lifecycle
    detected_at = models.DateTimeField(null=True, blank=True)           # when scanner detected the file
    processing_started_at = models.DateTimeField(null=True, blank=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    processing_attempts = models.IntegerField(default=0)
    error_message = models.TextField(null=True, blank=True)
    worker_task_id = models.CharField(max_length=255, null=True, blank=True)
    
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_UPLOADED) # changed default to UPLOADED for file handling
    embeddings_stored = models.BooleanField(default=False)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"{self.original_name} ({self.id})"

# added for document chunking and ingestion logs
class DocumentChunk(models.Model):
    """
    A piece/chunk of text derived from a PDF page or region.
    Embedding references (e.g. file path or vector id) stored here.
    """
    uploaded = models.ForeignKey(UploadedPDF, on_delete=models.CASCADE, related_name='chunks')
    chunk_id = models.CharField(max_length=256, unique=True)   # e.g. f"{uploaded.id}_p{page}_{offset}"
    text = models.TextField()
    page_no = models.IntegerField(null=True, blank=True)
    token_count = models.IntegerField(null=True, blank=True)
    # location of stored embedding; for now we can save path to .npy or later vector_id
    embedding_path = models.CharField(max_length=1024, null=True, blank=True)
    vector_id = models.CharField(max_length=256, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['chunk_id']),
            models.Index(fields=['uploaded']),
        ]

    def __str__(self):
        return f"Chunk {self.chunk_id} ({self.uploaded_id})"


class IngestionLog(models.Model):
    """
    Audit log for ingestion/processing events.
    """
    uploaded = models.ForeignKey(UploadedPDF, on_delete=models.CASCADE, related_name='ingestion_logs', null=True, blank=True)
    event_time = models.DateTimeField(auto_now_add=True)
    level = models.CharField(max_length=20, choices=[('INFO','INFO'),('ERROR','ERROR'),('DEBUG','DEBUG')], default='INFO')
    message = models.TextField()
    metadata = models.JSONField(null=True, blank=True)

    class Meta:
        ordering = ['-event_time']

    def __str__(self):
        return f"[{self.event_time}] {self.level} - {self.uploaded_id or 'N/A'}"