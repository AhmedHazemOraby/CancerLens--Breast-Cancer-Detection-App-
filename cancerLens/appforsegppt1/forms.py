from django import forms
from .models import UserCredentials, add_WSI_table, add_IHC_table, add_HandE_table, add_tumorMask_table
import os
from django.conf import settings

class LoginForm(forms.ModelForm):
    class Meta:
        model = UserCredentials
        fields = ['username', 'password']


class add_WSI_Form(forms.ModelForm):
    class Meta:
        model = add_WSI_table
        fields = ['slide_name', 'slide_number', 'magnification_level', 'zip_file']
        
        
class add_IHC_Form(forms.ModelForm):
    class Meta:
        model = add_IHC_table
        fields = ['image_name', 'stain_type_IHC', 'zip_file']

class add_HandE_Form(forms.ModelForm):
    class Meta:
        model = add_HandE_table
        fields = ['image_name',  'zip_file']
        
class add_tumorMask_Form(forms.ModelForm):
    class Meta:
        model = add_tumorMask_table
        fields = ['mask_name', 'corres_slide_name', 'corres_slide_number', 'zip_file']

class GeneratePatchesForm(forms.Form):
    wsi_image = forms.ChoiceField(choices=[])

    def __init__(self, *args, **kwargs):
        super(GeneratePatchesForm, self).__init__(*args, **kwargs)
        directory_path = os.path.join(settings.MEDIA_ROOT, 'WSI_zipfiles')
        if os.path.exists(directory_path):
            self.fields['wsi_image'].choices = [
                (f, f) for f in os.listdir(directory_path) if f.lower().endswith('.zip')
            ]

class ImageUploadForm(forms.Form):
    ihc_image = forms.ImageField(label='IHC mask image')
    tumor_image = forms.ImageField(label='Tumor mask image')
    ihc_type = forms.ChoiceField(choices=[('CD3', 'CD3'), ('CD4', 'CD4'), ('CD8', 'CD8'), ('PDL', 'PDL')])
    ihc_area = forms.CharField()
    slide_number = forms.CharField()

class ImageSelectionForm(forms.Form):
    ihc_image = forms.ChoiceField(label='IHC Mask Image')
    tumor_image = forms.ChoiceField(label='Tumor Mask Image')
    ihc_type = forms.ChoiceField(label='IHC Type', choices=[('CD3', 'CD3'), ('CD4', 'CD4'), ('CD8', 'CD8'), ('PDL', 'PDL')])
    slide_number = forms.CharField(label='Slide Number')
    min_area = forms.IntegerField(label='Minimum Area')
    max_area = forms.IntegerField(label='Maximum Area')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['ihc_image'].choices = self.get_files('IHC_files')
        self.fields['tumor_image'].choices = self.get_files('tumorMask_files')

    def get_files(self, directory):
        path = os.path.join(settings.MEDIA_ROOT, directory)
        if os.path.exists(path):
            files = [(f, f) for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
            return files
        return []

from django import forms

class TumorPredictionForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(TumorPredictionForm, self).__init__(*args, **kwargs)
        patches_path = os.path.join(settings.MEDIA_ROOT, 'patches')
        if os.path.exists(patches_path):
            choices = [(d, d) for d in os.listdir(patches_path) if os.path.isdir(os.path.join(patches_path, d))]
        else:
            choices = []
        self.fields['testing_patches_path'] = forms.ChoiceField(choices=choices, label="Testing Patches Path")

    slide_number = forms.CharField(label='Slide Number', max_length=50)
    magnification_level = forms.IntegerField(label='Magnification Level')