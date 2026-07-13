import uuid
from django.db import models

class UploadedFile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # New field: unique custom name, blank and null allowed for default auto-generation
    custom_slug = models.SlugField(max_length=50, unique=True, blank=True, null=True)
    file = models.FileField(upload_to='uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.file.name.split('/')[-1]}"
