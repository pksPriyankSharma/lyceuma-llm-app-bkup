# messenger/models.py
from django.db import models

class UploadedPDF(models.Model):
    STATUS_PENDING = 'PENDING'
    STATUS_PROCESSING = 'PROCESSING'
    STATUS_DONE = 'DONE'
    STATUS_FAILED = 'FAILED'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_PROCESSING, 'Processing'),
        (STATUS_DONE, 'Done'),
        (STATUS_FAILED, 'Failed'),
    ]

    original_name = models.CharField(max_length=1024)
    file = models.FileField(upload_to='uploads/')
    size = models.BigIntegerField()
    uploaded_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    embeddings_stored = models.BooleanField(default=False)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"{self.original_name} ({self.id})"
