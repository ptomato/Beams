# Inspired by
# http://www.jeffknupp.com/blog/2013/08/16/open-sourcing-a-python-project-the-right-way/

from setuptools import setup
import io

import beams

def read(*filenames, **kwargs):
    encoding = kwargs.get('encoding', 'utf-8')
    sep = kwargs.get('sep', '\n')
    buf = []
    for filename in filenames:
        with io.open(filename, encoding=encoding) as f:
            buf.append(f.read())
    return sep.join(buf)

long_description = read('README')

setup(
    name='Beams',
    version=beams.__version__,

    packages=['beams'],
    include_package_data=True,
    entry_points={
        'gui_scripts': ['beams = beams.MainWindow:main'],
    },
    install_requires=[
        'traits >= 4',
        'traitsui >= 4',
        'pyface >= 4',
        'chaco >= 4',
        'scipy >= 0.11',
    ],
    platforms='any',

    # Metadata
    author='Philip Chimento',
    author_email='philip.chimento@gmail.com',
    url='http://ptomato.name/opensource/beams/beams.html',
    description='Laser beam profiling software designed for cheap webcams',
    long_description=long_description,
    license='MIT License',
    classifiers=[
        'Programming Language :: Python',
        'Development Status :: 4 - Beta',
        'Natural Language :: English',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Scientific/Engineering :: Physics',
        'Topic :: Scientific/Engineering :: Visualization',
        'Topic :: Multimedia :: Video :: Capture',
    ],
)
