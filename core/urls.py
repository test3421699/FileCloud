from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from converter import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.upload_file, name='upload'),
    # Changed to str to accept both strings (custom slug) and UUID formats
    path('download/<str:file_identifier>/', views.download_file, name='download'),
    # New API route for checking availability live
    path('api/check-availability/', views.check_slug_availability, name='check_availability'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
