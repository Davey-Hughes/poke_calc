import setuptools

with open("README.md", "r") as f:
    long_description = f.read()

setuptools.setup(
    name='daveyhughes',
    version='0.1.1',
    author='David Hughes',
    author_email='davidralphhughes@gmail.com',
    description='A python interface for using the Smogon damage calculator',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/Davey-Hughes/poke_calc',
    packages=setuptools.find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
