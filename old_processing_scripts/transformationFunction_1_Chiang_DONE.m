clc,clearvars, close all


function [outputFile] = transformation(file,prefix)
    matlabbatch{1}.spm.spatial.normalise.estwrite.subj.vol = {file}; %to align
    matlabbatch{1}.spm.spatial.normalise.estwrite.subj.resample = {file};%to write
    matlabbatch{1}.spm.spatial.normalise.estwrite.eoptions.biasreg = 0.0001;
    matlabbatch{1}.spm.spatial.normalise.estwrite.eoptions.biasfwhm = 60;
    matlabbatch{1}.spm.spatial.normalise.estwrite.eoptions.tpm = {'/Users/theochiang/documents/MATLAB/spm-main/tpm/TPM.nii'}; %tissue probability map, probability of different tissues being present at each voxel. <- why necessary?
    matlabbatch{1}.spm.spatial.normalise.estwrite.eoptions.affreg = 'mni'; %mni = registration template/space used in spatial normalization
    matlabbatch{1}.spm.spatial.normalise.estwrite.eoptions.reg = [0 0 0.1 0.01 0.04];
    matlabbatch{1}.spm.spatial.normalise.estwrite.eoptions.fwhm = 0;
    matlabbatch{1}.spm.spatial.normalise.estwrite.eoptions.samp = 3;
    matlabbatch{1}.spm.spatial.normalise.estwrite.woptions.bb = [-78 -112 -70
                                                                 78 76 85];
    matlabbatch{1}.spm.spatial.normalise.estwrite.woptions.vox = [2 2 2];
    matlabbatch{1}.spm.spatial.normalise.estwrite.woptions.interp = 1;
    matlabbatch{1}.spm.spatial.normalise.estwrite.woptions.prefix = prefix; %prefix

    
    %bb, interpolation #,biasfwhm

    % Run the normalization process
    spm_jobman('run', matlabbatch);

    % Extract the filename of the normalized image from the prefix
    [~, filename, ext] = fileparts(file);
    normalizedFilename = fullfile(fileparts(file), [prefix, filename, ext]);

    % Assign the normalized filename to the outputFile output parameter
    outputFile = normalizedFilename;
end



%original code for FLAIR, FLAIR
%newFile = transformation('/Users/theochiang/Desktop/Radiology Internship 2024/Archive - Files/UCLA-321/201506251138-MR/FLAIR<=T2_Flair_Axial_p2_5.nii,1','/Users/theochiang/Desktop/Radiology Internship 2024/Archive - Files/UCLA-321/201506251138-MR/FLAIR<=T2_Flair_Axial_p2_5.nii,1','w3');

%DWI: one is FLAIR, DWI, one is DWI, DWI

new_flair_image = transformation('/Users/theochiang/Desktop/Training Data/Base Images/FLAIR<=AX_FLAIR_5.nii',['w3' ...
    ''])
