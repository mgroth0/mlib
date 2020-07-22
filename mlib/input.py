import argparse
def boolinput(q):
    from mlib.proj.struct import Project
    if Project.INPUT_FILE.exists:
        for line in Project.INPUT_FILE.readlines():
            p = line.split('=')[0]
            if q.startswith(p):
                return bool(line.split('=')[1].strip())
    a = ''
    while a.upper() not in ['Y', 'N']:
        a = input(f'{q}? (y/n) > ').upper()
    return a == 'Y'
def strinput(q, choices):
    from mlib.proj.struct import Project
    if Project.INPUT_FILE.exists:
        lines = Project.INPUT_FILE.readlines()
        for line in lines:
            p = line.split('=')[0]
            if q.startswith(p):
                a = line.split('=')[1].strip()
                assert a in choices
                return a
    a = None
    while a not in choices:
        a = input(f'{q}? ({"/".join(choices)}) > ')
    return a


def margparse(**kwargs):
    parser = argparse.ArgumentParser()
    for key, value in kwargs.items():
        parser.add_argument(f'--{key}', type=value, required=True)
    FLAGS = parser.parse_args()
    print('EXECUTION ARGUMENTS: ' + str(FLAGS))
    return FLAGS
