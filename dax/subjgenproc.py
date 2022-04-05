# launcher ???? -----> processor ???
import sys
import logging

import pandas as pd

from dax import XnatUtils

from .task import XnatTask


logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
LOGGER = logging.getLogger()


SGP_URI = '/REST/subjects?xsiType=xnat:subjectdata\
&columns=\
project,\
subject_label,\
proc:subjgenprocdata/label,\
proc:subjgenprocdata/procstatus,\
proc:subjgenprocdata/proctype,\
proc:subjgenprocdata/validation/status,\
proc:subjgenprocdata/inputs,\
last_modified&project={}',

SGP_RENAME = {
    'project': 'PROJECT',
    'subject_label': 'SUBJECT',
    'proc:subjgenprocdata/label': 'ASSR',
    'proc:subjgenprocdata/procstatus': 'PROCSTATUS',
    'proc:subjgenprocdata/proctype': 'PROCTYPE',
    'proc:subjgenprocdata/validation/status': 'QCSTATUS',
    'xsiType': 'XSITYPE',
    'proc:genprocdata/inputs': 'INPUTS'}


ASSR_URI = '/REST/experiments?xsiType=xnat:imagesessiondata\
&columns=\
project,\
subject_label,\
session_label,\
session_type,\
xnat:imagesessiondata/acquisition_site,\
xnat:imagesessiondata/date,\
xnat:imagesessiondata/label,\
proc:genprocdata/label,\
proc:genprocdata/procstatus,\
proc:genprocdata/proctype,\
proc:genprocdata/validation/status,\
last_modified,\
proc:genprocdata/inputs'


ASSR_RENAME = {
    'project': 'PROJECT',
    'subject_label': 'SUBJECT',
    'session_label': 'SESSION',
    'session_type': 'SESSTYPE',
    'xnat:imagesessiondata/date': 'DATE',
    'xnat:imagesessiondata/acquisition_site': 'SITE',
    'proc:genprocdata/label': 'ASSR',
    'proc:genprocdata/procstatus': 'PROCSTATUS',
    'proc:genprocdata/proctype': 'PROCTYPE',
    'proc:genprocdata/validation/status': 'QCSTATUS',
    'xsiType': 'XSITYPE',
    'proc:genprocdata/inputs': 'INPUTS'}


SCAN_URI = '/REST/experiments?xsiType=xnat:imagesessiondata\
&columns=\
project,\
subject_label,\
session_label,\
session_type,\
xnat:imagesessiondata/date,\
xnat:imagesessiondata/label,\
xnat:imagesessiondata/acquisition_site,\
xnat:imagescandata/id,\
xnat:imagescandata/type,\
xnat:imagescandata/quality'


SCAN_RENAME = {
    'project': 'PROJECT',
    'subject_label': 'SUBJECT',
    'session_label': 'SESSION',
    'session_type': 'SESSTYPE',
    'xnat:imagesessiondata/date': 'DATE',
    'xnat:imagesessiondata/acquisition_site': 'SITE',
    'xnat:imagescandata/id': 'SCANID',
    'xnat:imagescandata/type': 'SCANTYPE',
    'xnat:imagescandata/quality': 'QUALITY',
    'xsiType': 'XSITYPE'}


def build_project_subjgenproc(xnat, daxlauncher, project, includesubj=None):
    """
        Build the project

        :param xnat: pyxnat.Interface object
        :param project: project ID on XNAT
        :param includesubj: list of specific subjects to build, otherwise all
        :return: None
    """

    pdata = {}
    pdata['name'] = project
    pdata['scans'] = load_scan_data(xnat, [project])
    pdata['assessors'] = load_assr_data(xnat, [project])
    pdata['sgp'] = load_sgp_data(xnat, project)

    build_sgp_processors(xnat, pdata, daxlauncher, includesubj)


