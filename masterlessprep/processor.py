import os
import yaml
import tempfile
import shutil
from sarge import Capture, capture_both
from .utils import cd


def git_clone(name, url, rev):
    print 'git clone %s' % url
    clone_process = capture_both('git clone %s' % url)
    if clone_process.returncode != 0:
        raise Exception('`git clone %s` failed' % url)
    with cd(name):
        checkout_process = capture_both('git checkout %s' % rev)
        if checkout_process.returncode != 0:
            raise Exception('`git checkout %s` failed' % rev)


class MasterlessTemplate(object):
    @classmethod
    def from_yaml(cls, template_path):
        template_path = os.path.abspath(template_path)

        # Load template yaml
        template_obj = yaml.load(open(template_path).read())

        # Determine build path
        template_dir_path = os.path.dirname(template_path)
        build_path = os.path.join(template_dir_path, 'masterless-build')

        return MasterlessTemplate(template_obj, build_path)

    def __init__(self, template_obj, build_path):
        self._template_obj = template_obj
        self._build_path = build_path

    def build(self):
        template_obj = self._template_obj
        build_path = self._build_path

        if os.path.exists(build_path):
            shutil.rmtree(build_path)

        # Ensure the build directory exists
        os.makedirs(build_path)

        # Git clone all of the formulas into a temporary directory
        temp_git_clone_path = tempfile.mkdtemp()

        formulas = template_obj.get('formulas', {})

        try:
            formula_path_infos = self._load_formulas(formulas,
                                                     temp_git_clone_path)

            for repo_name, formula_name  in formula_path_infos:
                # Generate the paths for moving files around
                old_path = os.path.join(temp_git_clone_path, repo_name,
                                        formula_name)
                new_path = os.path.join(build_path, formula_name)

                # Move the files
                shutil.move(old_path, new_path)
        finally:
            # Delete the temp directory no matter what happens
            shutil.rmtree(temp_git_clone_path)

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
