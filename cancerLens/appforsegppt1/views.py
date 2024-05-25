import os
import shutil
import tempfile
from django.shortcuts import render,redirect,get_object_or_404
from django.contrib import messages
from .forms import LoginForm, add_WSI_Form, add_IHC_Form, add_HandE_Form, add_tumorMask_Form
from .models import UserCredentials, add_WSI_table, add_IHC_table, add_HandE_table, add_tumorMask_table
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.conf import settings
from PIL import Image, ImageTk
from pathlib import Path
import random
import csv
import cv2
import string
from django.contrib.auth.hashers import check_password
from .models import SlideImage, ImagePatch
from django.http import JsonResponse
from .config import open_slide
from openslide import open_slide
import numpy as np
import logging
import zipfile
import tempfile
from .forms import GeneratePatchesForm
from .forms import TumorPredictionForm
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import tensorflow as tf
from .forms import ImageUploadForm
from django.core.files.storage import FileSystemStorage
from .forms import ImageSelectionForm
import csv
import matplotlib.pyplot as plt
import io

logger = logging.getLogger(__name__)

model_path = os.path.join(settings.STATIC_ROOT, 'Check_points_class_weight_InceptionV3_Freeze40_UnbalData_All_layers_best_model.hdf5')
model = tf.keras.models.load_model(model_path)


folder_name_WSI ="WSI_zipfiles"
folder_name_IHC ="IHC_files"
folder_name_HandE ="HandE_files"
folder_name_tumorMask = "tumorMask_files"




