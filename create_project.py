import click
import colorama
import jinja2
import os

from colorama import Back
from colorama import Fore
from colorama import Style


class ExpandedPath(click.Path):
    def convert(self, value, *args, **kwargs):
        value = os.path.expanduser(value)
        return super(ExpandedPath, self).convert(value, *args, **kwargs)


def render_template(template_path, context):
    path, filename = os.path.split(template_path)
    return jinja2.Environment(
            loader=jinja2.FileSystemLoader(path or './')).get_template(filename).render(context)


def get_c_config(name):
    config = {}
    if click.prompt("Do you want to add your libft?", type=bool):
        config['libft_path'] = os.path.abspath(os.path.expanduser(click.prompt('Please enter the path to your libft',
                type=ExpandedPath(exists=True, file_okay=False, dir_okay=True))))
    if click.prompt(f'Do you want a "{name}.c" file?', type=bool):
        config['main'] = name + '.c'
    elif click.prompt("Do you want a 'main.c' file?", type=bool):
        config['main'] = 'main.c'
    if click.prompt("Create a author file?", type=bool):
        config['author'] = click.prompt("Input your username:", type=str)
    return config


def get_py_config(name):
    config = {}
    if click.prompt("Do you want a virtualenv?", type=bool):
        config['venv'] = True
    if click.prompt("Install dependencies(requirements.txt)?", type=bool):
        config['depend'] = os.path.abspath(os.path.expanduser(
            click.prompt('Please enter the path to your requirements.txt',
                type=ExpandedPath(exists=True, file_okay=True, dir_okay=False))))
    return config


def create_program(name, lang, output_dir, config=None):
    pass


@click.command()
@click.option('--name', '-n',
        prompt='What do you want to call your project?',
        help='Name of your project')
@click.option('--lang', '-l', type=click.Choice(['c', 'py']),
    prompt='Which language is your project in [c/py]?',
    help='Which language is your project in[c/python]?')
@click.option('--output_dir', type=click.Path(exists=True,
    file_okay=False, dir_okay=True, resolve_path=True), default='./')
def get_user_input(name, lang, output_dir):
    path = os.path.join(output_dir, name)
    print(Fore.GREEN)
    if lang == 'c':
        config = get_c_config(name)
    elif lang == 'py':
        config = get_py_config(name)
    print()
    for k, v in config.items():
        print(f"\t{k} : {v}")
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
