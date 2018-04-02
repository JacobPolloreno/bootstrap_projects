import click
import colorama
import jinja2
import glob
import os
import subprocess

from colorama import Fore
from colorama import Style
from typing import Dict
from shutil import copy
from shutil import copytree
from shutil import rmtree
from urllib.parse import urlparse


TEMPLATE_BASE_PATH = os.path.abspath('./templates')
CLANG_TEMPLATE_PATH = os.path.join(TEMPLATE_BASE_PATH, 'clang')
PYTHON_TEMPLATE_PATH = os.path.join(TEMPLATE_BASE_PATH, 'py')


class ExpandedPath(click.Path):
    def convert(self, value, *args, **kwargs):
        value = os.path.expanduser(value)
        return super(ExpandedPath, self).convert(value, *args, **kwargs)


def render_template(template_path: str, context: Dict) -> str:
    """Render a jinja2 template with context variables

    Args:
        template_path (str): path to template to use
        context (dict): variables to replace in jinja2 template

    Returns:
        str: rendered template in str format
    """
    path, filename = os.path.split(template_path)
    return jinja2.Environment(
        loader=jinja2.FileSystemLoader(path or './')
    ).get_template(filename).render(context)


def print_success() -> None:
    """Print a successfuly message and art to the user

    """
    print(Fore.YELLOW)
    with open(os.path.join(TEMPLATE_BASE_PATH, 'success.txt'), 'r') as f:
        print(f.read())


def get_from_git(args):
    return subprocess.call_check(['git'] + list[args])


def get_c_config(name: str) -> Dict:
    """Build configuration with user input.

    Args:
        name (str): project name

    Returns:
        dict: configuration dictionary for a c project
    """
    config = {}
    config['name'] = name
    if click.prompt("Do you want to add your libft?", type=bool):
        if click.prompt("From Git repo?", type=bool):
            url = urlparse(click.prompt("What's the git repo url?", type=str))
            if url.netlock != 'github.com':
                raise click.UsageError("github.com repos only supported")
            get_from_git(['submodule', 'add', url.geturl()])
        else:
            config['libft_path'] = os.path.abspath(
                os.path.expanduser(
                    click.prompt(
                        'Please enter the path to your libft',
                        type=ExpandedPath(
                            exists=True,
                            file_okay=False,
                            dir_okay=True),
                        default=os.path.expanduser('~/Documents/libft/'))))
    if click.prompt(f'Do you want a "{name}.c" file?', type=bool):
        config['main'] = name + '.c'
    elif click.prompt("Do you want a 'main.c' file?", type=bool):
        config['main'] = 'main.c'
    if click.prompt("Create a author file?", type=bool):
        config['author'] = click.prompt("Input your username", type=str)
    if click.prompt("Create a README.md?", type=bool):
        config['readme'] = 'True'
    return config


def get_py_config(name: str) -> Dict:
    """Build configuration with user input.

    Args:
        name (str): project name

    Returns:
        dict: configuration dictionary for a python project
    """
    config = {}
    config['name'] = name
    if click.prompt("Do you want a virtualenv?", type=bool):
        config['venv'] = 'True'
    if click.prompt("Install dependencies(requirements.txt)?", type=bool):
        config['depend'] = os.path.abspath(os.path.expanduser(click.prompt(
            'Please enter the path to your requirements.txt',
            type=ExpandedPath(exists=True, file_okay=True, dir_okay=False))))
    if click.prompt("Do you want to create testing files?", type=bool):
        config['testing'] = 'True'
        if click.prompt(
            "Do you want to install pyTest testing framework?",
                type=bool):
            config['pytest'] = "True"
    if click.prompt("Create a author file?", type=bool):
        config['author'] = click.prompt("Input your username", type=str)
    if click.prompt("Create a README.md?", type=bool):
        config['readme'] = 'True'
    return config


