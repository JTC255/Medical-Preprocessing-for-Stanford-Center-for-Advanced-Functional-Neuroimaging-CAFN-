from flask import Flask, render_template, request, redirect, url_for, send_from_directory,flash, send_file
import os, shutil
from werkzeug.utils import secure_filename

import torch
import torch.nn as nn
import torch.nn.functional as F

import zipfile

import numpy as np
import nibabel as nib
import itk

#yongkai's stuff:
import networks
from FoundationNorm import FoundationNorm

import io
from PIL import Image

app = Flask(__name__)

app.secret_key = 'your_secret_key'

#Upload Folder:
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'


app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 1000 * 1024 * 1024  # Upload size limit: 16MB

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
image_folder = os.path.join(app.root_path, 'uploads')
shutil.rmtree(image_folder); os.makedirs(image_folder)
image_folder = os.path.join(app.root_path, 'outputs')
shutil.rmtree(image_folder); os.makedirs(image_folder)

#Initialize model:
net = networks.tallUNet2(dimension=3)
model = FoundationNorm(network=net)

if torch.cuda.device_count() > 1:
    print(f"Using {torch.cuda.device_count()} GPUs")
    model = torch.nn.DataParallel(model)

    
model = model.cuda()
model.load_state_dict(torch.load('model_checkpoint1642_epoch_85.pth'))

def subsample_tensor(tensor, num_samples=10000):
    """Subsample a large tensor to make operations like quantile computation more efficient."""
    flat_tensor = tensor.reshape(-1)
    indices = torch.randperm(flat_tensor.size(0))[:num_samples]
    return flat_tensor[indices]


def normalize_nifti(file_path):
    # Load the base image and its affine matrix
    base_img_nib = nib.as_closest_canonical(nib.load(file_path))

    # Extract the data and affine matrix
    base_image = base_img_nib.get_fdata().copy()
    base_affine = base_img_nib.affine
    print(f"image affine {base_affine}")

    # Convert to PyTorch tensor
    base_image = torch.tensor(base_image, dtype=torch.float32)
    base_shape = base_image.shape
    print(f"base shape: {base_shape}")

    # Transpose to get the shape [Depth, Height, Width]
    #no its not??
    base_image = base_image.permute(2, 0, 1)

    # Rotate the image (if required by your model's input expectations)
    base_image = base_image.rot90(k=1, dims=(1, 2))

    # Calculate min and max using subsampling for quantile normalization
    base_min = base_image.min()
    base_max = torch.quantile(subsample_tensor(base_image), 0.99)

    epsilon = 1e-5

    # Normalize the base image
    base_image = (base_image - base_min) / (base_max - base_min + epsilon)

    # Add a channel dimension to match shape [1, Depth, Height, Width]
    base_image_tensor = base_image.unsqueeze(0)

    # Define the target shape for interpolation
    target_shape = (164, 164, 164)

    # Interpolate the image to the target shape
    base_image_tensor = F.interpolate(base_image_tensor.unsqueeze(0), size=target_shape, mode='trilinear', align_corners=False).squeeze(0)

    # Perform inference using the preloaded model
    with torch.no_grad():
        base_image_tensor = base_image_tensor.unsqueeze(0).cuda()
        output,disp_vecs = model(base_image_tensor)
        

        
        disp_vecs_np = disp_vecs.cpu().numpy()
        affine = np.eye(4)
        disp_vecs_nifti = nib.Nifti1Image(disp_vecs_np, affine)
        nib.save(disp_vecs_nifti, 'disp_vecs.nii')

    # Apply the transformations to the affine matrix
    permute_affine = np.array([
        [0, 0, 1, 0],
        [1, 0, 0, 0],
        [0, 1, 0, 0],
        [0, 0, 0, 1]
    ])
    rotate_affine = np.array([
        [0, -1, 0, 0],
        [1,  0, 0, 0],
        [0,  0, 1, 0],
        [0,  0, 0, 1]
    ])
   
    
    adjusted_affine = base_affine @ permute_affine @ rotate_affine

    original_shape = base_image.shape
    scale_factors = np.array(original_shape) / np.array(target_shape)

    scale_matrix = np.diag(np.append(scale_factors, 1))

    adjusted_affine = adjusted_affine @ scale_matrix
    base_max = base_max.cpu().numpy()
    base_min = base_min.cpu().numpy()
    output_image_np = output.cpu().numpy()[0][0]
    print(base_max, base_min)
    output_image_np = output_image_np * (base_max - base_min + epsilon) + base_min

    output_nifti = nib.Nifti1Image(output_image_np, adjusted_affine)
    output_filename = file_path[8:] + ".gz"


    output_path = os.path.join(OUTPUT_FOLDER, output_filename)
    nib.save(output_nifti, output_path)
    
    # Debugging output
    print("INFO: ")
    print(f"Output path: {output_path}")
    print(f"File exists: {os.path.exists(output_path)}")
    
    return output_filename
    
