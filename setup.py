from setuptools import setup, find_packages

setup(
    # Application name:
    name="pydofus2",
    
    # Version number (initial):
    version=open("./VERSION").read(),
    
    # Application author details:
    author="majdoub khalid",
    author_email="majdoub.khalid@gmail.com",
    
    # Packages
    packages=find_packages(),
    
    # Include additional files into the package
    include_package_data=True,
    data_files=[('pydofus2', ['pydofus2/*.json', 'pydofus2/binaryData/*.bin'])],
    
    # Details
    url="http://pypi.python.org/pypi/pydofus2_v100/",
    
    #
    # license="LICENSE.txt",
    description="Light python client for dofus2 offi.",
    
    # long_description=open("README.txt").read(),
    
    # Dependent packages (distributions)
    install_requires= open("./requirements.txt").readlines()
)