def admin_page(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            try:
                user_credentials = UserCredentials.objects.get(username=username)
                if check_password(password, user_credentials.password):
                    return redirect('options_page')
                else:
                    messages.error(request, 'Invalid username or password.')
            except UserCredentials.DoesNotExist:
                messages.error(request, 'Invalid username or password.')
    else:
        form = LoginForm()
    return render(request, 'segppt1/admin_page.html', {'form': form}) 

def options_page(request):
    return render(request, 'segppt1/options_page.html')



def WSI(request):
    return render(request, 'segppt1/WSI.html')

def HandE(request):
    return render(request, 'segppt1/HandE.html')

def IHC(request):
    return render(request, 'segppt1/IHC.html')

def tumorMask(request):
    return render(request, 'segppt1/tumorMask.html')


#add, delete, search for WSI

#adding WSI:

def add_WSI(request):
    if request.method == 'POST':
        form = add_WSI_Form(request.POST, request.FILES)
        if form.is_valid():
            zip_file_instance = form.save(commit=False)
            unique_code = generate_unique_code()
            zip_file_instance.unique_code = unique_code

            uploaded_file = request.FILES.get('zip_file')
            if uploaded_file and uploaded_file.name.endswith('.zip'):
                file_name = uploaded_file.name
                folder_name = 'WSI_zipfiles'
                upload_path = os.path.join(settings.MEDIA_ROOT, folder_name, file_name)

                os.makedirs(os.path.dirname(upload_path), exist_ok=True)
                with open(upload_path, 'wb+') as destination:
                    for chunk in uploaded_file.chunks():
                        destination.write(chunk)

                zip_file_instance.zip_file = os.path.join(folder_name, file_name)
                zip_file_instance.save()

                return render(request, 'success.html', {'zip_file_instance': zip_file_instance, 'unique_code': unique_code})
            else:
                messages.error(request, 'A zip file must be uploaded.')
                return render(request, 'segppt1/add_WSI.html', {'form': form})
        else:
            messages.error(request, 'The form is not valid.')
    else:
        form = add_WSI_Form()
    return render(request, 'segppt1/add_WSI.html', {'form': form})

def generate_unique_code():
    prefix = "WSI_"
    suffix = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
    return prefix + suffix

def success(request, unique_code):
    zip_file_instance = add_WSI_table.objects.get(unique_code=unique_code)
    return render(request, 'success.html', {'zip_file_instance': zip_file_instance, 'unique_code': unique_code})

#deleting WSI:

def delete_WSI(request):
  directory_path = os.path.join(settings.MEDIA_ROOT, folder_name_WSI)
  upload_dir = directory_path
  files = os.listdir(upload_dir)
  return render(request, 'segppt1/delete_WSI.html', {'files': files})

def delete_file(request):
    if request.method == 'POST':
        file_name = request.POST.get('file_name')
        file_path = os.path.join(settings.MEDIA_ROOT, folder_name_WSI, file_name)
        if os.path.exists(file_path):
            os.remove(file_path)
            message = f"{file_name} was deleted successfully."
            try:
                uploaded_file = add_WSI_table.objects.get(zip_file=file_name)
                uploaded_file.delete()
                message = f"{file_name} was deleted successfully."
            except add_WSI_table.DoesNotExist:
                message = "Database entry not found for the file."
        else:
            message = "File not found."
        return render(request, 'segppt1/delete_file.html', {'message': message})
    else:
        return render(request, 'segppt1/delete_file.html')
    
#searching WSI:

def search_WSI(request):
    query = request.GET.get('q')
    upload_code = request.GET.get('upload_code')
    files = add_WSI_table.objects.all()

    if query:
        files = files.filter(zip_file__icontains=query)
    if upload_code:
        files = files.filter(unique_code=upload_code)
        
    for file in files:
        print(file.zip_file.name)
        
    return render(request, 'segppt1/search_WSI.html', {'files': files, 'query': query, 'upload_code': upload_code})

def download_file(request, file_name):
    file_path = os.path.join(settings.MEDIA_ROOT, folder_name_WSI, file_name)
    if os.path.exists(file_path):
        with open(file_path, 'rb') as file:
            response = HttpResponse(file.read(), content_type='application/octet-stream')
            response['Content-Disposition'] = f'attachment; filename="{file_name}"'
            return response
    else:
        return HttpResponse("File not found", status=404)
    
#add, delete, search for IHC

#adding IHC:

def add_IHC(request):
    zip_file_instance = None
    if request.method == 'POST':
        form = add_IHC_Form(request.POST, request.FILES)
        if form.is_valid():
            zip_file_instance = form.save(commit=False)
            unique_code = generate_unique_code_IHC()  # Generate unique code
            zip_file_instance.unique_code = unique_code

            # Save the file to the 'media/' directory
            file_name = form.cleaned_data['zip_file'].name
            upload_path = os.path.join(settings.MEDIA_ROOT, folder_name_IHC , file_name)

            os.makedirs(os.path.dirname(upload_path), exist_ok=True)
            with open(upload_path, 'wb+') as destination:
                for chunk in request.FILES['zip_file'].chunks():
                    destination.write(chunk)

            # Update the model instance with the file path
            zip_file_instance.zip_file = file_name
            zip_file_instance.save()

            return render(request, 'success_IHC.html', {'zip_file_instance': zip_file_instance, 'unique_code': unique_code})
    else:
        form = add_IHC_Form()
    return render(request, 'segppt1/add_IHC.html', {'form': form})

def generate_unique_code_IHC():
    prefix = "IHC_"
    suffix = ''.join(random.choices(string.ascii_letters + string.digits, k=10))  # Generate random combination
    return prefix + suffix

def success_IHC(request, unique_code):
    zip_file_instance = add_IHC_table.objects.get(unique_code=unique_code)
    return render(request, 'success_IHC.html', {'zip_file_instance': zip_file_instance, 'unique_code': unique_code})
    
#deleting_IHC:

def delete_IHC(request):
  directory_path = os.path.join(settings.MEDIA_ROOT, folder_name_IHC)
  upload_dir = directory_path
  files = os.listdir(upload_dir)
  return render(request, 'segppt1/delete_IHC.html', {'files': files})

def delete_file_IHC(request):
    if request.method == 'POST':
        file_name = request.POST.get('file_name')
        file_path = os.path.join(settings.MEDIA_ROOT, folder_name_IHC, file_name)
        if os.path.exists(file_path):
            os.remove(file_path)
            message = f"{file_name} was deleted successfully."
            try:
                uploaded_file = add_IHC_table.objects.get(zip_file=file_name)
                uploaded_file.delete()
                message = f"{file_name} was deleted successfully."
            except add_IHC_table.DoesNotExist:
                message = "Database entry not found for the file."
        else:
            message = "File not found."
        return render(request, 'segppt1/delete_file_IHC.html', {'message': message})
    else:
        return render(request, 'segppt1/delete_file_IHC.html')
    
 #Searching IHC:
     
def search_IHC(request):
    query = request.GET.get('q')
    upload_code = request.GET.get('upload_code')
    files = add_IHC_table.objects.all()

    if query:
        files = files.filter(zip_file__icontains=query)
    if upload_code:
        files = files.filter(unique_code=upload_code)
        
    for file in files:
        print(file.zip_file.name)
        
    return render(request, 'segppt1/search_IHC.html', {'files': files, 'query': query, 'upload_code': upload_code})

def download_file_IHC(request, file_name):
    file_path = os.path.join(settings.MEDIA_ROOT, folder_name_IHC, file_name)
    if os.path.exists(file_path):
        with open(file_path, 'rb') as file:
            response = HttpResponse(file.read(), content_type='application/octet-stream')
            response['Content-Disposition'] = f'attachment; filename="{file_name}"'
            return response
    else:
        return HttpResponse("File not found", status=404)

#add, delete, search H&E

#Adding H&E:
    

def add_HandE(request):
    zip_file_instance = None
    if request.method == 'POST':
        form = add_HandE_Form(request.POST, request.FILES)
        if form.is_valid():
            zip_file_instance = form.save(commit=False)
            unique_code = generate_unique_code_HandE() # Generate unique code
            zip_file_instance.unique_code = unique_code

            # Save the file to the 'media/' directory
            file_name = form.cleaned_data['zip_file'].name
            upload_path = os.path.join(settings.MEDIA_ROOT, folder_name_HandE , file_name)

            os.makedirs(os.path.dirname(upload_path), exist_ok=True)
            with open(upload_path, 'wb+') as destination:
                for chunk in request.FILES['zip_file'].chunks():
                    destination.write(chunk)

            # Update the model instance with the file path
            zip_file_instance.zip_file = file_name
            zip_file_instance.save()

            return render(request, 'success_HandE.html', {'zip_file_instance': zip_file_instance, 'unique_code': unique_code})
    else:
        form = add_HandE_Form()
    return render(request, 'segppt1/add_HandE.html', {'form': form})

def generate_unique_code_HandE():
    prefix = "HandE_"
    suffix = ''.join(random.choices(string.ascii_letters + string.digits, k=10))  # Generate random combination
    return prefix + suffix

def success_HandE(request, unique_code):
    zip_file_instance = add_HandE_table.objects.get(unique_code=unique_code)
    return render(request, 'success_HandE.html', {'zip_file_instance': zip_file_instance, 'unique_code': unique_code})

#Deleting H&E:
    
def delete_HandE(request):
  directory_path = os.path.join(settings.MEDIA_ROOT, folder_name_HandE)
  upload_dir = directory_path
  files = os.listdir(upload_dir)
  return render(request, 'segppt1/delete_HandE.html', {'files': files})

def delete_file_HandE(request):
    if request.method == 'POST':
        file_name = request.POST.get('file_name')
        file_path = os.path.join(settings.MEDIA_ROOT, folder_name_HandE, file_name)
        if os.path.exists(file_path):
            os.remove(file_path)
            message = f"{file_name} was deleted successfully."
            try:
                uploaded_file = add_HandE_table.objects.get(zip_file=file_name)
                uploaded_file.delete()
                message = f"{file_name} was deleted successfully."
            except add_HandE_table.DoesNotExist:
                message = "Database entry not found for the file."
        else:
            message = "File not found."
        return render(request, 'segppt1/delete_file_HandE.html', {'message': message})
    else:
        return render(request, 'segppt1/delete_file_HandE.html')    
    
#Searching H&E:
    
def search_HandE(request):
    query = request.GET.get('q')
    upload_code = request.GET.get('upload_code')
    files = add_HandE_table.objects.all()

    if query:
        files = files.filter(zip_file__icontains=query)
    if upload_code:
        files = files.filter(unique_code=upload_code)
        
    for file in files:
        print(file.zip_file.name)
        
    return render(request, 'segppt1/search_HandE.html', {'files': files, 'query': query, 'upload_code': upload_code})

def download_file_HandE(request, file_name):
    file_path = os.path.join(settings.MEDIA_ROOT, folder_name_HandE, file_name)
    if os.path.exists(file_path):
        with open(file_path, 'rb') as file:
            response = HttpResponse(file.read(), content_type='application/octet-stream')
            response['Content-Disposition'] = f'attachment; filename="{file_name}"'
            return response
    else:
        return HttpResponse("File not found", status=404)
    
#add, delete, search Tumor Mask

#Adding tumor mask: 

def add_tumorMask(request):
    zip_file_instance = None
    if request.method == 'POST':
        form = add_tumorMask_Form(request.POST, request.FILES)
        if form.is_valid():
            zip_file_instance = form.save(commit=False)
            unique_code = generate_unique_code_tumorMask()  # Generate unique code
            zip_file_instance.unique_code = unique_code

            # Save the file to the 'media/' directory
            file_name = form.cleaned_data['zip_file'].name
            upload_path = os.path.join(settings.MEDIA_ROOT, folder_name_tumorMask , file_name)

            os.makedirs(os.path.dirname(upload_path), exist_ok=True)
            with open(upload_path, 'wb+') as destination:
                for chunk in request.FILES['zip_file'].chunks():
                    destination.write(chunk)

            # Update the model instance with the file path
            zip_file_instance.zip_file = file_name
            zip_file_instance.save()

            return render(request, 'success_tumorMask.html', {'zip_file_instance': zip_file_instance, 'unique_code': unique_code})
    else:
        form = add_tumorMask_Form()
    return render(request, 'segppt1/add_tumorMask.html', {'form': form})

def generate_unique_code_tumorMask():
    prefix = "tumorMask_"
    suffix = ''.join(random.choices(string.ascii_letters + string.digits, k=10))  # Generate random combination
    return prefix + suffix

def success_tumorMask(request, unique_code):
    zip_file_instance = add_tumorMask_table.objects.get(unique_code=unique_code)
    return render(request, 'success_tumorMask.html', {'zip_file_instance': zip_file_instance, 'unique_code': unique_code})

#Deleting tumor mask:
    
def delete_tumorMask(request):
  directory_path = os.path.join(settings.MEDIA_ROOT, folder_name_tumorMask)
  upload_dir = directory_path
  files = os.listdir(upload_dir)
  return render(request, 'segppt1/delete_tumorMask.html', {'files': files})

def delete_file_tumorMask(request):
    if request.method == 'POST':
        file_name = request.POST.get('file_name')
        file_path = os.path.join(settings.MEDIA_ROOT, folder_name_tumorMask, file_name)
        if os.path.exists(file_path):
            os.remove(file_path)
            message = f"{file_name} was deleted successfully."
            try:
                uploaded_file = add_tumorMask_table.objects.get(zip_file=file_name)
                uploaded_file.delete()
                message = f"{file_name} was deleted successfully."
            except add_tumorMask_table.DoesNotExist:
                message = "Database entry not found for the file."
        else:
            message = "File not found."
        return render(request, 'segppt1/delete_file_tumorMask.html', {'message': message})
    else:
        return render(request, 'segppt1/delete_file_tumorMask.html')
    
#searching tumor mask:
    
def search_tumorMask(request):
    query = request.GET.get('q')
    upload_code = request.GET.get('upload_code')
    files = add_tumorMask_table.objects.all()

    if query:
        files = files.filter(zip_file__icontains=query)
    if upload_code:
        files = files.filter(unique_code=upload_code)
        
    for file in files:
        print(file.zip_file.name)
        
    return render(request, 'segppt1/search_tumorMask.html', {'files': files, 'query': query, 'upload_code': upload_code})

def download_file_tumorMask(request, file_name):
    file_path = os.path.join(settings.MEDIA_ROOT, folder_name_tumorMask, file_name)
    if os.path.exists(file_path):
        with open(file_path, 'rb') as file:
            response = HttpResponse(file.read(), content_type='application/octet-stream')
            response['Content-Disposition'] = f'attachment; filename="{file_name}"'
            return response
    else:
        return HttpResponse("File not found", status=404)

def get_img_data(f, maxsize=(350, 800)):
    """Generate image data for web usage"""
    img = Image.open(f)
    img.thumbnail(maxsize)
    img.save(f"static/{os.path.basename(f)}", format="PNG")
    return f"/static/{os.path.basename(f)}"

def read_slide(slide_path, x, y, level, width, height, as_float=False):
    slide = open_slide(slide_path)
    im = slide.read_region((x, y), level, (width, height)).convert('RGB')
    return np.asarray(im, dtype=np.float32) if as_float else np.asarray(im)


def generate_patches(request):

    directory_path = os.path.join(settings.MEDIA_ROOT, 'WSI_zipfiles')

    try:
        wsi_files = [f for f in os.listdir(directory_path) if f.lower().endswith('.zip')]
    except FileNotFoundError:
        wsi_files = []
        messages.error(request, "The WSI_zipfiles directory does not exist.")

    if request.method == 'POST':
        form = GeneratePatchesForm(request.POST)
        if form.is_valid():
            file_name = form.cleaned_data['wsi_image']
            file_path = os.path.join(directory_path, file_name)

            if file_name.lower().endswith('.zip'):
                with tempfile.TemporaryDirectory() as temp_dir:
                    try:

                        with zipfile.ZipFile(file_path, 'r') as zip_ref:
                            zip_ref.extractall(temp_dir)

                            for filename in os.listdir(temp_dir):
                                if filename.lower().endswith(('.png', '.jpeg', '.jpg', '.tif', '.tiff', '.svs')):
                                    image_path = os.path.join(temp_dir, filename)
                                    slide = open_slide(image_path)
                                    title = os.path.splitext(filename)[0]
                                    output_dir = os.path.join(settings.MEDIA_ROOT, 'patches', title)
                                    os.makedirs(output_dir, exist_ok=True)

                                    level = min(2, slide.level_count - 1)
                                    patch_size = 256
                                    dimensions = slide.level_dimensions[level]
                                    downsample = slide.level_downsamples[level]

                                    for x in range(0, dimensions[0], patch_size):
                                        for y in range(0, dimensions[1], patch_size):
                                            width = min(patch_size, dimensions[0] - x)
                                            height = min(patch_size, dimensions[1] - y)
                                            region = (int(x * downsample), int(y * downsample), int(width * downsample), int(height * downsample))
                                            patch = slide.read_region(region, level, (width, height)).convert('RGB')

                                            patch_filename = f"{title}_{x}_{y}.png"
                                            patch_path = os.path.join(output_dir, patch_filename)
                                            patch.save(patch_path, "PNG")

                                            slide_image, created = SlideImage.objects.get_or_create(
                                                title=title,
                                                defaults={'image': patch_path}
                                            )

                                            ImagePatch.objects.create(
                                                slide_image=slide_image,
                                                image_path=patch_path,
                                                has_tumor=False
                                            )
                            messages.success(request, 'Patches generated successfully.')
                    except zipfile.BadZipFile:
                        messages.error(request, "The uploaded file is not a valid ZIP file.")
                    except Exception as e:
                        messages.error(request, f"An error occurred: {e}")
            else:
                messages.error(request, "Uploaded file is not a ZIP file.")

            return redirect('generate_patches')
        else:
            messages.error(request, "There was an error with the form submission.")

    else:
        form = GeneratePatchesForm()

    return render(request, 'segppt1/generate_patches.html', {'form': form, 'wsi_files': wsi_files})


def spatial_features(request):
    ihc_directory_path = os.path.join(settings.MEDIA_ROOT, 'IHC_files')
    tumor_directory_path = os.path.join(settings.MEDIA_ROOT, 'tumorMask_files')

    ihc_files = [f for f in os.listdir(ihc_directory_path) if f.endswith('.zip')]
    tumor_mask_files = [f for f in os.listdir(tumor_directory_path) if f.endswith('.zip')]

    context = {
        'ihc_files': ihc_files,
        'tumor_mask_files': tumor_mask_files
    }

    if request.method == 'POST':
        ihc_image_name = request.POST.get('ihc_name')
        tumor_image_name = request.POST.get('tumor_name')
        ihc_type = request.POST.get('ihc_type')
        ihc_area = request.POST.get('ihc_area')
        slide_number = request.POST.get('slide_number')

        if ihc_area.startswith('>'):
            min_area = int(ihc_area[1:])
            max_area = float('inf')
        elif '-' in ihc_area:
            min_area, max_area = [int(x) for x in ihc_area.split('-')]
        else:
            min_area = max_area = int(ihc_area)

        ihc_zip_path = os.path.join(ihc_directory_path, ihc_image_name)
        tumor_zip_path = os.path.join(tumor_directory_path, tumor_image_name)
        output_path = os.path.join(settings.MEDIA_ROOT, 'spatial_features')

        os.makedirs(output_path, exist_ok=True)

        with tempfile.TemporaryDirectory() as temp_dir:
            with zipfile.ZipFile(ihc_zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
            with zipfile.ZipFile(tumor_zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)

            extracted_files = os.listdir(temp_dir)
            ihc_image_files = [f for f in extracted_files if f.lower().endswith(('.png', '.jpg', '.jpeg')) and ihc_type.lower() in f.lower()]
            tumor_image_files = [f for f in extracted_files if f.lower().endswith(('.png', '.jpg', '.jpeg')) and 'mask' in f.lower()]

            if not ihc_image_files or not tumor_image_files:
                messages.error(request, "The required IHC or tumor mask image file was not found in the zip.")
                return render(request, 'segppt1/spatial_features.html', context)

            ihc_image_full_path = os.path.join(temp_dir, ihc_image_files[0])
            tumor_image_full_path = os.path.join(temp_dir, tumor_image_files[0])

            ihc_img = cv2.imread(ihc_image_full_path)
            tumor_img = cv2.imread(tumor_image_full_path, cv2.IMREAD_GRAYSCALE)

            if ihc_img is None or tumor_img is None:
                messages.error(request, "One of the images could not be read.")
                return render(request, 'segppt1/spatial_features.html', context)
            contours, _ = cv2.findContours(tumor_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            if not contours:
                messages.error(request, "No contours were detected in the tumor mask image.")
                return render(request, 'segppt1/spatial_features.html', context)

            annotated_image = ihc_img.copy()
            spatial_features_list = []

            for contour in contours:
                area = cv2.contourArea(contour)
                if min_area <= area <= max_area:
                    M = cv2.moments(contour)
                    cx = int(M['m10'] / M['m00']) if M['m00'] != 0 else 0
                    cy = int(M['m01'] / M['m00']) if M['m00'] != 0 else 0
                    spatial_features_list.append([cx, cy, area])
                    cv2.drawContours(annotated_image, [contour], -1, (0, 255, 0), 8)
                else:
                    print(f"Contour with area {area} excluded from range {min_area}-{max_area}")

            if not spatial_features_list:
                print(f"No contours within the specified area range {min_area}-{max_area} were found.")
                messages.error(request, "No spatial features within the area range were detected.")
                return render(request, 'segppt1/spatial_features.html', context)

            annotated_image_path = os.path.join(output_path, f"Annotated_{slide_number}.png")
            cv2.imwrite(annotated_image_path, annotated_image)

            csv_file_path = os.path.join(output_path, f"SpatialFeatures_{slide_number}.csv")
            with open(csv_file_path, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Center X', 'Center Y', 'Area'])
                writer.writerows(spatial_features_list)

            messages.success(request, "Spatial features generated successfully.")

    return render(request, 'segppt1/spatial_features.html', context)


def predict_tumor_view(request):
    if request.method == 'POST':
        form = TumorPredictionForm(request.POST)
        if form.is_valid():

            testing_patches_path = str(
                os.path.join(settings.MEDIA_ROOT, 'patches', form.cleaned_data['testing_patches_path']))

            model_path = os.path.join(settings.STATIC_ROOT, 'Check_points_class_weight_InceptionV3_Freeze40_UnbalData_All_layers_best_model.hdf5')
            model = tf.keras.models.load_model(model_path)
            output_directory = os.path.join(settings.MEDIA_ROOT, 'tumor_detection_outcome')
            os.makedirs(output_directory, exist_ok=True)

            images = []
            target_size = (256, 256)
            for filename in os.listdir(testing_patches_path):
                if filename.endswith(".png"):
                    img_path = os.path.join(testing_patches_path, filename)
                    image = Image.open(img_path).convert('RGB')
                    image = image.resize(target_size)
                    images.append(np.array(image) / 255.0)

            images = np.array(images)
            if images.size == 0:
                message = "No images found in the directory for generating predictions."
                return render(request, 'segppt1/predict_tumor.html', {'form': form, 'message': message})

            predictions = model.predict(images)
            predicted_classes = np.argmax(predictions, axis=1)
            unique_document_name = os.path.basename(testing_patches_path).replace(" ", "_")
            result_file_name = f"{unique_document_name}_predictions.txt"
            result_file_path = os.path.join(output_directory, result_file_name)

            with open(result_file_path, 'w') as file:
                for filename, pred_class in zip(os.listdir(testing_patches_path), predicted_classes):
                    file.write(f"{filename}: Class {pred_class}\n")

            message = "Predictions computed successfully!"
            return render(request, 'segppt1/predict_tumor.html', {'form': form, 'message': message})
    else:
        form = TumorPredictionForm()

    return render(request, 'segppt1/predict_tumor.html', {'form': form})