import os, json
from PyQt6 import QtCore
from PyQt6.QtCore import Qt
from qframelesswindow.webengine import FramelessWebEngineView
from PyQt6.QtWebChannel import QWebChannel
from qfluentwidgets import (InfoBar, InfoBarPosition)

class UDPPortHandler(QtCore.QObject):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self._parent = parent

    @QtCore.pyqtSlot(str)
    def sendSuccess(self, message):
        try:
            data = json.loads(message)
            if isinstance(data, list):
                for item in data:
                    self.createCOMSuccessInfoBar(json.dumps(item, ensure_ascii=False))
            else:
                self.createCOMSuccessInfoBar(message)
        except json.JSONDecodeError:
            print("Invalid JSON received")

    @QtCore.pyqtSlot(str)
    def sendFailure(self, message):
        try:
            data = json.loads(message)
            if isinstance(data, list):
                for item in data:
                    self.createCOMErrorInfoBar(json.dumps(item, ensure_ascii=False))
            else:
                self.createCOMErrorInfoBar(message)
        except json.JSONDecodeError:
            print("Invalid JSON received")

    def createCOMSuccessInfoBar(self, portStr):
        InfoBar.success(
            title='已发送',
            content=portStr,
            orient=Qt.Orientation.Horizontal,
            isClosable=True,
            duration=5000,
            parent=self._parent.parent()
        )

    def createCOMErrorInfoBar(self, errorStr):
        InfoBar.error(
            title='错误',
            content=errorStr,
            orient=Qt.Orientation.Horizontal,
            isClosable=True,
            duration=5000, 
            parent=self._parent.parent()
        )

class WebViewer(FramelessWebEngineView):
 
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName("webViewer")
 
        self.settings().setAttribute(self.settings().WebAttribute.ShowScrollBars, False)
        self.settings().setAttribute(self.settings().WebAttribute.WebGLEnabled, True)
        self.settings().setAttribute(self.settings().WebAttribute.LocalContentCanAccessRemoteUrls, True)  # 启用跨域请求
        self.set_html()
 
        self.setWindowTitle("视频")

        # 设置WebChannel
        self.channel = QWebChannel(self.page())
        self.udpPortHandler = UDPPortHandler(self)
        self.channel.registerObject('udpPort', self.udpPortHandler)
        self.page().setWebChannel(self.channel)
 
    def set_html(self):
        path = "file:\\" + os.getcwd() + "\\index.html"
        path = path.replace('\\', '/')
        self.load(QtCore.QUrl(path))

    def refresh_page(self):
        self.reload()

    def sizeHint(self) -> QtCore.QSize:
        return QtCore.QSize(200, 200)








