from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404
from .models import UploadedFile

def upload_file(request):
    link = None
    if request.method == 'POST' and request.FILES.get('myfile'):
        # Save file directly via model instantiation
        uploaded = UploadedFile.objects.create(file=request.FILES['myfile'])
        # Form absolute dynamic URI link string
        link = request.build_absolute_uri(f'/download/{uploaded.id}/')
        
    return render(request, 'converter/index.html', {'link': link})

def download_file(request, file_id):
    uploaded_file = get_object_or_404(UploadedFile, id=file_id)
    try:
        response = HttpResponse(uploaded_file.file, content_type='application/octet-stream')
        # Instruct browser to download file instead of rendering it inline
        response['Content-Disposition'] = f'attachment; filename="{uploaded_file.file.name.split("/")[-1]}"'
        return response
    except FileNotFoundError:
        raise Http404("Requested file does not exist on server.")
