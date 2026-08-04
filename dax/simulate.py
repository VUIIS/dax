


# show set of assssors thar would exist after build but dont create anythun new
# must iterate to get downstream assessors



class DaxSimulator(object):

    def __init__(self, rc):
        self._redcap = rc

    def simulate(
        xnat,
        project,
        processor=None,
        subject=None,
        unverified=None,
    ):
        print(f'simulate build:{project=}:{processor=}:{subject=}:{unverified=}')

        # Load project info
        info = load_project_info(xnat, project)

        print('PROJECT INFO:{project=}')
        print(info)


        # Simulate build on processor(s) to get potential assessors


        # Display existing and potential assessors
