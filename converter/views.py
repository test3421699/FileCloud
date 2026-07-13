import re
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404, JsonResponse
from django.db.models import Q
from .models import UploadedFile

def upload_file(request):
    link = None
    error = None
    
    if request.method == 'POST' and request.FILES.get('myfile'):
        custom_name = request.POST.get('custom_name', '').strip().lower()
        
        # Clean the input to match standard slug rules (letters, numbers, hyphens)
        custom_name = re.sub(r'[^a-z0-9-_]', '', custom_name)
        
        if custom_name:
            # Server-side validation check to ensure safety
            if UploadedFile.objects.filter(custom_slug=custom_name).exists():
                error = "That link name is already taken!"
            else:
                uploaded = UploadedFile.objects.create(
                    file=request.FILES['myfile'], 
                    custom_slug=custom_name
                )
                link = request.build_absolute_uri(f'/download/{uploaded.custom_slug}/')
        else:
            # Default auto-generation behavior if field is left blank
            uploaded = UploadedFile.objects.create(file=request.FILES['myfile'])
            link = request.build_absolute_uri(f'/download/{uploaded.id}/')
            
    return render(request, 'converter/index.html', {'link': link, 'error': error})

def download_file(request, file_identifier):
    # Lookup file checking both the UUID field and the custom slug field
    uploaded_file = get_object_or_404(
        UploadedFile, 
        Q(id=file_identifier) | Q(custom_slug=file_identifier)
    )
    try:
        response = HttpResponse(uploaded_file.file, content_type='application/octet-stream')
        response['Content-Disposition'] = f'attachment; filename="{uploaded_file.file.name.split("/")[-1]}"'
        return response
    except FileNotFoundError:
        raise Http404("Requested file does not exist.")

def check_slug_availability(request):
    """API endpoint for live checking via JavaScript"""
    slug = request.GET.get('slug', '').strip().lower()
    slug = re.sub(r'[^a-z0-9-_]', '', slug)
    
    if not slug:
        return JsonResponse({'available': False, 'message': ''})
        
    exists = UploadedFile.objects.filter(custom_slug=slug).exists()
    return JsonResponse({'available': not exists})
