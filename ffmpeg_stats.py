from flask import Flask, jsonify
from flask_cors import CORS
import subprocess
import threading
import time
import re
import requests  # 新增导入requests库

class FFmpegStatsApp:
    def __init__(self):
        self.app = Flask(__name__)
        CORS(self.app)  # 允许所有来源的跨域请求
        self.stream1_stats = {}
        self.stream2_stats = {}
        self.setup_routes()

    def setup_routes(self):
        @self.app.route('/stats', methods=['GET'])
        def stats():
            return jsonify(stream1=self.stream1_stats, stream2=self.stream2_stats)

    def get_resolution(self, stream_url):
        try:
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            result = subprocess.run(
                ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height", 
                 "-of", "default=noprint_wrappers=1", stream_url],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, startupinfo=startupinfo, creationflags=subprocess.CREATE_NO_WINDOW
            )
            output = result.stdout
            m_width = re.search(r'width=\s*(\d+)', output)
            m_height = re.search(r'height=\s*(\d+)', output)
            if not m_width or not m_height:
                return "Unknown"
            width = int(m_width.group(1))
            height = int(m_height.group(1))
            return f"{width}x{height}"
        except Exception as e:
            return "Unknown"

    def run_ffmpeg(self, stream_url, stats_dict):
        while True:
            try:
                # 发送GET请求到目标IP的8889端口
                target_ip = stream_url.split('/')[2].split(':')[0]
                try:
                    requests.get(f"http://{target_ip}:8889")
                except requests.ConnectionError:
                    time.sleep(1)
                    continue

                resolution = self.get_resolution(stream_url)
                stats_dict['resolution'] = resolution
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                process = subprocess.Popen(
                    ["ffmpeg", "-i", stream_url, "-c:v", "copy", "-f", "h264", "NUL", "-progress", "-"],
                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True, startupinfo=startupinfo, creationflags=subprocess.CREATE_NO_WINDOW
                )
                frame_rate = "Unknown"
                bitrate = "Unknown"
                for line in process.stdout:
                    if "fps=" in line:
                        frame_rate_match = re.search(r'fps=\s*(\d+)', line)
                        if frame_rate_match:
                            frame_rate = frame_rate_match.group(1)
                    if "bitrate=" in line:
                        bitrate_match = re.search(r'bitrate=\s*(\d+)', line)
                        if bitrate_match:
                            bitrate = bitrate_match.group(1)
                    stats_dict['frame_rate'] = frame_rate
                    stats_dict['bitrate'] = bitrate
                process.wait()
            except Exception as e:
                pass
            time.sleep(1)

    def start(self):
        threading.Thread(target=self.run_ffmpeg, args=("rtsp://192.168.137.18:8554/stream1", self.stream1_stats), daemon=True).start()
        threading.Thread(target=self.run_ffmpeg, args=("rtsp://localhost:8554/stream2", self.stream2_stats), daemon=True).start()
        self.app.run(debug=True, use_reloader=False, port=6060, host="0.0.0.0")

if __name__ == '__main__':
    app = FFmpegStatsApp()
    app.start()
