def list_reqs():

    with open('reqs_conda_top.txt', 'r') as f:
        t = f.read()
        lines = t.split('\n')
        lines = list(filter(lambda l: not l.strip() == '', lines))
        tops = lines

    reqs = []
    # with open("reqs_pip.txt", "r") as f:
    #     for line in f.read().split('\n'):
    #         if len(line.strip())==0: continue
    #         reqs.append(line.strip())
    with open("reqs_conda.txt", "r") as f:
        for line in f.read().split('\n'):
            if line.startswith("#"): continue
            if len(line.strip())==0: continue
            short = line.strip().split('=')[0]
            if short not in tops: continue
            reqs.append(' =='.join(line.strip().split("=")[0:2]))
    return reqs
reqs = '\n    - ' + '\n    - '.join(list_reqs()) + '\n'

with open('.bumpversion.cfg','r') as f:
    t = f.read()
    for line in t.split('\n'):
        if line.strip().startswith('current_version'):
            version = line.split('=')[1].strip()

with open('meta.yaml','w') as f:
    f.write('''
package:
  name: mlib-mgroth0
  version: '''+version+'''
source:
  path: .
requirements:
  build:
    - python
    - pip #requires setuptools which reqs wheel
  run:
'''+reqs+'''
# having this section means creating a test env
# removing this seciton avoids creating a test env completely
test:
  imports:
    - mlib
''')