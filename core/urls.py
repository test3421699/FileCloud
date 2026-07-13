from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from converter import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.upload_file, name='upload'),
    path('download/<uuid:file_id>/', views.download_file, name='download'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
