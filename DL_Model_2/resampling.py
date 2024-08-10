import os
import warnings
import numpy as np
import nibabel as nib
#from nonfunctional-Orientation import orientate_base_images
import ants
import math




#FUNCTIONS
def find_target_spacing(reference_image_paths):
    nifti_file = nib.load(reference_image_paths[0])
    affine = nifti_file.affine
    voxel_sizes = np.sqrt(np.sum(affine[:3, :3] ** 2, axis=0))
    return(voxel_sizes)

def original_spacing(base_image_paths):
    nifti_file = nib.load(base_image_paths[0])
    affine = nifti_file.affine
    voxel_sizes = np.sqrt(np.sum(affine[:3, :3] ** 2, axis=0))
    return(voxel_sizes)

def find_orientation(reference_image_paths):
    nifti_file = nib.load(reference_image_paths[0])
    affine = nifti_file.affine
    orientation = nib.aff2axcodes(affine)
    return(orientation)

#cropping functions:
def find_bounding_box(images):
    """
    Find the bounding box that encompasses all non-zero elements across all images.
    """
    global_min = np.array([np.inf, np.inf, np.inf])
    global_max = np.array([-np.inf, -np.inf, -np.inf])
    
    for img in images:
        img_data = img.numpy()
        non_zero_coords = np.argwhere(img_data != 0)
        min_coords = non_zero_coords.min(axis=0)
        max_coords = non_zero_coords.max(axis=0)
        
        global_min = np.minimum(global_min, min_coords)
        global_max = np.maximum(global_max, max_coords)
    
    return global_min, global_max

def pad_and_crop_images(images, bounding_box_min, bounding_box_max):
    cropped_images = []
    for img in images:
        pad_dims = bounding_box_max.copy()
       
        for i in range(len(bounding_box_max)):
            pad_dims[i] = math.floor((bounding_box_max[i]+10)/10)*10
        img_shape = img.shape  # Shape should be (x_dim, y_dim, z_dim)
        padded_array = [((pad_dims[0]-img.shape[0])/2,(pad_dims[0]-img.shape[0])/2),((pad_dims[1]-img.shape[1])/2,(pad_dims[1]-img.shape[1])/2),((pad_dims[2]-img.shape[2])/2,(pad_dims[2]-img.shape[2])/2)]
        
        unfloored_padded_array = [(p[0], p[1]) for p in padded_array]
        padded_array = [(int(p[0]), int(p[1])) for p in padded_array]
        padded_array = [list(p) for p in padded_array]
        for i in range(len(padded_array)):
            if unfloored_padded_array[i][0] - int(unfloored_padded_array[i][0]) != 0:
                padded_array[i][0] += 1
                print(padded_array[i])
                #EXTRA SLICE ADDED TO LEFT/SMALLER SIDE IN CASE OF MISSING SLICE DUE TO ROUNDING
            
        
        padded_img = ants.pad_image(img, pad_width=padded_array)
        
        cropped_images.append(padded_img)
    return cropped_images



def save_images(images, paths):
    """
    Save all cropped images.
    """
    for img, path in zip(images, paths):
        ants.image_write(img, path)
        print(f"Saved cropped image to {path}")


# Define paths

def resample(data_dir,base_image_paths,reference_image_paths):

    target_spacing = find_target_spacing(reference_image_paths)
    target_orientation = find_orientation(reference_image_paths)
    target_orientation = ''.join(target_orientation)
    base_orientation = find_orientation(base_image_paths)
    base_spacing = original_spacing(base_image_paths)

    #TEMPLATE/TPM
    tpm_img = ants.image_read('/Users/theochiang/Documents/MATLAB/spm-main/tpm/TPM.nii', reorient=target_orientation)


    full_file_names = []
    resampled_images = []
    for i in range(len(base_image_paths)):
        file_name = os.path.basename(base_image_paths[i])
        base_img = ants.image_read(base_image_paths[i], reorient=target_orientation)
        resampled_image = ants.resample_image(base_img, target_spacing, False, 0)
        fullname = os.path.join(data_dir, 'Resampled Images', "R_" + str(file_name))



        resampled_images.append(resampled_image)
        full_file_names.append(fullname)
        #ants.image_write(resampled_image, fullname)

    global_min, global_max = find_bounding_box(resampled_images)

    print('global min and max:')
    print(global_min,global_max)
    cropped_images = pad_and_crop_images(resampled_images, global_min, global_max)
    save_images(cropped_images, full_file_names)

    # Print out information about the original and resampled images
    print(f"Original image shape: {base_img.shape}, spacing: {base_img.spacing}")
    print(f"Resampled image shape: {resampled_image.shape}, spacing: {resampled_image.spacing}")
    
    
    
    
#run
#data_dir = os.path.join(os.path.expanduser("~"), 'Desktop', 'Radiology Internship 2024', 'python code', #'Registration_Torch_Model_Chiang', 'Training Data')
#resample(data_dir,[os.path.join(data_dir, 'Base Images', f) for f in os.listdir(os.path.join(data_dir, 'Base Images')) if f.endswith(('.nii', '.nii.gz'))],[os.path.join(data_dir, 'Reference Images (w3_)', f) for f in os.listdir(os.path.join(data_dir, 'Reference Images (w3_)')) if f.endswith(('.nii', '.nii.gz'))])

