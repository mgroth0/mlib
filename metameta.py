from mlib.file import File, strippedlines

def metameta():

    VERSION = '0.0.44'
    # bumpversion
    NEW_VERSION = '0.0.'+str(int(VERSION.split('.')[2])+1)
    File(__file__).write(File(__file__).read().replace(
        f'{VERSION}', f'{NEW_VERSION}'
    ))

    reqs = strippedlines("reqs_conda.txt").filtered(
        lambda lin: not lin.startswith("#"),
        lambda lin: lin.split('=')[0] in strippedlines('reqs_conda_top.txt')
    ).map(
        lambda lin: ' =='.join(lin.split("=")[0:2])
    )

    # version = strippedlines('.bumpversion.cfg').first(
    #     lambda lin: lin.startswith('current_version')
    # ).split('=')[1].strip()

    File('meta.yaml').save(dict(
        package=dict(name='mlib-mgroth0', version=NEW_VERSION),
        source={'path': '.'},
        build={'script': 'python -m pip install --no-deps --ignore-installed .'},
        requirements={
            'build': [
                'python',
                'pip'  # requires setuptools which reqs wheel
            ],
            'run'  : reqs.tolist()
        },

        # having this section means creating a test env
        # removing this seciton avoids creating a test env completely
        test={'imports': 'mlib'}
    ))

    File('setup.py').write(
        '''
            
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
name="mlib-mgroth0",
version="''' + NEW_VERSION + '''",
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
    
        
    '''
    )
