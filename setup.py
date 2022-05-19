from setuptools import setup
import pathlib

# Import dependencies from base requirements file. This centralizes requirements and helps bring
# order to Python's fragmented packaging system. Any extra environment-specific dependencies, such
# as those for dev, testing, etc., should be placed in discrete requirements files to be used in a
# manual pip install by the developers.
_install_requires = list()
_requirements_common_file = pathlib.Path(__file__).parent / 'requirements' / 'common.txt'
if _requirements_common_file.exists() and _requirements_common_file.is_file():
    try:
        _install_requires = [
            line_string for line_string
            in _requirements_common_file.read_text().split('\n')
            if line_string
        ]
    except OSError:
        _warning_string = 'Warning: requirements file "{file_path!s}" exists but could not be read.'
        _warning_string = _warning_string.format(file_path=_requirements_common_file)
        print(_warning_string)

setup(
   name='bird_guide_creator',
   version='15.9',
   description='Makes bird guides for phone music player.',
   author='DCS',
   author_email='jawwolfe@gmail.com',
   packages=['bird_guide_creator'],
   install_requires=_install_requires
)
