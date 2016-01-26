__author__ = 'damons'
__purpose__ = 'Test the timestamp setting for subjects for various projects'

from dax import XnatUtils
from datetime import datetime
from datetime import timedelta

if __name__ == '__main__':
    XNAT = XnatUtils.get_interface()
    UPDATE_PREFIX = 'updated--'
    UPDATE_FORMAT = "%Y-%m-%d %H:%M:%S"
    SUBJECTS = XnatUtils.list_subjects(XNAT, '')
    for SUBJECT in SUBJECTS:
        update_start_time = datetime.now()
        print "Start Time %s for subject %s" % (update_start_time, SUBJECT['subject_label'])
        print "Begin Set %s" % datetime.now()
        xsi_type = 'xnat:mrSessionData'
        sess_obj = XnatUtils.get_full_object(XNAT, SUBJECT)
        last_modified_xnat = sess_obj.attrs.get(xsi_type+'/meta/last_modified')
        last_mod = datetime.strptime(last_modified_xnat[0:19], '%Y-%m-%d %H:%M:%S')
        update_str = (datetime.now()+timedelta(minutes=1)).strftime(UPDATE_FORMAT)
        sess_obj.attrs.set(xsi_type+'/original', UPDATE_PREFIX+update_str)
        update_end_time = datetime.now()
        print "End Set. Took  %s seconds\n" % (update_end_time - update_start_time).seconds
    XNAT.disconnect()