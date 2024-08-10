

res=load('results.mat').results;



Kb  = size(res.intensity(1).lik,2);


N=1;

tc=zeros(6,4);
bf=zeros(1,2);
df=[0,1];
mrf=0;
cleanup=0;
bb=[NaN,NaN,NaN;NaN,NaN,NaN];
vx = NaN; % Default to TPM voxel size
odir = []; % Output directory

% Read essentials from tpm (it will be cleared later)
tpm = res.tpm;
if ~isstruct(tpm) || ~isfield(tpm, 'bg1')
    tpm = spm_load_priors8(tpm);
end


d1     = size(tpm.dat{1});
d1      = d1(1:3);
M1      = tpm.M;


% Use the actual dimensions and orientations of
% the tissue priors.
odim = tpm.V(1).dim;
mat  = tpm.V(1).mat;


[pth,nam] = fileparts(res.image(1).fname);

ind  = res.image(1).n;
d    = res.image(1).dim(1:3);

[x1,x2,o] = ndgrid(1:d(1),1:d(2),1);
x3 = 1:d(3);


% do_cls   = any(tc(:)) || nargout>=1;
do_cls=0;nargout=0;

tiss(Kb) = struct('Nt',[]);
for k1=1:Kb
    if tc(k1,4) || any(tc(:,3)) || tc(k1,2) || nargout>=1,
        do_cls  = true;
    end

    if tc(k1,1),
        tiss(k1).Nt      = nifti;
        tiss(k1).Nt.dat  = file_array(fullfile(pth,['c', num2str(k1), nam, '.nii']),...
                                      res.image(n).dim(1:3),...
                                      [spm_type('uint8') spm_platform('bigend')],...
                                      0,1/255,0);
        tiss(k1).Nt.mat  = res.image(n).mat;
        tiss(k1).Nt.mat0 = res.image(n).mat;
        tiss(k1).Nt.descrip = ['Tissue class ' num2str(k1)];
        create(tiss(k1).Nt);
        do_cls = true;
    end
end


prm     = [3 3 3 0 0 0];
Coef    = cell(1,3);
Coef{1} = spm_bsplinc(res.Twarp(:,:,:,1),prm);
Coef{2} = spm_bsplinc(res.Twarp(:,:,:,2),prm);
Coef{3} = spm_bsplinc(res.Twarp(:,:,:,3),prm);


do_defs = any(df);
do_defs = do_cls | do_defs;


y = zeros([res.image(1).dim(1:3),3],'single');

M = M1\res.Affine*res.image(1).mat;


for z=1:length(x3)

    if do_defs
        % Compute the deformation (mapping voxels in image to voxels in TPM)
        [t1,t2,t3] = defs1(Coef,z,res.MT,prm,x1,x2,x3,M);

        if exist('y','var')
            % If needed later, save in variable y
            y(:,:,z,1) = t1;
            y(:,:,z,2) = t2;
            y(:,:,z,3) = t3;
        end
    end
end


clear tpm
M0  = res.image(1).mat;

M1 = mat;
d1 = odim;


% y here is the deformation field, invdef spm diffeo just makes reverse transformation to get 'y_' file which we sort of dont need


% Save the variable 'y' to a NIfTI file before invdef line

y_dims = size(y);
y_dims = y_dims(1:3);
N_pre_invdef = nifti;
N_pre_invdef.dat = file_array(fullfile(pth, ['fy_', nam, '.nii']), [y_dims,1,3], 'float32', 0, 1, 0);
N_pre_invdef.mat = M1;
N_pre_invdef.mat0 = M1;
N_pre_invdef.descrip = 'Forward Deformation';
N_pre_invdef.dat(:,:,:,:,:) = reshape(y,[y_dims,1,3]);
create(N_pre_invdef);
%N_pre_invdef.dat(:,:,:,:,:) = reshape(y, [d1, 1, 3]);

% y         = spm_diffeo('invdef',y,d1,eye(4),M0);
% y         = spm_extrapolate_def(y,mat);
% 
% N         = nifti;
% N.dat     = file_array(fullfile(pth,['y_', nam, '.nii']),...
%                        [d1,1,3],'float32',0,1,0);
% N.mat     = M1;
% N.mat0    = M1;
% N.descrip = 'Deformation';
% create(N);
% N.dat(:,:,:,:,:) = reshape(y,[d1,1,3]);








%% ----
% % Load original image metadata and data
% V = spm_vol('/Users/yongkailiu/Documents/untitled_folder/DWI3.nii');
% Y = spm_read_vols(V);
% 
% % Generate the original coordinate grid
% [Y1, Y2, Y3] = ndgrid(1:size(Y,1), 1:size(Y,2), 1:size(Y,3));
% 
% % Apply the displacement to the original grid coordinates
% newY1 = Y1 + y(:,:,:,1);
% newY2 = Y2 + y(:,:,:,2);
% newY3 = Y3 + y(:,:,:,3);
% 
% % Interpolate the original image data at the new coordinates
% Y_interp = interpn(Y1, Y2, Y3, Y, newY1, newY2, newY3, 'linear', 0);
% 
% % Update the volume header to reflect potential changes in dimensions
% V.fname = 'registered_image.nii';
% V.dim = size(Y_interp);  % Make sure the dimensions match the interpolated data
% 
% % Write the registered image
% spm_write_vol(V, Y_interp);