#Routes:

print("test test test")
@app.route("/")
def home():
    return render_template("index.html")


    
@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/resources")
def resources():
    return render_template('resources.html')

@app.route("/model")
def model_page():
    disp_images = False
    uploaded_files = os.listdir(app.config['UPLOAD_FOLDER'])
    uploaded_files = [f for f in uploaded_files if os.path.isfile(os.path.join(app.config['UPLOAD_FOLDER'], f)) if f != ".DS_Store"]
    print(f"Length uploads: {len(uploaded_files)}")
    normalized_files = os.listdir(app.config['OUTPUT_FOLDER'])
    normalized_files = [f for f in normalized_files if os.path.isfile(os.path.join(app.config['OUTPUT_FOLDER'], f)) if f != ".DS_Store"]
    print(f"Length: {len(normalized_files)}")
    
    
    #whether to display images or not/which images to display
    show_normalized_label = False
    show_normalized = False
    
    image_folder = os.path.join(app.root_path, 'static', 'images', "model_page_slices")
    shutil.rmtree(image_folder); os.makedirs(image_folder)

    if len(normalized_files) > 0:
        show_normalized = True
    
    if show_normalized:
        show_normalized_label = True
        list_urls = []
        for i in range(len(normalized_files)):
            disp_images = True
            file_path = os.path.join(app.config['OUTPUT_FOLDER'],normalized_files[i])
            img = itk.imread(file_path)
            img_array = itk.array_view_from_image(img)

            #slice_index:
            #goes to default for now
            slice_index = int(request.args.get('slice_index', img_array.shape[2] // 2))

            # Ensure slice_index is within valid bounds
            slice_index = max(0, min(slice_index, img_array.shape[2] - 1))


            #extract slice:
            slice_2d = img_array[:,:,slice_index]

            slice_2d_normalized = 255 * (slice_2d - np.min(slice_2d)) / (np.max(slice_2d) - np.min(slice_2d))
            slice_2d_normalized = slice_2d_normalized.astype(np.uint8)

            slice_image = Image.fromarray(slice_2d_normalized)
            slice_image_rotated = slice_image.rotate(270)
            
            img_io = io.BytesIO()
            slice_image_rotated.save(img_io, 'PNG')
            img_io.seek(0)

            image_filename = "norm_slice_image_" + str(i)+ ".png"
            image_path = os.path.join(image_folder, image_filename)
            slice_image_rotated.save(image_path)

            # Generate the URL for the image to be used in the template
            slice_image_url = url_for('static', filename=f'images/model_page_slices/{image_filename}')
            list_urls.append(slice_image_url)
        return render_template('model.html', uploaded_files=uploaded_files, disp_images=disp_images, slice_image_urls=list_urls,show_normalized_label=show_normalized_label)
    elif len(uploaded_files) >0:
        list_urls = []
        for i in range(len(uploaded_files)):
            disp_images = True
            file_path = os.path.join(app.config['UPLOAD_FOLDER'],uploaded_files[i])
            img = itk.imread(file_path)
            img_array = itk.array_view_from_image(img)

            #slice_index:
            #goes to default for now
            slice_index = int(request.args.get('slice_index', img_array.shape[0] // 2))

            # Ensure slice_index is within valid bounds
            slice_index = max(0, min(slice_index, img_array.shape[0] - 1))


            #extract slice:
            slice_2d = img_array[slice_index, :,:]

            slice_2d_normalized = 255 * (slice_2d - np.min(slice_2d)) / (np.max(slice_2d) - np.min(slice_2d))
            slice_2d_normalized = slice_2d_normalized.astype(np.uint8)

            slice_image = Image.fromarray(slice_2d_normalized)
            img_io = io.BytesIO()
            slice_image.save(img_io, 'PNG')
            img_io.seek(0)

            image_filename = "slice_image_" + str(i)+ ".png"
            image_path = os.path.join(image_folder, image_filename)
            slice_image.save(image_path)

            # Generate the URL for the image to be used in the template
            slice_image_url = url_for('static', filename=f'images/model_page_slices/{image_filename}')
            list_urls.append(slice_image_url)
        return render_template('model.html', uploaded_files=uploaded_files, disp_images=disp_images, slice_image_urls=list_urls,show_normalized_label=show_normalized_label)
    return render_template('model.html', uploaded_files=uploaded_files, disp_images=disp_images,show_normalized_label=show_normalized_label)
#uploading files:

@app.route('/upload', methods=['GET','POST'])
def upload_file():
    if request.method == 'POST':
        if 'files' not in request.files:
            flash('No file part')
            print('No file part')
            return redirect(request.url)

        files = request.files.getlist('files')

        if not files or files[0].filename == '':
            flash('No selected file')
            return redirect(request.url)

        for file in files:
            if file and file.filename != '':
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        flash('Files successfully uploaded')
        return redirect(url_for('model_page'))
    else:
        # Render the upload form or show a message
        return redirect(url_for('model_page'))
    
    



    
@app.route('/reset', methods=['POST'])
def reset_uploads():
    try:
        for filename in os.listdir(app.config['UPLOAD_FOLDER']):
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            # Skip .ipynb_checkpoints and other hidden folders
            if filename.startswith('.'):
                continue
            
            print(f"Attempting to delete: {file_path}")  # Debug print
            if os.path.isfile(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        
        flash('Uploads folder cleared.')
    except Exception as e:
        flash(f'Error clearing uploads folder: {str(e)}')

    try:
        for filename in os.listdir(app.config['OUTPUT_FOLDER']):
            file_path = os.path.join(app.config['OUTPUT_FOLDER'], filename)
            # Skip .ipynb_checkpoints and other hidden folders
            if filename.startswith('.'):
                continue
            
            print(f"Attempting to delete: {file_path}")  # Debug print
            if os.path.isfile(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        
        flash('output folder cleared.')
    except Exception as e:
        flash(f'Error clearing output folder: {str(e)}')
    
    return redirect(url_for('model_page'))

@app.route('/normalize', methods=['POST'])
def normalize():
    image_folder = os.path.join(app.root_path, "outputs")
    shutil.rmtree(image_folder); os.makedirs(image_folder)
    
    uploaded_files = os.listdir(app.config['UPLOAD_FOLDER'])
    uploaded_files = [f for f in uploaded_files if os.path.isfile(os.path.join(app.config['UPLOAD_FOLDER'], f)) if f != ".DS_Store"]
     # Normalize the NIfTI file
    output_filenames = []
    for file_path in uploaded_files:
        print(f"FILE PATHS IN UPLOADED_FILES: {file_path}")
        output_filename = normalize_nifti(os.path.join(app.config['UPLOAD_FOLDER'], file_path))
        output_filenames.append(output_filename)
        # Redirect to the download URL
    return redirect(url_for('model_page'))
    


@app.route('/downloads', methods=['POST'])
def download_files():
    output_folder = app.config['OUTPUT_FOLDER']
    filenames = os.listdir(output_folder)
    
    if not filenames:
        return "No files specified", 400

    # Create an in-memory ZIP file
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_archive:
        for filename in filenames:
            file_path = os.path.join(app.root_path, 'outputs', filename)
            if os.path.exists(file_path):
                zip_archive.write(file_path, arcname=filename)
            else:
                return f"File {filename} not found", 404

    # Move back to the beginning of the BytesIO buffer
    zip_buffer.seek(0)
    
    # Send the zip file as an attachment
    return send_file(zip_buffer, mimetype='application/zip', as_attachment=True, download_name='normalized_images.zip')





if __name__ == "__main__":
    #app.run(debug=True)
    app.run(host='127.0.0.1', port=5050, debug=True)
    
    
    
#in case of access denied error:

#chrome://net-internals/#sockets
#[Flush socket pools]
#aimi2:port#
#FLASK_APP=app.py flask run --host=0.0.0.0 --port=5050
