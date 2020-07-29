from mlib.proj.struct import Project
from mlib.web.html import HTMLPage, Hyperlink, HTMLImage
SKIPPED_SOURCE = [
    '@log_invokation',
    'global DOC',
    '@staticmethod'
]

def scipy_doc_url(funname): return f'https://docs.scipy.org/doc/scipy/reference/generated/{funname}.html'

FUN_LINKS = {
    'bilinear': 'https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.bilinear.html'
}

FUN_LINKS.update(
    {fun.split('.')[-1]: scipy_doc_url(fun) for fun in [
        'scipy.signal.filtfilt',
        'scipy.signal.lfilter',
        'scipy.signal.butter'
    ]}
)


def ShadowIndex(*pages):
    return HTMLPage(
        'index',
        *[Hyperlink(page.rootpath, f"{page.rootpath}/{page.name}.html") for page in pages],
        HTMLImage(Project.PYCALL_FILE, fix_abs_path=True),
        HTMLImage(Project.PYDEPS_OUTPUT, fix_abs_path=True)
    )