def build_sgp_processors(xnat, project_data, daxlauncher, includesubj=None):
    project = project_data['name']
    sgp_processors = daxlauncher.get_subjgenproc_processors(project)
    subjects = list(set([x['SUBJECT'] for x in project_data['sgp']]))
    xnat = daxlauncher.xnat

    # Filter list if specified
    if includesubj:
        subjects = [x for x in subjects if x in includesubj]

    for (subj, processor) in zip(subjects, sgp_processors):
        print(subj, processor.get_proctype())

        # Get list of inputs sets (not yet matched with existing)
        inputsets = processor.parse_subject(subj, project_data)
        print(inputsets)

        for inputs in inputsets:
            # Get assessor with these inputs and this proc type, create as needed
            (assr, info) = get_assessor(xnat, subj, inputs, processor, project_data)
            print(info)


            # TODO: apply reproc or rerun if needed
            # (assr,info) = undo_processing()
            # (assr,info) = reproc_processing()


            if info['PROCSTATUS'] in [NEED_TO_RUN, NEED_INPUTS]:
                (assr, info) = build_task(assr, info, processor, project_data, daxlauncher)
                print(info)
            else:
                LOGGER.debug('already built:{}'.format(info['LABEL']))

def build_task(assr, info, processor, project_data, dax_launcher):
    resdir = dax_launcher.resdir
    diskq = os.path.join(dax_launcher.resdir, 'DISKQ')
    old_proc_status = info['PROCSTATUS'] 
    old_qc_status = info['QCSTATUS'] 

    try:
        cmds = processor.build_cmds(
            assr,
            info,
            project_data,
            jobdir,
            resdir)

        batch_file = batch_path(dax_launcher, info['ASSR'])
        outlog = outlog_path(dax_launcher, info['ASSR'])

        batch = PBS(
            batch_file,
            outlog,
            cmds,
            processor.walltime_str,
            processor.memreq_mb,
            processor.ppn,
            processor.env,
            dax_launcher.job_email,
            dax_launcher.job_email_options,
            dax_launcher.job_rungroup,
            dax_launcher.xnat_host,
            processor.job_template)

        LOGGER.info('writing:' + batch_file)
        batch.write()

        # Set new statuses to be updated
        new_proc_status = JOB_RUNNING
        new_qc_status = JOB_PENDING

        # Write processor spec file for version 3
        try:
            # write processor spec file
            LOGGER.debug('writing processor spec file')
            write_processor_spec()
        except AttributeError as err:
            # older processor does not have version
            LOGGER.debug('procyamlversion not found'.format(err))

    except NeedInputsException as e:
        new_proc_status = NEED_INPUTS
        new_qc_status = e.value
    except NoDataException as e:
        new_proc_status = NO_DATA
        new_qc_status = e.value

    # Update on xnat
    if new_proc_status != old_proc_status or new_qc_status != old_qc_status:
        assr.attrs.mset({
            'proc:subjgenprocdata/procstatus': new_proc_status,
            'proc:subjgenprocdata/validation/status': new_qc_status,
        })

    # Update info
    info['PROCSTATUS'] = new_proc_status
    info['QCSTATUS'] =  new_qc_status

    return (assr, info)





# def undo_processing(self):
    #     """
    #     Unset the job ID, memory used, walltime, and jobnode information
    #      for the assessor on XNAT

    #     :except: pyxnat.core.errors.DatabaseError when attempting to
    #      delete a resource
    #     :return: None

    #     """
    #     from pyxnat.core.errors import DatabaseError

    #     self.set_qcstatus(JOB_PENDING)
    #     self.set_jobid(' ')
    #     self.set_memused(' ')
    #     self.set_walltime(' ')
    #     self.set_jobnode(' ')

    #     out_resource_list = self.assessor.resources()
    #     for out_resource in out_resource_list:
    #         if out_resource.label() not in REPROC_RES_SKIP_LIST:
    #             LOGGER.info('   Removing %s' % out_resource.label())
    #             try:
    #                 out_resource.delete()
    #             except DatabaseError:
    #                 LOGGER.error('   ERROR:deleting resource.')

