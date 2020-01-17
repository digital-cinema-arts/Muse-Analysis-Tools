from setuptools import setup, find_packages, find_namespace_packages
import os, sys

with open("README.md", "r") as fh:
    long_description = fh.read()

this_version = {}
with open("./analyze_muse/ABCS_version.py", "r") as fh:
    this_version = fh.read()
    this_version =  this_version[14:len(this_version)-2]

# ABCS_version='1.1.9'

print("\n") 
print("Building Version: ", this_version)
print("find_packages: ", find_packages())
print("find_namespace_packages: ", find_namespace_packages())
print("\n") 

 
setup(
    name="Muse-Analysis-Tools",
#     version="1.1.3",
    version=this_version.rstrip(),

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
#        "License :: GNU Affero General Public License v3.0",
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


