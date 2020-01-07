from setuptools import setup, find_packages
import os, sys, codecs, re

with open("README.md", "r") as fh:
    long_description = fh.read()


# here = os.path.abspath(os.path.dirname(__file__))

# def read(*parts):
#     with codecs.open(os.path.join(here, *parts), 'r') as fp:
#         return fp.read()

# def find_version(*file_paths):
#     version_file = read(*file_paths)
#     version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
#                               version_file, re.M)
#     if version_match:
#         return version_match.group(1)
#     raise RuntimeError("Unable to find version string.")

this_version = {}
with open("./analyze_muse/version.py", "r") as fh:
    this_version = fh.read()
 
print("\n") 
print("VBuilding ersion: ", this_version)
print("\n") 
    
setup(
    name="Muse-Analysis-Tools",
#     version="1.1.3",
#     version=find_version("analyze_muse", "__init__.py"),
    version=this_version,

    author="debra_peri",
#    author="Debra Grace Peri",
    author_email="debragraceperi@gmail.com",

    description="This package contains code for graphing Muse EEG data",
    keywords="Muse EEG",

    long_description=long_description,
    long_description_content_type="text/markdown",

    url="https://github.com/digital-cinema-arts/Muse-Analysis-Tools/", 

    packages=find_packages(),

    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Development Status :: 5 - Production/Stable",
        "Topic :: Utilities",
        "License :: GNU Affero General Public License v3.0",
    ],
    python_requires='>=3.6',

    include_package_data=True, 

    scripts=['analyze_muse/analyze_muse_data.py'],

    install_requires=['docutils>=0.3'],
    zip_safe=True,

    requires=['time', 'datetime', 'numpy', 'scipy', 'pandas', 'math', 'h5py', 'tables',
                    'bitstring', 'os', 'sys', 'csv', 'argparse', 'progress', 'filetype',
                    'json', 'pathlib', 'pandas.plotting', 'matplotlib', 
                    'PyQt5'],
                
     package_data={
         'resources': ['analyze_muse/resources/resources_rc.py']
         },
        
     data_files=[
          ('resources', ['analyze_muse/resources/resources_rc.py']),
          ('icons', ['analyze_muse/resources/ABCS.ico'])
      ],

   project_urls={
       "Bug Tracker": "https://github.com/digital-cinema-arts/Muse-Analysis-Tools/issues",
       "Documentation": "https://github.com/digital-cinema-arts/Muse-Analysis-Tools/wiki",
       "Source Code": "https://github.com/digital-cinema-arts/Muse-Analysis-Tools",
   },

)


