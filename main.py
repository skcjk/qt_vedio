# coding:utf-8
import os
import sys
import subprocess

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication
from qfluentwidgets import (NavigationItemPosition, 
                            FluentWindow, FluentBackgroundTheme,
                            FluentTranslator)
from qfluentwidgets import FluentIcon as FIF
from common.config import cfg
from common.signal_bus import signalBus
from SettingUI import SettingInterface

from WebPage import WebViewer
from ReplayPage import ReplayViwer
from ffmpeg_stats import FFmpegStatsApp

# Window class inherits from FluentWindow and serves as the main application window
class Window(FluentWindow):

    def __init__(self):
        super().__init__()
        self.mediamtx_process = None
        self.initWindow()

        # create sub interface
        self.mainWindow = WebViewer(self)
        self.replayWindow = ReplayViwer(self)
        self.settingInterface = SettingInterface(self)

        signalBus.switchToSampleCard.connect(self.switchToSample)

        self.initNavigation()

    def initNavigation(self):
        self.addSubInterface(self.mainWindow, FIF.CONNECT, '主界面', NavigationItemPosition.SCROLL)
        self.addSubInterface(self.replayWindow, FIF.PLAY, '回放', NavigationItemPosition.SCROLL)
        # 页面刷新按钮
        self.navigationInterface.addItem(
            routeKey='refreshWebPage',
            icon=FIF.SYNC,
            text="刷新页面",
            onClick=self.mainWindow.refresh_page,
            selectable=False,
            tooltip="刷新页面",
            position=NavigationItemPosition.SCROLL
        )

        self.addSubInterface(self.settingInterface, FIF.SETTING, '设置', NavigationItemPosition.BOTTOM)

    def initWindow(self):
        """
        Initializes the main window properties such as size, title, icon, and position.

        Last modified: 2024-07-01 by 申凯诚
        """

        self.resize(1200, 1000)
        self.setWindowIcon(QIcon('./resource/logo.png'))
        self.setWindowTitle('标题')

        self.setMicaEffectEnabled(False)

        desktop = QApplication.screens()[0].availableGeometry() 
        w, h = desktop.width(), desktop.height()
        self.move(w//2 - self.width()//2, h//2 - self.height()//2)

        # use custom background color theme (only available when the mica effect is disabled)
        self.setCustomBackgroundColor(*FluentBackgroundTheme.DEFAULT_BLUE)

        self.show()
        QApplication.processEvents()
        self.startMediaMtx()

    def startMediaMtx(self):
        """ Start mediamtx.exe in a new thread """
        import threading
        def run_mediamtx():
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            self.mediamtx_process = subprocess.Popen(
            ["mediamtx.exe"],
            startupinfo=startupinfo, creationflags=subprocess.CREATE_NO_WINDOW
        )
        
        thread = threading.Thread(target=run_mediamtx)
        thread.daemon = True
        thread.start()

    def closeEvent(self, event):
        """ Handle window close event to terminate mediamtx.exe """
        if self.mediamtx_process:
            self.mediamtx_process.terminate()
            self.mediamtx_process.wait()
        event.accept()

    def switchToSample(self, routeKey, index):
        """ switch to sample """
        self.stackedWidget.setCurrentWidget(getattr(self, routeKey), False)
        
if __name__ == '__main__':

    # enable dpi scale
    if cfg.get(cfg.dpiScale) != "Auto":
        os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "0"
        os.environ["QT_SCALE_FACTOR"] = str(cfg.get(cfg.dpiScale))

    # create application
    app = QApplication(sys.argv)
    app.setAttribute(Qt.ApplicationAttribute.AA_DontCreateNativeWidgetSiblings)

    # internationalization
    locale = cfg.get(cfg.language).value
    translator = FluentTranslator(locale)

    app.installTranslator(translator)

    # create a new thread to run FFmpegStatsApp
    import threading
    def run_ffmpeg_stats_app():
        ffmpegStatsApp = FFmpegStatsApp()
        ffmpegStatsApp.start()

    ffmpeg_thread = threading.Thread(target=run_ffmpeg_stats_app)
    ffmpeg_thread.daemon = True
    ffmpeg_thread.start()

    # create main window
    w = Window()
    w.show()
    w.setWindowState(Qt.WindowState.WindowMaximized) #全屏最大化
    
    app.exec()
