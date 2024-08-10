"""
This script assumes that you already have the tarnsformed w- images and are now using y- images to apply to
original images to create new images which you then check against the w- images.

"""
import os
import nibabel as nib
import numpy as np
import SimpleITK as sitk
import pydicom as pydicom


# Load the base image (no prefix):
base_image_path = "/Users/theochiang/Desktop/Radiology Internship 2024/Archive - Files/UCLA-321/201506251138-MR/FLAIR<=T2_Flair_Axial_p2_5.nii"
base_image = nib.load(base_image_path)
#retrieves voxel data (y):
base_data = base_image.get_fdata()
#we go ahead and convert base, trans, and test into itk just for intuition/testing
base_image_sitk = sitk.GetImageFromArray(base_data)

#Load Transformation Field:
transformation_field_path = "/Users/theochiang/Desktop/Radiology Internship 2024/Archive - Files/UCLA-321/201506251138-MR/y_FLAIR<=T2_Flair_Axial_p2_5.nii"
transformation_field_image = nib.load(transformation_field_path)
transformation_field_data = transformation_field_image.get_fdata()

transformation_field_image_sitk = sitk.GetImageFromArray(transformation_field_data)

#Load Test Image (w):
test_image_path = "/Users/theochiang/Desktop/Radiology Internship 2024/Archive - Files/UCLA-321/201506251138-MR/w3FLAIR<=T2_Flair_Axial_p2_5.nii"
test_image = nib.load(test_image_path)
test_data = test_image.get_fdata()

test_image_sitk = sitk.GetImageFromArray(test_data)

#check dims
#"""
#check shape and dim
"""
print('base:')
print(f'num dimensions: {base_data.ndim}')
print(f'shape: {base_data.shape}')
print(f'dtype: {base_data.dtype}')
print(f'size: {base_data.size}')
print('\n')
print('trans field:')
print(f'num dimensions: {transformation_field_data.ndim}')
print(f'shape: {transformation_field_data.shape}')
print(f'dtype: {transformation_field_data.dtype}')
print(f'size: {transformation_field_data.size}')
print('\n')
print('test image:')
print(f'num dimensions: {test_data.ndim}')
print(f'shape: {test_data.shape}')
print(f'dtype: {test_data.dtype}')
print(f'size: {test_data.size}')
"""



# Assuming trans_field is a 5D numpy array of shape (121, 145, 121, 1, 3)
# We'll reshape it to a (121, 145, 121, 3) array for easier handling

#print(transformation_field_data[50])
transformation_field_data = transformation_field_data.reshape((121, 145, 121, 3))

displacement_field = sitk.GetImageFromArray(transformation_field_data.astype(np.float64), isVector=True)

#set displacement field direction, origin and spacing to match base image?

displacement_field.SetDirection(base_image_sitk.GetDirection())
displacement_field.SetOrigin(base_image_sitk.GetOrigin())
displacement_field.SetSpacing(base_image_sitk.GetSpacing())

#Initialize ResampleImageFilter
resampler = sitk.ResampleImageFilter()

#Trying to do custom reference image to get new dimensions of test image
size = [79,95,79]
spacing = [1.0,1.0,1.0]
origin = [0.0,0.0,0.0]
direction = [1.0,0.0,0.0,0.0,1.0,0.0,0.0,0.0,1.0]

custom_image = sitk.Image(size,sitk.sitkFloat64)

custom_image.SetSpacing(spacing)
custom_image.SetOrigin(origin)
custom_image.SetDirection(direction)

#Set resampler parameters
resampler.SetReferenceImage(custom_image)
resampler.SetInterpolator(sitk.sitkLinear) #trilinear interpolation
resampler.SetDefaultPixelValue(0)

#Use displacement field as transform
displacement_transform = sitk.DisplacementFieldTransform(displacement_field)
resampler.SetTransform(displacement_transform)

#Apply transformation to base image
transformed_image = resampler.Execute(base_image_sitk)

transformed_image_data = sitk.GetArrayFromImage(transformed_image)

#check shape and stuff:
print('\ntransformed image data')
print(f'num dimensions: {transformed_image_data.ndim}')
print(f'shape: {transformed_image_data.shape}')
print(f'dtype: {transformed_image_data.dtype}')
print(f'size: {transformed_image_data.size}')

print(base_image.affine)
print(test_image.affine)
resampled_image = nib.Nifti1Image(transformed_image_data, transformation_field_image.affine)

filename = 'transformed_FLAIR<=T2_Flair_Axial_p2_5.nii'
output_dir = '/Users/theochiang/Desktop/Radiology Internship 2024/python code/TransformationFieldApplication-2/'
output_path = os.path.join(output_dir,filename)

nib.save(resampled_image,output_path)

print(f"Transformed image saved to {output_path}")

#code from attempt 1
"""
resampler = sitk.ResampleImageFilter() #interpolate image data to fit new coord system?
resampler.SetReferenceImage(base_sitk_image) #to do trans on
resampler.SetTransformation(displacement_field) #setting tarnsformation field
resampled_sitk_image = resampler.Execute(base_sitk_image) #actually doing it

resampled_data = sitk.GetArrayFromImage(resampled_sitk_image)
resampled_image = nib.Nifti1Image(resampled_data, base_image.affine)

output_path = '/Users/theochiang/Desktop/Radiology Internship 2024/python code/TransformationFieldApplication-2/'
nib.save(resampled_image,output_path)

print(f"Transformed image saved to {output_path}")


print(test_image_sitk.GetOrigin())
print(test_image_sitk.GetSpacing())
print(test_image_sitk.GetDirection())
print(test_image_sitk.GetSize())


"""