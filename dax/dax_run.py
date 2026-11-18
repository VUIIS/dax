import os

from dax.noxnat.builder_noxnat import TaskBuilderNoXnat
from dax.noxnat.database_noxnat import DatabaseNoXnat
from dax.noxnat.launcher_noxnat import TaskLauncherNoXnat


def run_noxnat(
    rootdir,
    yamlfile=None,
    projects=None,
    retry_failed=False,
    purge_needinputs=False,
    run_create=True,
    run_build=True,
    run_launch=True,
    run_update=True,
    run_finish=True
):
    builder = None
    launcher = None
    opt_processors = f'{rootdir}/settings/processors.yaml'
    opt_launcher = f'{rootdir}/settings/launcher.yaml'
    only_projects = None

    if projects:
        only_projects = projects.split(',') or None

    # Create a task launcher
    launcher = TaskLauncherNoXnat(rootdir)

    # Task builder
    builder = TaskBuilderNoXnat(rootdir)

    # Database
    db = DatabaseNoXnat(f'{rootdir}/db/dax.duckdb')

    # Load optional launcher settings from file
    if os.path.isfile(opt_launcher):
        launcher.apply_settings(opt_launcher)

    # Configure as requested
    if not run_launch:
        launcher.disable_launch()

    if not run_build:
        builder.disable_build()

    if not run_create:
        builder.disable_create()        

    if not run_update:
        launcher.disable_update()

    if not run_finish:
        launcher.disable_finish()

    # Set processors from command-line or default optional location
    if yamlfile:
        builder.set_processors(yamlfile)
    elif os.path.isfile(opt_processors):
        builder.set_processors(opt_processors)

    if run_build:
        builder.update_all(only_projects=only_projects)

    if run_launch:
        launcher.update(projects=only_projects)

    if retry_failed:
        launcher.retry_failed(projects=only_projects)

    if purge_needinputs:
        db.delete_all_need_inputs(projects=only_projects)
