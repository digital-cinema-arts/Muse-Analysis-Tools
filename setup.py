from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="Muse-Analysis-Tools",
    version="1.0.3",


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
#    zip_safe=True,

     package_data={
         'resources': ['analyze_muse/resources/resources_rc.py']
         },
        
     data_files=[
#          ('resources', ['resources/resources_rc.py']),
          ('resources', ['analyze_muse/resources/resources_rc.py']),
          ('icons', ['analyze_muse/resources/ABCS.ico'])
      ],

#    project_urls={
#        "Bug Tracker": "https://github.com/digital-cinema-arts/Muse-Analysis-Tools/issues",
#        "Documentation": "https://github.com/digital-cinema-arts/Muse-Analysis-Tools/wiki",
#        "Source Code": "https://github.com/digital-cinema-arts/Muse-Analysis-Tools",
#    },

)

