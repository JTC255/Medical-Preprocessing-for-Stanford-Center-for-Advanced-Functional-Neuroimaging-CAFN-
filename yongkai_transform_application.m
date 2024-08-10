clearvars, close all

def_path='/Users/theochiang/documents/MATLAB/nifti_files/y_FLAIR<=T2_Flair_Axial_p2_5.nii';
% Transformation Field


img_path='/Users/theochiang/documents/MATLAB/nifti_files/FLAIR<=T2_Flair_Axial_p2_5.nii';
%Original Image

% img_path='resampled_ex3.nii'; <- Is this saying that image should already
%be resmapled?


Nii = nifti(def_path); %gets nifti file contents from file path
Def = single(Nii.dat(:,:,:,1,:)); %<- gets data (Nii.dat) and loads it into single precision file type, float32, 
                                 % more easy to manage. Also, the one right here is the only element, so it could
                                 % be replaced by colon

d = size(Def); %<- dimensions of Def
Def = reshape(Def,[d(1:3) d(5)]); %the 3d transformation vector for each voxel is the only element in its list, thus
                                  %the 1 in the fourth dimension. We'll get rid of that dimension to make this whole
                                  %thing easier
mat = Nii.mat; %trans_affine in my python
%disp(mat)                         Nii.mat returns a matrix that translates
                                  %by (91.5,-127.5,-73) and scales by
                                  %(-1.5x,1.5y,1.5z)-> is this the map to physical coords?

fwhm = [0 0 0]; %full width half medium = [0,0,0], meaning no gaussian smoothing is applied to the data?
% Smoothing settings
vx = sqrt(sum(mat(1:3,1:3).^2)); %takes top left of matrix, the 3 scale values, square it and then squareroot 
                                 %gets rid of any negative sign
krn = max(fwhm./vx,0.25); %<- minimum kernel size of 0.25. Because the fhwm is 0,0,0, the first value will always be 0.
                          %so, nothing would change if fwhm./vx was just 0. However, the purpose of this function is to 
                          %ensure that the minimum kernel size is 0.25 units. krn is not referenced in this code
                          %anywhere else besides commented out code. In
                          %this case vx is 1.5-1.5-1.5, but because 0 is devided by vx, it's still 0

%krn and vx are not mentioned anywhere else besides commented out smoothing

%% affine 
NI = nifti(img_path);     %original image called

M0 = NI.mat;              %matrix called, I believe to get from image to physical
M = inv(M0);              %M now is the inverse, so it converts physiccal to image
oM = zeros(4,4);          %creating empty 4x4

if ~all(M(:)==oM(:))
    % Generate new deformation (if needed)
    Y = affine(Def,M); 
    % Y is now the transformation field combined with matrix that converts 
                       % phys to image (AKA AFFINE MATRIX). Part of registration
               
end
%% nonrigid (PROBABLY REGISTRATION)

f0 = single(NI.dat(:,:,:)); % simplified single format of base image
intrp = 1;%specifies that this is Linear interpolation
intrp = [intrp*[1 1 1], 0 0 0]; % returns [1,1,1,0,0,0] each of first 3 specifies degree of interpolation
                                % in that dimension, for example 0 = nearest neighbor, 3 = cubic interp
                                % next 3 numbers specify wrapping/periodic boundary where 1 = there is
                                % periodic boundary means like the data is repeated in a pattern and edges are 
                                % connected to another version of that image. So 3 dimensions are specified here,
                                % which is super chill

                        %THESE TWO LINES ARE THE INTERPOLATION PROCESS,
                        %FIRST LINE FINDS coefficients for 
%c = spm_diffeo('bsplinc',f0,intrp);

% FORMAT c = spm_diffeo('bsplinc',f,d) <- documentation for bsplins diffeo
%   f - an image
%   d(1:3) - degree of B-spline (from 0 to 7) along different dimensions
%       d(4:6) - 1/0 to indicate wrapping along the dimensions
%   c - returned volume of B-spline coefficients
%
% This function deconvolves B-splines from f, returning
% coefficients, c.  These coefficients are then passed to 'bsplins'
% in order to sample the data using B-spline interpolation.

