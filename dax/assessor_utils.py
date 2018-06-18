
import pyxnat


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
    if len(elements != 4):
        raise ValueError(("'assessor_name' parameter '{}' is not a valid full "
                          "assessor name".format(assessor_name)))
    return dict(zip(
        ['project_id', 'subject_id', 'session_id', 'assessor_label'],
        elements))





