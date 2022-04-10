
import pyxnat
import re
import os

SGP_PATTERN = '\w+-x-\w+-x-\w+_v[0-9]+-x-[0-9a-f]+'


def __pyxnat_assessor_type():
    return pyxnat.core.resources.Assessor


def full_label(project_id, subject_id, session_id,
               assessor_label):
    return '-x-'.join([project_id, subject_id, session_id, assessor_label])


# TODO: BenM/assessor_of_assessor/behaviour contingent on assessor version;
# the name shouldn't be used to test this
def full_label_from_assessor(assessor):
    assessor_label = assessor.label()
    if '-x-' in assessor_label:
        return assessor_label

    components = list()
    components.append(assessor_label)
    entity = assessor
    while True:
        entity = entity.parent()
        if entity is None:
            break
        components.append(entity.label())
    return '-x-'.join(reversed(components))


def parse_full_assessor_name(assessor_name):
    elements = assessor_name.split('-x-')
    assrdict = dict()

    if is_sgp_assessor(assessor_name):
        assrdict = dict(list(zip([
            'project_id', 'subject_label', 'session_label', 'label'],
            [elements[0], elements[1], '', assessor_name])))
    elif len(elements) == 5:
        # relabel is in use or old style with scan id in label
        assrdict = dict(list(zip(
            ['project_id', 'subject_label', 'session_label', 'label'],
            [elements[0], elements[1], elements[2], assessor_name])))
    elif len(elements) == 4:
        if len(elements[3]) == 36:
            # new style label with uuid
            assrdict = dict(list(zip(
                ['project_id', 'subject_label', 'session_label', 'label'],
                elements)))
        else:
            # old style label
            assrdict = dict(list(zip(
                ['project_id', 'subject_label', 'session_label', 'label'],
                [elements[0], elements[1], elements[2], assessor_name])))
    else:
        raise ValueError(("'assessor_name' parameter '{}' is not a valid full "
                          "assessor name".format(assessor_name)))

    return assrdict


def is_sgp_assessor(dirpath):
    # PROJECT-x-SUBJECT-x-PROCTYPE-x-UID
    return re.match(SGP_PATTERN, os.path.basename(dirpath))