f1 = spm_diffeo('bsplins',f0,Y,intrp);
%FORMAT [f,dfx,dfy,dfz] = spm_diffeo('bsplins', c, y,d) <- documentation for bsplins diffeo
% c          - input image(s) of B-spline coefficients n1*n2*n3*n4
%              - see 'bsplinc'
% y          - points to sample n1*n2*n3*3
% d(1:3)     - degree of B-spline (from 0 to 7) along different dimensions
%              - these must be same as used by 'bsplinc'
% d(4:6)     - 1/0 to indicate wrapping along the dimensions
%
% f           - output image n1*n2*n3*n4
% dfx,dfy,dfz - sampled first derivatives
%
% c, f and y are single precision floating point.
%
% This function takes B-spline basis coefficients from spm_bsplinc,
% and re-convolves them with B-splines centred at the new sample points.
% 
% Note that nearest neighbour interpolation is used instead of 0th
% degree B-splines, and the derivatives of trilinear interpolation are
% returned instead of those of 1st degree B-splines.  The difference is
% extremely subtle.
%
% c, f and y are single precision floating point.

%SO COEFFICIENTS * Y/(TRANSFORMATION FIELD COMBINED WITH PHYSICAL COORD TRANSLATOR) = ACTUAL COORDS THROUGH INTERP?
%FIGURE OUT IF THIS PART IS RESAMPLING? IT HAPPENS AFTER REGISTRATION??

figure,imshow(f1(:,:,40),[]) %This is just visualizing slice 40 of the new image

% if sum(job.fwhm.^2)~=0
%     spm_smooth(f1,f1,krn); % Side effects
% end



%% make new

NO = NI;
NO.descrip='Warped';

%most of this stuff is just filling in metadata of new file
%setting name of new file to have ex_ prefix

name_pre = NO.dat.fname(1:47);
NO.dat.fname = NO.dat.fname(48:end);

NO.dat.fname=['ex_',NO.dat.fname];
NO.dat.fname = [name_pre,NO.dat.fname];



dim = size(Def);                   %specifying dimensions = transformation field (but is it already this, or does this determine that aspect?)
dim = dim(1:3);                    %getting rid of last dimension of transformation vector, since are not transforming anything, but is just one intensity value

NO.dat.dim = [dim NI.dat.dim(4:end)]; 
NO.dat.offset = 0; % For situations where input .nii images have an extension.
NO.mat = mat;      %reencode the same matrix from original file that gives image coords from physical
NO.mat0 = mat;     %SAME AS OTHER PHYSICAL COORD TTRANSLATOR BUT DOESN'T PAY ATTENTION TO HEADER INFO?


NO.mat_intent = 'Aligned'; 
NO.mat0_intent = 'Aligned';% These two lines specify intent-of-file, a required part of the metadata, and these two are already registered images, so they are aligned

NO.extras = [];        %nothing else to add

NO.dat(:,:,:,1,1,1) = f1;   %actual image matrix. NO and F1 ALREADY HAVE MATCHING DIMENSION ARRAYS? WHY NEED EXTRA 1's? CODE WORKS WITH NO 1's

create(NO); %creates new transformed warped image file



%NEED TO FIND OUT WHAT TEMPLATE IS USED AND WHERE, OR IS THIS JUST REGISTRATION?
%^ I THINK TRANSFORMATION TEMPLATE IS USED ALREADY TO MAKE Y? SO NOW THIS IS NORMALIZING BECAUSE OF THAT. 


%{
output_f = spm_bsplins(c, Y(:,:,:,1), Y(:,:,:,2), Y(:,:,:,3), [1,1,1]);
% Print the outpute
figure,imshow(output_f(:,:,40),[])




for mex files:
mex -outdir /Users/theochiang/spm-main /Users/theochiang/spm-main/src/spm_bsplins.c /Users/theochiang/spm-main/src/bsplines.c

%}

disp(size(Y))
disp(size(f0))
disp(size(f1))