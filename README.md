# CancerLens--Breast-Cancer-Detection-App-
This is a read me file for the Breast Cancer tissue analysis web application by Group L for SEGP. 

The project uses a django framework, with PostgreSQL as its main database and also employs a file system for easy access to files.

->The following are the libraries that must be installed for the application: 

psycopg2 
os
shutil
random
csv
cv2
string
numpy
logging
zipfile
tempfile
tensorflow
matplotlib.pyplot
io
openslide
string
opencv
django


****Note: 
- We encountered an error 'error: libopenslide-0.dll was not found' and so we fixed it by importing the path of the dll file itself, alongside the library in the config.py file.
(Reference from 'config.py' under appforsegppt1)

- We tried creating serveal environments, deleting and reinstalling libraries but nothing else worked and therefore we resorted to the solution mentioned above.
