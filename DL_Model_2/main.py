import os
import warnings
import numpy as np
import nibabel as nib
#from nonfunctional-Orientation import orientate_base_images
import ants
import math
from resampling import resample








#RESAMPLING (orienting, resampling, padding)
data_dir = os.path.join(os.path.expanduser("~"), 'Desktop', 'Radiology Internship 2024', 'python code', 'Registration_Torch_Model_Chiang', 'Training Data')

resample(data_dir,[os.path.join(data_dir, 'Base Images', f) for f in os.listdir(os.path.join(data_dir, 'Base Images')) if f.endswith(('.nii', '.nii.gz'))],[os.path.join(data_dir, 'Reference Images (w3_)', f) for f in os.listdir(os.path.join(data_dir, 'Reference Images (w3_)')) if f.endswith(('.nii', '.nii.gz'))])