def create_program(
        name: str,
        lang: str,
        output_dir: str,
        config: Dict) -> None:
    """Create a project dir with starter files

    Args:
        name (str): project name
        lang (str): project programming language (c and python supported)
        output_dir (str): path to output dir
        config (dict): project configuration
    """
    if 'author' in config:
        with open(os.path.join(output_dir, 'author'), 'w') as f:
            f.write(config['author'])
    if 'readme' in config:
        with open(os.path.join(output_dir, 'README.md'), 'w') as f:
            readme = render_template(
                os.path.join(TEMPLATE_BASE_PATH, 'readme.md.j2'),
                context=config)
            f.write(readme)
    if lang == 'c':
        copy(os.path.join(CLANG_TEMPLATE_PATH, 'C.gitignore'),
             os.path.join(output_dir, '.gitignore'))
        srcs_dir = os.path.join(output_dir, 'srcs')
        incl_dir = os.path.join(output_dir, 'includes')
        os.mkdir(srcs_dir)
        os.mkdir(incl_dir)
        with open(os.path.join(output_dir, 'Makefile'), 'w') as f:
            makefile = render_template(
                os.path.join(CLANG_TEMPLATE_PATH, 'Makefile.j2'),
                context=config)
            f.write(makefile)
        if 'main' in config:
            with open(os.path.join(srcs_dir, config['main']), 'w') as f:
                main = render_template(
                    os.path.join(CLANG_TEMPLATE_PATH, 'main.j2'),
                    context=config)
                f.write(main)
        if 'libft_path' in config:
            output_libft_path = os.path.join(output_dir, 'libft')
            copytree(config['libft_path'], output_libft_path)
            if os.path.exists(os.path.join(output_libft_path, '.git')):
                rmtree(os.path.join(output_libft_pathm, '.git'))
    elif lang == 'py':
        copy(os.path.join(PYTHON_TEMPLATE_PATH, 'Python.gitignore'),
             os.path.join(output_dir, '.gitignore'))
        open(os.path.join(output_dir, '__init__.py'), 'w').close()
        open(os.path.join(output_dir, 'main.py'), 'w').close()
        if 'venv' in config:
            subprocess.run(["virtualenv", "venv"], cwd=output_dir)
        if 'depend' in config:
            copy(
                config['depend'],
                os.path.join(
                    output_dir,
                    'requirements.txt'))
            if 'venv' in config:
                subprocess.run(["venv/bin/pip", "install",
                                "-r", "requirements.txt"], cwd=output_dir)
            else:
                subprocess.run(["pip", "install",
                                "-r", "requirements.txt"], cwd=output_dir)
        if 'testing' in config:
            copy(
                os.path.join(
                    PYTHON_TEMPLATE_PATH,
                    'test_project.py'),
                os.path.join(
                    output_dir,
                    'test_project.py'))
            if 'pytest' in config:
                if 'venv' in config:
                    subprocess.run(["venv/bin/pip", "install",
                                    "pytest"], cwd=output_dir)
                else:
                    subprocess.run(["pip", "install",
                                    "pytest"], cwd=output_dir)

    print(Fore.GREEN)
    print("\nFiles created:\n")
    print(glob.glob(os.path.join(output_dir, ".*")))
    print(glob.glob(os.path.join(output_dir, "*"), recursive=True))
    print_success()


@click.command()
@click.option('--name', '-n',
              prompt='What do you want to call your project?',
              help='Name of your project')
@click.option('--lang', '-l', type=click.Choice(['c', 'py']),
              prompt='Which language is your project in [c/py]?',
              help='Which language is your project in[c/python]?')
@click.option('--output_dir', '-o', type=click.Path(
    file_okay=False, dir_okay=True, resolve_path=True))
def get_user_input(name, lang, output_dir):
    if not output_dir:
        output_dir = name
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    else:
        raise OSError(Fore.RED + f'{output_dir} exists already')
    print(Fore.GREEN)
    if lang == 'c':
        config = get_c_config(name)
    elif lang == 'py':
        config = get_py_config(name)
    print()
    for k, v in config.items():
        print(f"\t{k} : {v}")
    path = os.path.join(output_dir, name)
    print(f'\nYour project {name} in {lang} will be created at {path}\n')
    print(Fore.YELLOW)
    click.confirm('Do you want to continue?', abort=True)
    create_program(name, lang, output_dir, config)


if __name__ == '__main__':
    colorama.init()
    print(Fore.WHITE)
    print("Let's create some starter files for your project!!!\n")
    print(Fore.BLUE)
    get_user_input()
    print(Style.RESET_ALL)
