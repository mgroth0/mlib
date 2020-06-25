import json
import subprocess

def conda_prune():

    # sometimes there are circular deps because of older versions. I'll just have to 'stop'


    with open('reqs_conda_top.txt', 'r') as f:
        t = f.read()
        lines = t.split('\n')
        lines = list(filter(lambda l: not l.strip() == '', lines))
        tops = lines
    with open('reqs_conda_sub.txt', 'r') as f:
        t = f.read()
        lines = t.split('\n')
        lines = list(filter(lambda l: not l.strip() == '', lines))
        subs = lines

    with open('reqs_conda_cache.json', 'r') as f:
        t = f.read()
        cache = json.loads(t)

    stop = False

    checking = []

    def check(req):
        my_req_short = req.split('=')[0]
        if req in checking:
            # handles when a package is a sub twice and recursives
            print(f'already checking {my_req_short}')
            return
        global stop
        checking.append(req)
        print(f'checking: {my_req_short}')
        if line in list(cache.keys()):
            print(f'getting search result for {line} from cache')
            result = cache[line]
        else:
            print(f'searching {line}')
            raw = subprocess.Popen(
                [
                    'conda',
                    'search',
                    line,
                    '--info'
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT
            ).communicate()[0]
            result = raw.decode('utf-8')
            cache[line] = result

        dep_line = False
        deps = []
        for lin in result.split('\n'):
            if stop:
                break
            if lin.startswith('dependencies'):
                dep_line = True
                continue
            if dep_line:
                if lin.strip() == '':
                    # sometimes search returns multiple results
                    break
                else:
                    long_dep = lin.split('-')[1].strip()
                    deps.append(
                        long_dep.split(' ')[0]
                    )
                    # long_dep = long_dep.replace(' ', '')

        for d in deps:
            if d in tops:
                print(f'{d} is top')
            elif d in subs:
                print(f'{d} is sub')
            else:
                print(f'{my_req_short} depends on {d}')
                my_a = input('top?sub?stop? > ')
                if my_a == 'top':
                    print('adding top')
                    tops.append(d)
                elif my_a == 'sub':
                    print(f'recursing into {d}')
                    check(d)
                    print('adding sub')
                    subs.append(d)
                elif my_a == 'stop':
                    stop = True
                    break

        if len(deps) == 0:
            print(f'{my_req_short} has 0 deps')


    with open('reqs_conda.txt', 'r') as f:
        t = f.read()
        lines = t.split('\n')
        lines = list(filter(lambda l: not l.strip().startswith('#'), lines))
        lines = list(filter(lambda l: not l.strip() == '', lines))

        for line in lines:
            if stop:
                break
            line = line.strip()
            check(line)

        for line in lines:
            if stop:
                break
            req_short = line.split('=')[0].strip()
            if req_short not in tops and req_short not in subs:
                print(f'never answered for {req_short}')
                a = input('top?sub?stop? > ')
                if a == 'top':
                    print('adding top')
                    tops.append(req_short)
                elif a == 'sub':
                    print('adding sub')
                    subs.append(req_short)
                elif a == 'stop':
                    stop = True
                    break

    new_tops = '\n'.join(set(tops)) + '\n'
    with open('reqs_conda_top.txt', 'w') as f:
        f.write(new_tops)
    new_subs = '\n'.join(set(subs)) + '\n'
    with open('reqs_conda_sub.txt', 'w') as f:
        f.write(new_subs)

        # new_t = '\n'.join(lines) + '\n'
    # with open('reqs_conda.txt', 'w') as f:
    #     f.write(new_t)

    with open('reqs_conda_cache.json', 'w') as f:
        f.write(json.dumps(cache))
