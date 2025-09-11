# messenger/admin.py
from django.contrib import admin
from .models import UploadedPDF

@admin.register(UploadedPDF)
class UploadedPDFAdmin(admin.ModelAdmin):
    list_display = ('id', 'original_name', 'size', 'status', 'embeddings_stored', 'uploaded_at')
    list_filter = ('status', 'embeddings_stored')
    search_fields = ('original_name',)
