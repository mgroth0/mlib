# noinspection PyUnresolvedReferences
import readline
import sys

from mlib.boot import log
from mlib.boot.mutil import err
from mlib.km import activateIdea

def YesOrNo(q):
    response = answer_request('', q, None, False)
    if response == 'y':
        return True
    elif response == 'n':
        return False
    else:
        err(f'invalid response: {response}')

def answer_request(default, q, check, gui=True):
    to_return = {'r': None}
    if gui:
        app = SimpleApp(sys.argv, title="answer request", label=q, fullscreen=False)
        textInput = app.input(default)
        status = app.text()
    def fun(answer):
        log('hit button')
        if gui:
            folName = textInput.text()
        else:
            folName = answer
        if check is not None:
            r, figs_folder = check(folName)
        else:
            r = True
            figs_folder = folName
        if r:
            to_return['r'] = figs_folder
            if gui:
                app.close()
        else:
            if gui:
                status.setText(figs_folder)
            else:
                print(figs_folder)

    if gui:
        app.button("Submit", fun)
        app.exec()
    else:
        while to_return['r'] is None:
            readline.set_startup_hook(lambda: readline.insert_text(default))
            try:
                answer = input(q)
                fun(answer)
            finally:
                readline.set_startup_hook()

    if gui:
        activateIdea()
    return to_return['r']
