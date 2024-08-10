% Set the directory containing the .nii files
nii_dir = '/Users/theochiang/Desktop/Radiology Internship 2024/python code/Registration_Torch_Model_Chiang/Training Data/Base Images';


% Get a list of all .nii files in the directory
nii_files = dir(fullfile(nii_dir, '*.nii'));

% Initialize a table to store the dimensions
nii_dimensions = table('Size', [length(nii_files), 4], ...
                       'VariableTypes', {'string', 'double', 'double', 'double'}, ...
                       'VariableNames', {'Filename', 'Dim1', 'Dim2', 'Dim3'});

% Loop through each file and capture the dimensions
for i = 1:length(nii_files)
    % Get the full file path
    nii_file_path = fullfile(nii_dir, nii_files(i).name);
    
    % Load the NIfTI file
    nii = load_nii(nii_file_path);
    
    % Get the dimensions of the NIfTI file
    dims = size(nii.img);
    
    % Store the filename and dimensions in the table
    nii_dimensions.Filename(i) = string(nii_files(i).name);
    nii_dimensions.Dim1(i) = dims(1);
    nii_dimensions.Dim2(i) = dims(2);
    nii_dimensions.Dim3(i) = dims(3);
end

% Display the dimensions
disp(nii_dimensions);

% Calculate max values for each dimension
max_dim1 = max(nii_dimensions.Dim1);
max_dim2 = max(nii_dimensions.Dim2);
max_dim3 = max(nii_dimensions.Dim3);

% Calculate min values for each dimension
min_dim1 = min(nii_dimensions.Dim1);
min_dim2 = min(nii_dimensions.Dim2);
min_dim3 = min(nii_dimensions.Dim3);

% Calculate mean values for each dimension
mean_dim1 = mean(nii_dimensions.Dim1);
mean_dim2 = mean(nii_dimensions.Dim2);
mean_dim3 = mean(nii_dimensions.Dim3);

% Print max values
fprintf('Max Dimension X: %d\n', max_dim1);
fprintf('Max Dimension Y: %d\n', max_dim2);
fprintf('Max Dimension Z: %d\n', max_dim3);

% Print min values
fprintf('Min Dimension X: %.2f\n', min_dim1);
fprintf('Min Dimension Y: %.2f\n', min_dim2);
fprintf('Min Dimension Z: %.2f\n', min_dim3);

% Print mean values
fprintf('Mean Dimension X: %.2f\n', mean_dim1);
fprintf('Mean Dimension Y: %.2f\n', mean_dim2);
fprintf('Mean Dimension Z: %.2f\n', mean_dim3);

% Save the dimensions to a CSV file
writetable(nii_dimensions, 'nii_dimensions.csv');

% Function to load NIfTI file
function nii = load_nii(file_path)
    % Check if SPM is installed
    if exist('spm', 'file')
        % Use SPM to load NIfTI file
        nii = spm_vol(file_path);
        nii.img = spm_read_vols(nii);
    else
        error('SPM is not installed. Please install SPM to use this function.');
    end
end