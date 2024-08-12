For my 2024 Summer, I began working as a technical intern learning about medical imaging and clinical radiology within Stanford's Radiological Sciences Laboratory. 
Although I had not previously coded very much since middle school, I have been tinkering with languages that I once knew very well and it has come back to me pretty quickly. 
I've been working now with numerous softwares and learned several languages including python, MATLAB, and C++ in respective order of my proficiency with each one.
This module includes many files I've worked on that I feel like I've contributed in some substantial way. 
It does not encompass all coding/debugging/studying/miscellaneous work I have done with the preproc C++ source code or other files.
Enjoy. 

DL_Model_2 -> current attempts to use pytorch, monai, and various other softwares to develop a single modality AI model for image nonrigid spatial normalization. Also includes working reorientation, resampling, and padding for preprocessing before the nn does its thing. Hope to eventually extrapolate this project into multimodality, widespread use. 

extract_forward_deformation_field.m -> This builds upon code that my postdoc extracted from the spm preproc8 model. part of what this file did was draw from results of spatial normalization to create an inverse deformation field that would be used later for various purposes. My contributions included learning where the inverse transformation occured, how the forward deformation was created initially + how its dims were changed throughout the code + revising the code to solely extract the forward field in a nifti file. 

checkTransField_2_Chiang.py -> First attempt to apply inverse def field to image. Quickly cut it to use interpolation/other methods

MISSING? -> This is python code I wrote that performs the spatial normalization that spm preproc does. However, I did not use bsplines or optimization that spm had, only mimicked it with simple algebra. The point of this exercise was to understand the math behind the classical registration and run it successfully with python

yongkai_transform_application.m -> This is code that my mentor/postdoc got that mimics

transformationFunction_1_Chiang_DONE.m -> first code I wrote, essentially uses commands from spm to create a funtion which we could use to generate reference images (w) for later analysis/use.

checkField_2_Chiang.m -> This is code I wrote to check the dimensions and provide metrics such as average/max/min size of said dimensions of base patient images. slight chat gpt influence. 

check_base_dims.m -> more detailed, python version of checking dimensions of base image and trends


