from setuptools import setup, find_packages

setup(
    # Application name:
    name="pydofus2",
    
    # Version number (initial):
    version="1.0.0",
    
    # Application author details:
    author="majdoub khalid",
    author_email="majdoub.khalid@gmail.com",
    
    # Packages
    packages=find_packages(),
    
    # Include additional files into the package
    include_package_data=True,

    # Details
    url="http://pypi.python.org/pypi/pydofus2_v100/",
    
    #
    # license="LICENSE.txt",
    description="Useful towel-related stuff.",
    
    # long_description=open("README.txt").read(),
    
    # Dependent packages (distributions)
    install_requires=[
        "pycryptodomex",
        "whistle",
        "Py3AMF",
        "httpx[http2]",
        "xmltodict",
        "lxml"
    ],
)