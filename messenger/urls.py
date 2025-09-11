# messenger/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('api/send-text/', views.receive_text, name='receive_text'),
    path('api/upload-pdf/', views.upload_pdf, name='upload_pdf'),
    path('api/list-uploads/', views.list_uploads, name='list_uploads'),
    path('api/file/<int:pk>/details/', views.file_details, name='file_details'),
    path('api/file/<int:pk>/delete/', views.file_delete, name='file_delete'),
    path('api/file/<int:pk>/rename/', views.file_rename, name='file_rename'),
]
