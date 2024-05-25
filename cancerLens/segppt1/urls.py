"""
URL configuration for segppt1 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from appforsegppt1 import views


urlpatterns = [
    path("admin/", admin.site.urls),
    path('', views.admin_page, name='admin_page'),
    path('options_page', views.options_page, name='options_page'),
    
    path('WSI', views.WSI, name='WSI'),
    path('HandE', views.HandE, name='HandE'),
    path('IHC', views.IHC, name='IHC'),
    path('tumorMask', views.tumorMask, name='tumorMask'),
    
    path('add_WSI', views.add_WSI, name='add_WSI'),
    path('success/<int:zip_file_id>/', views.success, name='success'),
    path('delete_WSI', views.delete_WSI, name='delete_WSI'),
    path('delete_file/', views.delete_file, name='delete'),
    path('search_WSI', views.search_WSI, name='search'), 
    path('download/<str:file_name>/', views.download_file, name='download_file'),
    
    path('add_IHC', views.add_IHC, name='add_IHC'),
    path('success_IHC/<int:zip_file_id>/', views.success_IHC, name='success_IHC'),
    path('delete_IHC', views.delete_IHC, name='delete_IHC'),
    path('delete_file_IHC/', views.delete_file_IHC, name='delete_file_IHC'),
    path('search_IHC', views.search_IHC, name='search_IHC'), 
    path('download_IHC/<str:file_name>/', views.download_file_IHC, name='download_file_IHC'),
    
    
    path('add_HandE', views.add_HandE, name='add_HandE'),
    path('success_HandE/<int:zip_file_id>/', views.success_HandE, name='success_HandE'),
    path('delete_HandE', views.delete_HandE, name='delete_HandE'),
    path('delete_file_HandE/', views.delete_file_HandE, name='delete_file_HandE'),
    path('search_HandE', views.search_HandE, name='search_HandE'), 
    path('download_HandE/<str:file_name>/', views.download_file_HandE, name='download_file_HandE'),
    
    path('add_tumorMask', views.add_tumorMask, name='add_tumorMask'),
    path('success_tumorMask/<int:zip_file_id>/', views.success_tumorMask, name='success_tumorMask'),
    path('delete_tumorMask', views.delete_tumorMask, name='delete_tumorMask'),
    path('delete_file_tumorMask/', views.delete_file_tumorMask, name='delete_file_tumorMask'),
    path('search_tumorMask', views.search_tumorMask, name='search_tumorMask'), 
    path('download_tumorMask/<str:file_name>/', views.download_file_tumorMask, name='download_file_tumorMask'),
    path('generate_patches', views.generate_patches, name='generate_patches'),
    path('spatial_features', views.spatial_features, name='spatial_features'),
    path('predict_tumor', views.predict_tumor_view, name='predict_tumor'),

]

