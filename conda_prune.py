from mlib.boot import log
from mlib.boot.mutil import err
from mlib.file import strippedlines, load, File
from mlib.shell import spshell
def conda_prune():
    # sometimes there are circular deps because of older versions. I'll just have to 'stop'
    tops = strippedlines('reqs_conda_top.txt').tolist()
    subs = strippedlines('reqs_conda_sub.txt').tolist()
    cache = load('reqs_conda_cache.json')
    stop = False
    skipped = False
    checking = []
    def check(req):
        my_req_short = req.split('=')[0]
        if req in checking:
            # handles when a package is a sub twice and recursives
            log(f'already checking {my_req_short}')
            return
        stp = skped = False
        checking.append(req)
        log(f'checking: {my_req_short}')
        if line in list(cache.keys()):
            log(f'getting search result for {line} from cache')
            result = cache[line]
        else:
            log(f'searching {line}')
            result = spshell([
                'conda',
                'search',
                line,
                '--info'
            ]).all_output()
            cache[line] = result

        dep_line = False
        deps = []
        for lin in result.split('\n'):
            if stp:
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
                log(f'{d} is top')
            elif d in subs:
                log(f'{d} is sub')
            else:
                log(f'{my_req_short} depends on {d}')
                my_a = input('top?sub?stop/skip? > ')
                if my_a == 'top':
                    log('adding top')
                    tops.append(d)
                elif my_a == 'sub':
                    log(f'recursing into {d}')
                    stp, skp = check(d)
                    if skp:
                        skped = True
                    log('adding sub')
                    subs.append(d)
                elif my_a == 'stop':
                    stp = True
                    break
                elif my_a == 'skip':
                    skped = True
                else:
                    err('bad answer')

        if len(deps) == 0:
            log(f'{my_req_short} has 0 deps')

        return stp, skped


    lines = strippedlines('reqs_conda.txt').filtered(
        lambda l: not l.strip().startswith('#')
    )

    for line in lines:
        if stop: break
        stop,skp = check(line)
        if skp:
            skipped=True

    for line in lines:
        if stop:
            break
        req_short = line.split('=')[0].strip()
        if req_short not in tops and req_short not in subs:
            log(f'never answered for {req_short}')
            a = input('top?sub?stop/skip? > ')
            if a == 'top':
                log('adding top')
                tops.append(req_short)
            elif a == 'sub':
                log('adding sub')
                subs.append(req_short)
            elif a == 'stop':
                stop = True
                break
            elif a == 'skip':
                skipped = True
            else:
                err('bad answer')

    File('reqs_conda_top.txt').write_lines(set(tops))
    File('reqs_conda_sub.txt').write_lines(set(subs))
    File('reqs_conda_cache.json').save(cache)

    return not stop and not skipped
