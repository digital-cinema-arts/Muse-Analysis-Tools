from setuptools import setup, find_packages

setup(
    name="Muse-Analysis-Tools",
    version="0.1",
    include_package_data=True, 

    scripts=['src/analyze_muse_data.py'],

    install_requires=['docutils>=0.3'],
    zip_safe=True,

#     package_data={
#         'resources': ['resources/resources_rc.py']
#         },
        
        # If any package contains *.txt or *.rst files, include them:
#         '': ['*.txt', '*.rst'],

    requires=['time', 'datetime', 'numpy', 'scipy', 'pandas', 'math',
                'bitstring', 'os', 'sys', 'csv', 'argparse', 'tqdm', 
                'json', 'pathlib', 'pandas.plotting', 'matplotlib', 
                'PyQt5', 'resources_rc'],


#      package_dir={
#                 "gui": "myApp/gui",
#                 "logic": "myApp/logic",
#                 },

      data_files=[
          ('resources', ['resources/resources_rc.py']),
          ('icons', ['resources/icons/ABCS.ico'])
      ],
      

     long_description="""\

# Muse-Analysis-Tools
 
## Algorithmic Biofeedback Control System - Chart Tools

This script will generate a number of charts from Muse headband EEG CSV data files created by the Mind Monitor app.  Future versions of these tools will support Muse Direct and Muse Lab files.

    """,

    author="Debra Grace Peri",
    author_email="debragraceperi@gmail.com",
    description="This package contains code for graphing Muse EEG data",
    keywords="Muse EEG",
    url="https://github.com/digital-cinema-arts/Muse-Analysis-Tools/", 

    project_urls={
        "Bug Tracker": "https://github.com/digital-cinema-arts/Muse-Analysis-Tools/issues",
        "Documentation": "https://github.com/digital-cinema-arts/Muse-Analysis-Tools/wiki",
        "Source Code": "https://github.com/digital-cinema-arts/Muse-Analysis-Tools",
    },


      classifiers=[
         "Development Status :: 5 - Production/Stable",
         "Topic :: Utilities",
        'License :: GNU Affero General Public License v3.0'
    ]


)


