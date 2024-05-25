from django.db import models
from django.utils import timezone

class UserCredentials(models.Model):
    username = models.CharField(max_length=500)
    password = models.CharField(max_length=500)

    def __str__(self):
        return self.username


class add_WSI_table(models.Model):
    slide_name = models.CharField(max_length=250)
    slide_number = models.CharField(max_length=250)
    magnification_level = models.CharField(max_length=250)
    zip_file = models.FileField(upload_to='WSI_zipfiles/')
    uploaded_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.zip_file.name
    
class add_IHC_table(models.Model):
    image_name = models.CharField(max_length=250)
    stain_type_IHC = models.CharField(max_length=250)
    zip_file = models.FileField(upload_to='IHC_files/')
    uploaded_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.zip_file.name

class add_HandE_table(models.Model):
    image_name = models.CharField(max_length=250)
    zip_file = models.FileField(upload_to='HandE_files/')
    uploaded_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.zip_file.name

class add_tumorMask_table(models.Model):
    mask_name = models.CharField(max_length=250)
    corres_slide_name = models.CharField(max_length=250)
    corres_slide_number = models.CharField(max_length=250)
    zip_file = models.FileField(upload_to='tumorMask_files/')
    uploaded_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.zip_file.name

class SlideImage(models.Model):
    title = models.CharField(max_length=500, help_text="A descriptive title for the slide.")
    image = models.ImageField(upload_to='slide_images/', null=True, help_text="The slide image file.")
    slide_number = models.CharField(max_length=500, blank=True, help_text="An optional identifier or number associated with the slide.")
    description = models.TextField(blank=True, help_text="A detailed description of the slide.")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    filename = models.CharField(max_length=500, blank=True, null=True)

    def __str__(self):
        return f"{self.title} (Slide Number: {self.slide_number})"

    def save(self, *args, **kwargs):
        if self.image:
            self.filename = self.image.name
        super().save(*args, **kwargs)

class ImagePatch(models.Model):
    slide_image = models.ForeignKey('SlideImage', on_delete=models.CASCADE, related_name='patches')
    image_path = models.CharField(max_length=500)
    has_tumor = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Patch from {self.slide_image.title} - Tumor Present: {'Yes' if self.has_tumor else 'No'}"