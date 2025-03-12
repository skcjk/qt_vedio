import os
import json
import subprocess
from PyQt6 import QtCore
from PyQt6.QtWebChannel import QWebChannel
from qframelesswindow.webengine import FramelessWebEngineView
from SerialThread import serialThread

class FFmpegProcess:
    def __init__(self):
        self.ffmpeg_process = None
        # self.start_ffmpeg()

    def start_ffmpeg(self):
        """ Start ffmpeg process to push stream to rtsp """
        if self.ffmpeg_process is None:
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            ffmpeg_path = os.path.join(os.getcwd(), "ffmpeg", "bin", "ffmpeg.exe")
            self.ffmpeg_process = subprocess.Popen([
                ffmpeg_path, 
                '-f', 'h264', 
                '-i', 'pipe:0',
                '-c:v', 'copy', 
                '-rtsp_transport', 'tcp', 
                '-f', 'rtsp',
                'rtsp://localhost:8554/stream2',
            ], stdin=subprocess.PIPE, startupinfo=startupinfo, creationflags=subprocess.CREATE_NO_WINDOW)

    def stop_ffmpeg(self):
        """ Stop ffmpeg process """
        if self.ffmpeg_process:
            self.ffmpeg_process.terminate()
            self.ffmpeg_process.wait()
            self.ffmpeg_process = None

ffmpegProcess = FFmpegProcess() 

class SerialPortHandler(QtCore.QObject):
    @QtCore.pyqtSlot(str)
    def send(self, message):
        serialThread.send_data(f'{message}\r\n')
        try:
            command = json.loads(message)
            if command.get("command") == "start":
                ffmpegProcess.start_ffmpeg()
            elif command.get("command") == "stop":
                ffmpegProcess.stop_ffmpeg()
        except json.JSONDecodeError:
            print("Invalid JSON received")

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
        self.serialPortHandler = SerialPortHandler()
        self.channel.registerObject('serialPort', self.serialPortHandler)
        self.page().setWebChannel(self.channel)
        serialThread.dataReceived.connect(self.receivedSerialData)

        # 初始化双缓冲区：raw_buffer存原始数据，nalu_buffer存完整的nalu包
        self.raw_buffer = b''
        self.nalu_buffer = []  # 每个元素存储完整的nalu数据

        # 定时器以约30fps的速度发送nalu_buffer数据给FFmpeg
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.sendBufferData)
        self.timer.start(33)  # 33毫秒约等于 1/30秒
 
    def set_html(self):
        path = "file:\\" + os.getcwd() + "\\index.html"
        path = path.replace('\\', '/')
        self.load(QtCore.QUrl(path))

    def refresh_page(self):
        self.reload()

    def sizeHint(self) -> QtCore.QSize:
        return QtCore.QSize(200, 200)
    
    def receivedSerialData(self, data):
        # 将收到的数据累加到 raw_buffer 中，并尝试提取完整的nalu包
        if ffmpegProcess.ffmpeg_process is not None:
            self.raw_buffer += data
            
            start_code = b'\x00\x00\x00\x01'
            while True:
                # 若raw_buffer不足一个起始码的长度，则退出等待更多数据
                if len(self.raw_buffer) < len(start_code):
                    break
                # 如果raw_buffer不以起始码开头，则将前导非起始码数据移除
                if not self.raw_buffer.startswith(start_code):
                    pos = self.raw_buffer.find(start_code)
                    if pos != -1:
                        self.raw_buffer = self.raw_buffer[pos:]
                    else:
                        # 未找到起始码，清空缓冲区（可能为垃圾数据）
                        self.raw_buffer = b''
                        break
                # 尝试寻找下一个起始码，以确定一个完整的nalu包
                next_index = self.raw_buffer.find(start_code, len(start_code))
                if next_index != -1:
                    # 提取完整的nalu包
                    nalu = self.raw_buffer[:next_index]
                    self.nalu_buffer.append(nalu)
                    self.raw_buffer = self.raw_buffer[next_index:]
                else:
                    # 没找到下一个起始码，等待更多数据
                    break

    def sendBufferData(self):
        # 每1/30秒发送一次nalu_buffer内的所有nalu包给FFmpeg
        if ffmpegProcess.ffmpeg_process is not None and self.nalu_buffer:
            try:
                # 将所有nalu包拼接后发送
                data_to_send = b''.join(self.nalu_buffer)
                ffmpegProcess.ffmpeg_process.stdin.write(data_to_send)
                ffmpegProcess.ffmpeg_process.stdin.flush()
            except Exception as e:
                print("Error writing to ffmpeg:", e)
            self.nalu_buffer = []

    def closeEvent(self, event):
        """ Handle window close event to terminate ffmpeg process """
        self.stop_ffmpeg()
        event.accept()





