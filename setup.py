import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()
def list_reqs():
    reqs = []
    with open("reqs_pip.txt", "r") as f:
        for line in f.read().split('\n'):
            if len(line.strip())==0: continue
            reqs.append(line.strip())
    with open("reqs_conda.txt", "r") as f:
        for line in f.read().split('\n'):
            if line.startswith("#"): continue
            if len(line.strip())==0: continue
            reqs.append('=='.join(line.strip().split("=")[0:2]))
    return reqs
setuptools.setup(
    name="mlib-mgroth0",
    version="0.0.27",
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
    install_requires=list_reqs()
    # use_incremental=True,
    # setup_requires=['incremental'],
    # install_requires=['incremental']  # along with any other install dependencies
)