# def reproc_processing(self):
    #     """
    #     If the procstatus of an assessor is REPROC on XNAT, rerun the assessor.

    #     :return: None

    #     """
    #     curtime = time.strftime("%Y%m%d-%H%M%S")
    #     local_dir = '%s_%s' % (self.assessor_label, curtime)
    #     local_zip = '%s.zip' % local_dir
    #     xml_filename = os.path.join(self.upload_dir, local_dir,
    #                                 '%s.xml' % self.assessor_label)

    #     # Make the temp dir
    #     mkdirp(os.path.join(self.upload_dir, local_dir))

    #     # Download the current resources
    #     out_resource_list = self.assessor.resources()
    #     for out_resource in resource_list:
    #         olabel = out_resource.label()
    #         if olabel not in REPROC_RES_SKIP_LIST and \
    #            len(out_resource.files().get()) > 0:
    #             LOGGER.info('   Downloading: %s' % olabel)
    #             out_res = self.assessor.resource(olabel)
    #             out_res.get(os.path.join(self.upload_dir, local_dir),
    #                         extract=True)

    #     # Download xml of assessor
    #     xml = self.assessor.get()
    #     with open(xml_filename, 'w') as f_xml:
    #         f_xml.write('%s\n' % xml)

    #     # Zip it all up
    #     cmd = 'cd %s && zip -qr %s %s/' % (self.upload_dir, local_zip,
    #                                        local_dir)
    #     LOGGER.debug('running cmd: %s' % cmd)
    #     os.system(cmd)

    #     # Upload it to Archive
    #     self.assessor.resource(OLD_RESOURCE)\
    #                  .file(local_zip)\
    #                  .put(os.path.join(self.upload_dir, local_zip))

    #     # Run undo
    #     self.undo_processing()

    #     # Delete the local copies
    #     os.remove(os.path.join(self.upload_dir, local_zip))
    #     shutil.rmtree(os.path.join(self.upload_dir, local_dir))




def get_json(xnat, uri):
    import json

    return json.loads(xnat._exec(uri, 'GET'))


def load_assr_data(xnat, project_filter):
    LOGGER.info('loading XNAT data, projects={}'.format(project_filter))

    # Build the uri to query with filters and run it
    _uri = ASSR_URI
    _uri += '&project={}'.format(','.join(project_filter))
    LOGGER.debug(_uri)
    _json = get_json(xnat, _uri)
    dfa = pd.DataFrame(_json['ResultSet']['Result'])

    # Rename columns
    dfa.rename(columns=ASSR_RENAME, inplace=True)

    return dfa


def load_scan_data(xnat, project_filter):
    #  Load data
    LOGGER.info('loading XNAT scan data, projects={}'.format(project_filter))

    # Build the uri query with filters and run it
    _uri = SCAN_URI
    _uri += '&project={}'.format(','.join(project_filter))
    LOGGER.info(_uri)
    _json = get_json(xnat, _uri)
    dfs = pd.DataFrame(_json['ResultSet']['Result'])

    dfs.rename(columns=SCAN_RENAME, inplace=True)

    return dfs

                                 
def load_sgp_data(xnat, project):
    LOGGER.info('loading XNAT data, project={}'.format(project))

    # Build the uri to query with filters and run it
    _uri = SGP_URI.format(project)
    LOGGER.debug(_uri)
    _json = get_json(xnat, _uri)
    dfp = pd.DataFrame(_json['ResultSet']['Result'])

    # Rename columns
    dfp.rename(columns=SGP_RENAME, inplace=True)

    return dfp


def get_assessor(xnat, subject, inputs, processor, project_data):
    proctype = processor.get_proctype()
    assrlist = project_data['sgp']
    assrlist = [x for x in assrlist if x['SUBJECT'] == subject]
    assrlist = [x for x in assrlist if x['PROCTYPE'] == proctype]
    assrlist = [x for x in project_data['sgp'] if x['INPUTS'] == inputs]

    if len(assrlist) > 0:
        # Get the info for the assessor
        info = assrlist[0]

        # Get the assessor object
        assr = xnat.select_experiment(
            info['PROJECT'],
            info['SUBJECT'],
            info['ASSR'])
    else:
        print('no existing assessors found, creating a new one')
        subj = xnat.select_subject(project_data.get('name'), subject)
        (assr, info) = processor.create_assessor(subj, inputs, relabel=True)

    return (assr, info)


def batch_path(dax_launcher, assessor_label):
    return os.path.join(
        dax_launcher.resdir,
        'DISKQ',
        'BATCH',
        '{}.slurm'.format(assessor_label))


def outlog_path(dax_launcher, assessor_label): 
    return os.path.join(
        dax_launcher.resdir, 
        'DISKQ',
        'OUTLOG',
        '{}.txt'.format(assessor_label))


