from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal, QObject, Qt
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtWidgets import QMainWindow, QWidget, QGridLayout, QLabel, QPushButton, QLineEdit, QApplication

from mlib.boot.mlog import log

# spec = importlib.util.spec_from_file_location("breeze_resources",
#                                               "/Users/matt/Desktop/BreezeStyleSheets/breeze_resources.py")
# foo = importlib.util.module_from_spec(spec)
# spec.loader.exec_module(foo)
from mlib.term import log_invokation


palette = QPalette()
palette.setColor(QPalette.Window, QColor(0, 0, 0))
palette.setColor(QPalette.WindowText, Qt.white)
palette.setColor(QPalette.Base, Qt.blue)
# palette.setColor(QPalette.QLabel, Qt.white)
palette.setColor(QPalette.AlternateBase, Qt.yellow)
palette.setColor(QPalette.ToolTipBase, Qt.yellow)
palette.setColor(QPalette.ToolTipText, Qt.yellow)
palette.setColor(QPalette.Text, Qt.yellow)
palette.setColor(QPalette.Button, QColor(0, 0, 50))
palette.setColor(QPalette.ButtonText, Qt.white)
palette.setColor(QPalette.BrightText, Qt.yellow)
palette.setColor(QPalette.Link, Qt.yellow)
palette.setColor(QPalette.Highlight, Qt.yellow)
palette.setColor(QPalette.HighlightedText, Qt.yellow)
MAIN_QPALETTE = palette



class SimpleApp(QApplication):
    start_worker_sig = pyqtSignal()
    def __init__(self,
                 *args,
                 title="Insert Title Here",
                 label="Insert Label here",
                 background_fun=None,
                 fullscreen=True,
                 always_on_top=False,
                 no_title_bar=False,
                 **kwargs
                 ):
        super().__init__(*args, **kwargs)
        # app.setStyle("Default")
        # app.setStyle("Universal")
        self.setStyle("Fusion")
        # app.setStyle("Material")






        # Now use a palette to switch to dark colors:




        self.setPalette(palette)

        self.win = HelloWindow(title=title, label=label, fullscreen=fullscreen, always_on_top=always_on_top,
                               no_title_bar=no_title_bar)

        self.input = self.win.input
        self.text = self.win.text
        self.button = self.win.button

        self.worker_thread = None
        self.update_fun = None
        if background_fun is not None:
            class WorkerObject(QObject):
                sig = pyqtSignal(str)
                @QtCore.pyqtSlot()
                def startWork(self):
                    background_fun(self.sig)
            self.worker = WorkerObject()
            self.worker_thread = QtCore.QThread()
            self.worker.moveToThread(self.worker_thread)
            self.worker.sig.connect(self.update)
            self.start_worker_sig.connect(self.worker.startWork)
            # class Runnable(QThread):
            # C magic forces sig to be defined as a class attribute here
            # sig = pyqtSignal()
            # def run(self):
            #     background_fun(self.sig)
            # self.runnable = Runnable()
    @QtCore.pyqtSlot(str)
    def update(self, s):
        # @log_invokation
        log('invoking update')
        if self.update_fun is not None:
            log('update fun is not none')
            self.update_fun(s)
            log('actually passed update fun')

    # override
    @log_invokation
    def exec(self):
        if self.worker_thread is not None:
            log('starting worker')
            # self.runnable.finished.connect(app.exit)
            self.worker_thread.start()
            self.start_worker_sig.emit()
            # QThreadPool.globalInstance().start(self.runnable)
        log('showing win')
        self.win.show()
        log('really executing app')
        return super().exec()



    def quit(self):
        #     weird fullscreen ghost is not closing. hopefully this will help.
        self.win.showNormal()

        def realQuit():
            self.win.close()
            # self.app.quit() #prevents running another app on the same run

        # time.sleep(1) #looks like this is neccesary too...
        QtCore.QTimer.singleShot(1000, realQuit)

        # return
    close = quit










class HelloWindow(QMainWindow):
    def __init__(self, title, label, fullscreen=True, always_on_top=False, no_title_bar=False):
        # QMainWindow.__init__(self)
        # super().__init__(flags, *args, **kwargs)
        flags = []
        args = ()
        kwargs = {}

        flags = 0
        flags = None
        if no_title_bar:
            if flags is None:
                flags = QtCore.Qt.CustomizeWindowHint
            else:
                flags = flags | QtCore.Qt.CustomizeWindowHint
            # pass
        if always_on_top:
            if flags is None:
                flags = QtCore.Qt.WindowStaysOnTopHint
            else:
                flags = flags | QtCore.Qt.WindowStaysOnTopHint
            # flags = flags + QtCore.Qt.WindowStaysOnTopHint
            # pass
            # super().__init__(None, QtCore.Qt.WindowStaysOnTopHint)
            # super(w).__init__(None, QtCore.Qt.X11BypassWindowManagerHint)
        # else:
        super().__init__(None, flags)
        # self.setWindowFlags(QtCore.Qt.WindowFlags(QtCore.Qt.CustomizeWindowHint,QtCore.Qt.WindowStaysOnTopHint))
        # super().__init__(None,  QtCore.Qt.WindowStaysOnTopHint)

        # self.setMinimumSize(QSize(640, 480))
        # set stylesheet
        # CAUSED BUTTONS TO NOT WORK
        # file = QFile("/Users/matt/Desktop/BreezeStyleSheets/dark.qss")


        # file = QFile(":/dark.qss")
        # file.open(QFile.ReadOnly | QFile.Text)
        # stream = QTextStream(file)
        # CAUSED BUTTONS TO NOT WORK
        # self.setStyleSheet(stream.readAll())









        self.setWindowTitle(title)

        centralWidget = QWidget(self)
        self.setCentralWidget(centralWidget)

        self.cw = centralWidget

        gridLayout = QGridLayout(centralWidget)
        centralWidget.setLayout(gridLayout)

        self.gridLayout = gridLayout

        self.next = 0

        self.label = self.text(label)

        import AppKit
        screen_sizes = [(screen.frame().size.width, screen.frame().size.height)
                        for screen in AppKit.NSScreen.screens()]
        # will give you a list of tuples containing all screen sizes (if multiple monitors present)
        w = screen_sizes[0][0]
        h = screen_sizes[0][1]

        self.setFixedSize(w, h)

        if fullscreen:
            self.showFullScreen()
        else:
            self.setFixedSize(w, h - 45)
    def text(self, txt=""):
        txt = QLabel(txt, self.cw)
        txt.setPalette(MAIN_QPALETTE)
        txt.setAlignment(QtCore.Qt.AlignCenter)
        self.gridLayout.addWidget(txt, self.next, 0)
        self.next += 1
        return txt

    def button(self, text, fun):
        button = QPushButton(text, self.cw)
        button.setPalette(MAIN_QPALETTE)
        button.clicked.connect(fun)
        self.gridLayout.addWidget(button, self.next, 0)
        self.next += 1

    def input(self, initial=""):
        textInput = QLineEdit(self.cw)
        textInput.setText(initial)
        textInput.setPalette(MAIN_QPALETTE)
        # button.clicked.connect(self.plswork)
        self.gridLayout.addWidget(textInput, self.next, 0)
        self.next += 1
        return textInput

    def pane(self):
        box = QWidget(self)
        layout = QGridLayout()
        box.setLayout(layout)
        # button.clicked.connect(self.plswork)
        self.gridLayout.addWidget(box, self.next, 0)
        self.next += 1
        return layout
