from dax.noxnat.builder_noxnat import TaskBuilderNoXnat
from dax.noxnat.database_noxnat import DatabaseNoXnat
from dax.noxnat.launcher_noxnat import TaskLauncherNoXnat


def run_noxnat(rootdir, yamlfile=None, projects=None, retry_failed=False, purge_needinputs=False, only_steps=None):
    run_build = True
    run_launch = True
    builder = None
    launcher = None
    opt_processors = f'{rootdir}/settings/processors.yaml'
    opt_launcher = f'{rootdir}/settings/launcher.yaml'

    if args.projects:
        projects = args.projects.split(',') or None

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
    if args.launchonly:
        run_build = False
        run_launch = True
        launcher.set_launch_only()
    elif args.createonly:
        run_build = True
        run_launch = False
        builder.set_create_only()
    elif args.buildonly:
        run_build = True
        run_launch = False
        builder.set_build_only()        
    elif args.finishonly:
        run_build = False
        run_launch = True
        launcher.set_finish_only()

    # Set processors from command-line or default optional location
    if yamlfile:
        builder.set_processors(yamlfile)
    elif os.path.isfile(opt_processors):
        builder.set_processors(opt_processors)

    if run_build:
        builder.update_all(only_projects=projects)

    if run_launch:
        launcher.update(projects=projects)

    if retry_failed:
        launcher.retry_failed(projects=projects)

    if purge_needinputs:
        db.delete_all_need_inputs(projects=projects)
