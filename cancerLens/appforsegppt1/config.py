import os
import ctypes

dll_path = r'C:\openslide-x64\bin\libopenslide-0.dll'

if not os.path.exists(dll_path):
    raise FileNotFoundError(f"The specified 'libopenslide-0.dll' was not found in path: {dll_path}")

libopenslide = ctypes.cdll.LoadLibrary(dll_path)

os.environ['PATH'] = r'C:\openslide-x64\bin;' + os.environ['PATH']

from openslide import open_slide, __library_version__ as openslide_version

print(f"OpenSlide version loaded: {openslide_version}")