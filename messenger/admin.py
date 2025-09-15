# messenger/admin.py
from django.contrib import admin
from .models import UploadedPDF, DocumentChunk, IngestionLog # added DocumentChunk and IngestionLog 

@admin.register(UploadedPDF)
class UploadedPDFAdmin(admin.ModelAdmin):
    #list_display = ('id', 'original_name', 'size', 'status', 'embeddings_stored', 'uploaded_at')
    list_display = ('id', 'original_name', 'status', 'embeddings_stored', 'uploaded_at', 'processing_started_at', 'processed_at') # added processing timestamps
    list_filter = ('status', 'embeddings_stored')
    search_fields = ('original_name',)


# below admin registrations added for document chunking and ingestion logs  

@admin.register(DocumentChunk)
class DocumentChunkAdmin(admin.ModelAdmin):
    list_display = ('chunk_id', 'uploaded', 'page_no', 'token_count', 'created_at')
    search_fields = ('chunk_id', 'text')

# below admin registrations added for document chunking and ingestion logs
@admin.register(IngestionLog)
class IngestionLogAdmin(admin.ModelAdmin):
    list_display = ('event_time','level','uploaded')
    list_filter = ('level',)
    search_fields = ('message',)