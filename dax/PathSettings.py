"""
    Title: PathSettings.py
    Author: Benjamin Yvernault
    contact: b.yvernault@ucl.ac.uk
    Purpose:
        Python file defining the paths required by your spiders/processors/modules.
"""

__author__ = 'byvernault'
__email__ = 'b.yvernault@ucl.ac.uk'
__purpose__ = "Python file defining the paths required by your spiders/processors/modules."
__modifications__ = '24 August 2015 - Original write'

import os
from os.path import expanduser

USER_HOME = expanduser("~")
# Definition of the different paths.
# Path for software for Spider/Processor on default system for Vanderbilt University
DEFAULT_MASIMATLAB_PATH = os.path.join(USER_HOME,'masimatlab')
DEFAULT_ANTS_PATH = '/scratch/mcr/ANTs-build/bin/'
DEFAULT_ART_PATH = '/scratch/mcr/art/'
DEFAULT_FSL_PATH = '/scratch/mcr/fsl5/'
DEFAULT_MASIFUSION_DTIQA = '/scratch/mcr/src/masi-fusion/'  #V208
DEFAULT_MASIFUSION_MA = '/scratch/mcr/full-multi-atlas/masi-fusion/src/'  #V253 current
DEFAULT_MIPAV_PATH = '/scratch/mcr/full-multi-atlas/mipav/'
DEFAULT_MIPAV_PATH_CURRENT = '/scratch/mcr/full-multi-atlas/mipav-current/'
DEFAULT_NIFTYREG_PATH = '/scratch/mcr/NiftyReg/niftyreg_install/'
DEFAULT_RECON_FREESURFER_PATH = '/scratch/mcr/freesurfer/'
DEFAULT_REGALADIN_PATH = '/scratch/mcr/NiftyReg/niftyreg_build/reg-apps/reg_aladin'
DEFAULT_SPM_PATH = '/gpfs21/scratch/mcr/spm8/'
DEFAULT_SPM12_PATH = '/gpfs21/scratch/mcr/spm12/'
DEFAULT_TRACULA_FREESURFER_PATH = '/scratch/mcr/freesurfer5.3_TRACULA2014-05-26'
#Path for tools for Module on default system for Vanderbilt University
DEFAULT_DCM2NII_PATH = '/gpfs21/scratch/mcr/mricron'
DEFAULT_DCMDJPEG_PATH = '/usr/local/dcmtk/latest/x86_64/gcc46/nonet/bin'
#REDCap
API_URL = 'https://redcap.vanderbilt.edu/api/'

#MASIMATLAB
if 'MASIMATLAB_PATH' not in os.environ:
    MASIMATLAB_PATH = DEFAULT_MASIMATLAB_PATH
else:
    MASIMATLAB_PATH = os.environ['MASIMATLAB_PATH']
#ANTS_PATH
if 'ANTS_PATH' not in os.environ:
    ANTS_PATH = DEFAULT_ANTS_PATH
else:
    ANTS_PATH = os.environ['ANTS_PATH']
#ART_PATH
if 'ART_PATH' not in os.environ:
    ART_PATH = DEFAULT_ART_PATH
else:
    ART_PATH = os.environ['ART_PATH']
#FSL_PATH
if 'FSL_PATH' not in os.environ:
    FSL_PATH = DEFAULT_FSL_PATH
else:
    FSL_PATH = os.environ['FSL_PATH']
#MASIFUSION_PATH
#v208
if 'MASIFUSION_DTIQA' not in os.environ:
    MASIFUSION_DTIQA = DEFAULT_MASIFUSION_DTIQA
else:
    MASIFUSION_DTIQA = os.environ['MASIFUSION_DTIQA']
#Current
if 'MASIFUSION_MA' not in os.environ:
    MASIFUSION_MA = DEFAULT_MASIFUSION_MA
else:
    MASIFUSION_MA = os.environ['MASIFUSION_MA']
#MIPAV_PATH
if 'MIPAV_PATH' not in os.environ:
    MIPAV_PATH = DEFAULT_MIPAV_PATH
else:
    MIPAV_PATH = os.environ['MIPAV_PATH']
#NIFTYREG_PATH
if 'NIFTYREG_PATH' not in os.environ:
    NIFTYREG_PATH = DEFAULT_NIFTYREG_PATH
else:
    NIFTYREG_PATH = os.environ['NIFTYREG_PATH']
#RECON_FREESURFER_PATH
if 'RECON_FREESURFER_PATH' not in os.environ:
    RECON_FREESURFER_PATH = DEFAULT_RECON_FREESURFER_PATH
else:
    RECON_FREESURFER_PATH = os.environ['RECON_FREESURFER_PATH']
#REGALADIN_PATH
if 'REGALADIN_PATH' not in os.environ:
    REGALADIN_PATH = DEFAULT_REGALADIN_PATH
else:
    REGALADIN_PATH = os.environ['REGALADIN_PATH']
#SPM_PATH
if 'SPM_PATH' not in os.environ:
    SPM_PATH = DEFAULT_SPM_PATH
else:
    SPM_PATH = os.environ['SPM_PATH']
if 'SPM12_PATH' not in os.environ:
    SPM12_PATH = DEFAULT_SPM12_PATH
else:
    SPM_PATH = os.environ['SPM12_PATH']

#TRACULA_FREESURFER_PATH
if 'TRACULA_FREESURFER_PATH' not in os.environ:
    TRACULA_FREESURFER_PATH = DEFAULT_TRACULA_FREESURFER_PATH
else:
    TRACULA_FREESURFER_PATH = os.environ['TRACULA_FREESURFER_PATH']
#DCM2NII_PATH
if 'DCM2NII_PATH' not in os.environ:
    DCM2NII_PATH = DEFAULT_DCM2NII_PATH
else:
    DCM2NII_PATH = os.environ['DCM2NII_PATH']
#DCMDJPEG_PATH
if 'DCMDJPEG_PATH' not in os.environ:
    DCMDJPEG_PATH = DEFAULT_DCMDJPEG_PATH
else:
    DCMDJPEG_PATH = os.environ['DCMDJPEG_PATH']
