import re
import uuid
from datetime import timedelta
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404, JsonResponse
from django.db.models import Q
from django.utils import timezone
from .models import UploadedFile

def upload_file(request):
    link = None
    error = None
    uploaded = None
    
    if request.method == 'POST' and request.FILES.get('myfile'):
        custom_name = request.POST.get('custom_name', '').strip().lower()
        expiry_days = request.POST.get('expiry', '1')
        
        # Calculate exactly when this file lifecycle ends
        now = timezone.now()
        if expiry_days == '30':
            expires_at = now + timedelta(days=30)
        else:
            expires_at = now + timedelta(days=int(expiry_days))
            
        # Clean custom string to follow safe URI slug patterns
        custom_name = re.sub(r'[^a-z0-9-_]', '', custom_name)
        
        if custom_name:
            # Prevent users from overwriting someone else's custom path
            if UploadedFile.objects.filter(custom_slug=custom_name).exists():
                error = "That link name is already taken!"
            else:
                uploaded = UploadedFile.objects.create(
                    file=request.FILES['myfile'], 
                    custom_slug=custom_name,
                    expires_at=expires_at
                )
                link = request.build_absolute_uri(f'/download/{uploaded.custom_slug}/')
        else:
            # No custom backhalf requested; build standard randomized UUID path
            uploaded = UploadedFile.objects.create(
                file=request.FILES['myfile'],
                expires_at=expires_at
            )
            link = request.build_absolute_uri(f'/download/{uploaded.id}/')
            
    return render(request, 'converter/index.html', {
        'link': link, 
        'error': error,
        'expires_at_iso': uploaded.expires_at.isoformat() if uploaded else None
    })

def download_file(request, file_identifier):
    # Determine if the identifier is a valid UUID string to prevent database crashes
    is_valid_uuid = False
    try:
        uuid.UUID(file_identifier)
        is_valid_uuid = True
    except ValueError:
        is_valid_uuid = False

    # Query carefully based on the format format to protect UUIDField lookups
    if is_valid_uuid:
        uploaded_file = get_object_or_404(
            UploadedFile, 
            Q(id=file_identifier) | Q(custom_slug=file_identifier)
        )
    else:
        uploaded_file = get_object_or_404(UploadedFile, custom_slug=file_identifier)
    
    # Enforce file age restriction right at download view execution
    if timezone.now() > uploaded_file.expires_at:
        if uploaded_file.file:
            uploaded_file.file.delete(save=False)
        uploaded_file.delete()
        raise Http404("This link has expired and the file was removed.")
        
    try:
        # Deliver generic byte stream directly forcing an attachment download
        response = HttpResponse(uploaded_file.file, content_type='application/octet-stream')
        response['Content-Disposition'] = f'attachment; filename="{uploaded_file.file.name.split("/")[-1]}"'
        return response
    except FileNotFoundError:
        raise Http404("Requested file does not exist.")

def check_slug_availability(request):
    """API endpoint providing asynchronous live verification validation"""
    slug = request.GET.get('slug', '').strip().lower()
    slug = re.sub(r'[^a-z0-9-_]', '', slug)
    
    if not slug:
        return JsonResponse({'available': False})
        
    exists = UploadedFile.objects.filter(custom_slug=slug).exists()
    return JsonResponse({'available': not exists})
