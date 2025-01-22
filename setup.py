from setuptools import setup, find_packages

# Read the README file for the long description (optional but recommended)
with open('README.md') as f:
    long_description = f.read()

setup(
    name='Distrohaven',           # The name of your program/package
    version='1.0.0',                    # The version of your program/package
    packages=find_packages(),           # Automatically discover packages
    include_package_data=True,          # Include non-Python files (e.g., assets)
    install_requires=[                  # List of dependencies
        'certifi==2024.12.14',          # via requests
        'charset-normalizer==3.4.1',    # via requests
        'customtkinter==5.2.2',         # via -r requirements.in
        'darkdetect==0.8.0',            # via customtkinter
        'idna==3.10',                   # via requests
        'packaging==24.2',              # via customtkinter
        'pillow==11.1.0',               # via -r requirements.in
        'requests==2.32.3',             # via -r requirements.in
        'urllib3==2.3.0',               # via requests
    ],
    entry_points={                      # Define entry points if you have CLI tools
        'console_scripts': [
            'my_program = bin.main:main',  # Entry point: bin.main is the module, main is the function
        ],
    },
    package_data={                      # Include non-Python files (e.g., assets, config files)
        'my_python_program': [
            'assets/*',
        ],
    },
    data_files=[                        # For non-package data like config files
        ('/etc/my_python_program', ['config.json']),
    ],
    long_description=long_description,  # Detailed description shown on PyPI or elsewhere
    long_description_content_type='text/markdown',
    classifiers=[                       # Classifiers for PyPI and distribution
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.13.0',           # Specify supported Python version (3.13.0 or higher)
    author='Adison',                 # Author of the package
    author_email='adison.negron@gmail.com',  # Author's contact email
    description='A Python program to browse and save images from Wallhaven through the Wallhaven API. Next updates will add commands to edit/set wallpaper through commands',  # Short description
)