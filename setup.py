from setuptools import setup
from my_pkg import constants
from os import path

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md')) as f:
    long_description = f.read()

setup(
    name='pyMyTinyTodo',
    version=1.7,
    description='Simple way to manage todo list in AJAX style',
    author='Asderty Treds',
    author_email='asderty@atreds.pw',
    url='http://github.com/AsdertyTreds/pyMyTinyTodo',
    packages=[
        'pyMyTinyTodo',
    ],
    long_description=long_description,
    long_description_content_type='text/markdown',
    include_package_data=True,
    install_requires=[],
    python_requires='>=3.7',
    classifiers=[
        "License :: OSI Approved :: GNU GPL",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Topic :: Software Development :: Libraries"],
    package_data={
        '': ['*.md', '*.txt', '*.json']
    },
    keywords='pyMyTinyTodo',
    license='GPL',
)