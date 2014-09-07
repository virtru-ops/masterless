import os
import yaml
import tempfile
import shutil
from sarge import capture_both
from .utils import cd
import logging

logger = logging.getLogger(__name__)


def git_clone(name, url, rev):
    print 'git clone %s' % url
    clone_process = capture_both('git clone %s' % url)
    if clone_process.returncode != 0:
        raise Exception('`git clone %s` failed' % url)
    with cd(name):
        checkout_process = capture_both('git checkout %s' % rev)
        if checkout_process.returncode != 0:
            raise Exception('`git checkout %s` failed' % rev)


class TopCollection(object):
    @classmethod
    def initialize(cls, initial_includes=None):
        initial_includes = initial_includes or []
        initial_top = {
            "base": {
                "*": initial_includes
            }
        }
        return TopCollection(initial_top)

    def __init__(self, initial_top):
        self._top = initial_top

    def add(self, include):
        self._top['base']['*'].append(include)

    def export_top_sls(self, dest):
        dest_file = open(dest, 'w')
        dest_file.write(yaml.dump(self._top, default_flow_style=False))
        dest_file.close()


class MasterlessTemplate(object):
    @classmethod
    def from_yaml(cls, template_path):
        template_path = os.path.abspath(template_path)

        # Load template yaml
        logger.debug('Loading template "%s"' % template_path)
        template_obj = yaml.load(open(template_path).read())

        # Determine project path
        project_path = os.path.dirname(template_path)
        logger.debug('Found project path "%s"' % project_path)

        # Determine build path
        build_path = os.path.join(project_path, 'masterless-build')
        logger.debug('Generated build path "%s"' % build_path)

        return MasterlessTemplate(template_obj, project_path, build_path)

    def __init__(self, template_obj, project_path, build_path):
        self._template_obj = template_obj
        self._project_path = project_path
        self._build_path = build_path

    def project_path(self, *joins):
        return os.path.join(self._project_path, *joins)

    def build_path(self, *joins):
        return os.path.join(self._build_path, *joins)

    def build(self):
        logger.debug("Starting Build")
        template_obj = self._template_obj

        self._initialize_build_path()

        # Git clone all of the formulas into a temporary directory
        temp_git_clone_path = tempfile.mkdtemp()

        formulas = template_obj.get('formulas', {})

        states_top = TopCollection.initialize()
        pillars_top = TopCollection.initialize()

        # Move states
        self._copy_project_dir_to_build('states')
        self._copy_project_dir_to_build('pillars')

        try:
            formula_path_infos = self._load_formulas(formulas,
                                                     temp_git_clone_path)

            for repo_name, formula_name in formula_path_infos:
                # Generate the paths for moving files around
                old_path = os.path.join(temp_git_clone_path, repo_name,
                                        formula_name)
                new_path = self.build_path('states', formula_name)

                # Move the files
                shutil.move(old_path, new_path)

                # Automatically add the formula to the top file
                states_top.add(formula_name)
        finally:
            # Delete the temp directory no matter what happens
            shutil.rmtree(temp_git_clone_path)

        self._process_tops_in_project_dir('states', states_top)
        self._process_tops_in_project_dir('pillars', pillars_top)

        states_top.export_top_sls(self.build_path('states', 'top.sls'))
        pillars_top.export_top_sls(self.build_path('pillars', 'top.sls'))

    def _initialize_build_path(self):
        build_path = self._build_path
        if os.path.exists(build_path):
            shutil.rmtree(build_path)

        # Ensure the build directory exists
        os.makedirs(build_path)

    def _copy_project_dir_to_build(self, dirname, create_if_not_exist=True):
        src_path = self.project_path(dirname)
        dest_path = self.build_path(dirname)

        # Clean up anything left over from a previous build
        if os.path.exists(dest_path):
            shutil.rmtree(dest_path)

        if not os.path.exists(src_path):
            if create_if_not_exist:
                os.makedirs(dest_path)
            else:
                return
        else:
            shutil.copytree(src_path, dest_path)

    def _load_formulas(self, formulas, clone_path):
        formula_path_infos = []
        with cd(clone_path):
            for formula_name, formula_info in formulas.iteritems():
                formula_url = formula_info['url']
                formula_rev = formula_info.get('rev', 'master')

                print "Cloning %s from %s" % (formula_name, formula_url)

                repo_name = formula_url.split('/')[-1][:-4]

                git_clone(repo_name, formula_url, formula_rev)

                formula_path_info = (repo_name, formula_name)

                formula_path_infos.append(formula_path_info)
        return formula_path_infos

    def _process_tops_in_project_dir(self, dirname, top):
        src_path = self.project_path(dirname)

        # Process all of the files in the path
        for name in os.listdir(src_path):
            file_or_dir_path = os.path.join(src_path, name)
            # if it's a directory then check if init.sls exists otherwise
            # ignore
            if os.path.isdir(file_or_dir_path):
                state_file = os.path.join(file_or_dir_path, 'init.sls')
                if not os.path.exists(state_file):
                    continue
            else:
                # Include states only (and ignore top.sls)
                if name == 'top.sls' or not name.endswith('.sls'):
                    continue

            # Only add states ignore all other files
            top_name = name[:-4]
            logger.debug("Adding top %s" % top_name)
            top.add(top_name)
