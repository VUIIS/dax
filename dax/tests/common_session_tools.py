
import json

from dax import XnatUtils


class SessionTools:

    @staticmethod
    def get_connection(host):
        return XnatUtils.get_interface(host=host)

    @staticmethod
    def prep_project(intf, proj_id, subj_id, sess_id, scans, assessors):
        sess = intf.select_experiment(proj_id, subj_id, sess_id)
        for scan in scans:
            SessionTools.add_scan(sess, scan['name'], scan)
        for assessor in assessors:
            SessionTools.add_assessor(assessor, assessor['name'], assessor)

    @staticmethod
    def add_session(proj, name, parameters):
        sess = proj.scan(name)
        if sess.exists():
            sess.delete()
            sess = proj.session(name)
        sess.create(session=parameters['xsitype'])
        return sess

    @staticmethod
    def add_scan(sess, name, parameters):
        scn = sess.scan(name)
        if scn.exists():
            scn.delete()
            scn = sess.scan(name)
        kwargs = dict()
        print(parameters)
        print((parameters['xsitype']))
        kwargs[parameters['xsitype'] + '/type'] = parameters['type']
        kwargs[parameters['xsitype'] + '/quality'] = parameters['quality']
        scn.create(scans=parameters['xsitype'], **kwargs)
        for output in parameters['files']:
            for f in output[1]:
                scn.resource(output[0]).file(f).insert('./file.txt')
                # print output[0], f
        return scn

    @staticmethod
    def add_assessor(sess, name, parameters, inputs_policy="empty_if_not_set"):
        asr = sess.assessor(name)
        if asr.exists():
            asr.delete()
            asr = sess.assessor(name)
        kwargs = dict()
        kwargs[parameters['xsitype'] + '/proctype'] = parameters['proctype']
        kwargs[parameters['xsitype'] + '/procversion'] = '1.0.0'
        kwargs[parameters['xsitype'] + '/validation/status'] = "Needs QA"
        if inputs_policy == "empty_if_not_set":
            kwargs[parameters['xsitype'] + '/inputs'] =\
                json.dumps(parameters.get('inputs', {}))
        elif inputs_policy == "not_inputs":
            pass

        asr.create(assessors=parameters['xsitype'], **kwargs)
        for output in parameters['files']:
            for f in output[1]:
                asr.resource(output[0]).file(f).insert('./file.txt')
        return asr
