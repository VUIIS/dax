""" Module to generate NIFTI from DICOM with dcm2niix"""

from dax import XnatUtils, ScanModule
import os
import re
import glob
import logging
import nibabel as nib
import subprocess as sb
import shutil
from string import Template

LOGGER = logging.getLogger('dax')

DCM2NIIX_PATH = '/usr/local/bin/dcm2niix'
MODULE_NAME = 'dcm2niix'
TMP_PATH = '/tmp/' + MODULE_NAME
TEXT_REPORT = 'ERROR/WARNING for ' + MODULE_NAME + ':\n'
CMD_TEMPLATE = '''${dcm2niix} -z y -f %s_%d ${dicom}'''


class Module_dcm2niix(ScanModule):
    """ Module to convert dicom to nifti using dcm2niix """
    def __init__(self,
                 mod_name=MODULE_NAME,
                 directory=TMP_PATH,
                 email=None,
                 text_report=TEXT_REPORT,
                 dcm2niixpath=DCM2NIIX_PATH,
                 scantype_filter=None):

        """ init function overridden from base-class"""
        super(Module_dcm2niix, self).__init__(
            mod_name, directory, email,
            text_report=text_report)
        self.dcm2niixpath = dcm2niixpath
        self.scantype_filter = scantype_filter
        print('DEBUG:' + self.dcm2niixpath)

    def prerun(self, settings_filename=''):
        """ prerun function overridden from base-class"""
        self.make_dir(settings_filename)

    def afterrun(self, xnat, project):
        """ afterrun function overridden from base-class"""
        if self.send_an_email:
            self.send_report()

        try:
            shutil.rmtree(self.directory)
        except Exception:
            LOGGER.warn('dcm2niix:afterrun:delete failed ' + self.directory)

    def needs_run(self, cscan, xnat):
        """ needs_run function overridden from base-class
                cscan = CacheScan object from XnatUtils
            return True or False
        """

        # Check output
        if XnatUtils.has_resource(cscan, 'NIFTI'):
            LOGGER.debug('Has NIFTI')
            return False

        # Check input
        if not XnatUtils.has_resource(cscan, 'DICOM'):
            LOGGER.debug('No DICOM resource')
            return False

        if XnatUtils.is_cscan_unusable(cscan):
            LOGGER.debug('Unusable scan')
            return False

        return True

    def run(self, scan_info, scan_obj):
        """ run function to convert dicom to nifti and upload data"""
        if not len(scan_obj.resource('DICOM').files().get()) > 0:
            LOGGER.debug('no DICOM files')
            return

        LOGGER.debug('downloading all DICOMs...')
        scan_obj.resource('DICOM').get(self.directory, extract=True)

        # convert dcm to nii via dcm2niix
        dcm_dir = os.path.join(self.directory, 'DICOM')
        success = self.dcm2niix(dcm_dir)

        # Check if nifti was created
        nifti_list = [f for f in os.listdir(dcm_dir) if f.endswith('.nii.gz')]
        if not nifti_list or not success:
            LOGGER.warn('{0} conversion failed'.format(scan_info['scan_id']))
            self.log_warning_error('dcm2nii Failed', scan_info, error=True)
        else:
            self.upload_converted_images(dcm_dir, scan_obj, scan_info)

        # clean tmp folder
        self.clean_directory()

    def dcm2niix(self, dcm_path):
        """ convert dicom to nifti using dcm2niix """
        LOGGER.debug('converting dcm to nii...')
        cmd_data = {'dcm2niix': self.dcm2niixpath, 'dicom': dcm_path}
        cmd = Template(CMD_TEMPLATE).substitute(cmd_data)
        try:
            print('DEBUG:running cmd:' + cmd)
            sb.check_output(cmd.split())
        except sb.CalledProcessError:
            return False

        return True

    def upload_converted_images(self, dcm_dir, scan_obj, scan_info):
        """ upload images after checking them """
        nifti_list = []
        bval_path = ''
        bvec_path = ''

        LOGGER.debug('uploading the NIFTI files to XNAT...')

        # Get the NIFTI/bvec/bval files from the folder:
        for fpath in glob.glob(os.path.join(dcm_dir, '*')):
            if not os.path.isfile(fpath):
                continue

            if fpath.lower().endswith('.dcm'):
                continue

            # Rename to remove bad characters
            fname = os.path.basename(fpath)
            newfname = re.sub(r'[^.a-zA-Z0-9\-\_]', '_', fname)
            print(fname, newfname)
            
            if newfname != fname:
                newfpath = os.path.join(dcm_dir, newfname)
                os.rename(fpath, newfpath)
                fpath = newfpath

            if fpath.lower().endswith('.bval'):
                bval_path = fpath
            elif fpath.lower().endswith('.bvec'):
                bvec_path = fpath
            elif fpath.endswith('ADC.nii.gz'):
                LOGGER.warn('ignoring ADC NIFTI:' + fpath)
            elif fpath.lower().endswith('.nii.gz'):
                nifti_list.append(fpath)

        # Check
        success = self.check_outputs(
            scan_info, nifti_list, bval_path, bvec_path
        )
        if not success:
            return

        # Upload
        print(nifti_list)
        XnatUtils.upload_files_to_obj(
            nifti_list, scan_obj.resource('NIFTI'), remove=True
        )
        if os.path.isfile(bval_path) and os.path.isfile(bvec_path):
            # BVAL/BVEC
            XnatUtils.upload_file_to_obj(
                bval_path, scan_obj.resource('BVAL'), remove=True
            )
            XnatUtils.upload_file_to_obj(
                bvec_path, scan_obj.resource('BVEC'), remove=True
            )

        # more than one NIFTI uploaded
        if len(nifti_list) > 1:
            LOGGER.warn('dcm2nii:{} multiple NIFTI'.format(
                scan_info['scan_id']))
            self.log_warning_error('multiple NIFTI', scan_info)

    def check_outputs(self, scan_info, nifti_list, bval, bvec):
        """ Check outputs (opening nifti works)"""
        for nifti_fpath in nifti_list:
            try:
                nib.load(nifti_fpath)
            except nib.ImageFileError:
                LOGGER.warn(
                    '''dcm2niix:{}:{} is not NIFTI'''.format(
                        scan_info['scan_id'],
                        os.path.basename(nifti_fpath)))
                self.log_warning_error(
                    'non-valid nifti created', scan_info, error=True)
                return False

        return True
