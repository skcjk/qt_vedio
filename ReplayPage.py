import os
from PyQt6 import QtCore
from qframelesswindow.webengine import FramelessWebEngineView


class ReplayViwer(FramelessWebEngineView):
 
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName("replayViewer")
 
        self.settings().setAttribute(self.settings().WebAttribute.ShowScrollBars, False)
        self.settings().setAttribute(self.settings().WebAttribute.WebGLEnabled, True)
        self.settings().setAttribute(self.settings().WebAttribute.LocalContentCanAccessRemoteUrls, True)  # 启用跨域请求
        self.set_html()
 
        self.setWindowTitle("回放")

    def set_html(self):
        path = "file:\\" + os.getcwd() + "\\replay.html"
        path = path.replace('\\', '/')
        self.load(QtCore.QUrl(path))

    def refresh_page(self):
        self.reload()

    def sizeHint(self) -> QtCore.QSize:
        return QtCore.QSize(200, 200)
    





