
            
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
name="mlib-mgroth0",
version="0.0.48",
author="Matt Groth",
author_email="mjgroth@mit.edu",
description="Matt's lib",
long_description=long_description,
long_description_content_type="text/markdown",
url="https://github.com/mgroth0/mlib",
packages=setuptools.find_packages(),
classifiers=[
"Programming Language :: Python :: 3.8",
"License :: OSI Approved :: MIT License",
"Operating System :: MacOS :: MacOS X",
],
python_requires='>=3.8',
)
    
        
    