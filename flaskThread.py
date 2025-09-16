from flask import Flask, jsonify, request
from flask_cors import CORS
import socket
import subprocess
import os
import threading
import time
import crcmod

global comm_status_1, comm_status_2, bitrate_1, bitrate_2, resolution_1, resolution_2
comm_status_1 = -1
comm_status_2 = -1
bitrate_1 = -1
bitrate_2 = -1
resolution_1 = {"width": -1, "height": -1}
resolution_2 = {"width": -1, "height": -1}

class FlaskThread:
    def __init__(self):
        self.app = Flask(__name__)
        CORS(self.app)  # 允许所有来源的跨域请求
        self.setup_routes()
        self.ffmpeg_process1 = None
        self.ffmpeg_process2 = None
        self.ffmpeg_process1_restart_time = 0
        self.ffmpeg_process2_restart_time = 0

    def reconstructStream1FromH264(self):
        """ Start ffmpeg process to push stream to rtsp, with daemon restart """
        while True:
            if self.ffmpeg_process1 is None or self.ffmpeg_process1.poll() is not None:
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                ffmpeg_path = os.path.join(os.getcwd(), "ffmpeg", "bin", "ffmpeg.exe")
                self.ffmpeg_process1 = subprocess.Popen([
                    ffmpeg_path, 
                    '-f', 'h264', 
                    '-i', 'pipe:0',
                    '-c:v', 'copy', 
                    '-rtsp_transport', 'tcp', 
                    '-f', 'rtsp',
                    'rtsp://localhost:8554/stream1',
                ], stdin=subprocess.PIPE, startupinfo=startupinfo, creationflags=subprocess.CREATE_NO_WINDOW)
                self.ffmpeg_process1_restart_time += 1
            time.sleep(1)

    def reconstructStream2FromH264(self):
        """ Start ffmpeg process to push stream to rtsp, with daemon restart """
        while True:
            if self.ffmpeg_process2 is None or self.ffmpeg_process2.poll() is not None:
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                ffmpeg_path = os.path.join(os.getcwd(), "ffmpeg", "bin", "ffmpeg.exe")
                self.ffmpeg_process2 = subprocess.Popen([
                    ffmpeg_path, 
                    '-re',              
                    '-f', 'h264', 
                    '-i', 'pipe:0',
                    '-c:v', 'copy', 
                    '-rtsp_transport', 'tcp', 
                    '-f', 'rtsp',
                    'rtsp://localhost:8554/stream2',
                ], stdin=subprocess.PIPE, startupinfo=startupinfo, creationflags=subprocess.CREATE_NO_WINDOW)
                self.ffmpeg_process2_restart_time += 1
            time.sleep(1)

    def receiveUDPDataToReconstruct1(self, buffer_size=4096):
        while True:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.bind(('0.0.0.0', 10002))
                while True:
                    data, addr = sock.recvfrom(buffer_size)
                    if self.ffmpeg_process1 and self.ffmpeg_process1.stdin:
                        self.ffmpeg_process1.stdin.write(data)
            except Exception as e:
                time.sleep(1)
            finally:
                try:
                    sock.close()
                except:
                    pass

    def receiveUDPDataToReconstruct2(self, buffer_size=4096):
        while True:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.bind(('0.0.0.0', 10012))
                while True:
                    data, addr = sock.recvfrom(buffer_size)
                    if self.ffmpeg_process2 and self.ffmpeg_process2.stdin:
                        self.ffmpeg_process2.stdin.write(data)
            except Exception as e:
                time.sleep(1)
            finally:
                try:
                    sock.close()
                except:
                    pass
                
    def parse_udp_protocol(self, data):
        """解析自定义UDP协议，返回解析结果或None"""
        if len(data) < 9:
            return None
        if data[0:4] != b'\x48\x59\x43\x4C':
            return None
        addr_byte = data[4]
        cmd_type = data[5]
        length = data[6]
        if len(data) != length:
            return None
        payload = data[7:-2]
        crc_recv = int.from_bytes(data[-2:], byteorder='little')
        crc16_modbus = crcmod.mkCrcFun(0x18005, initCrc=0xFFFF, rev=True, xorOut=0x0000)
        crc_calc = crc16_modbus(data[:-2])
        if crc_calc != crc_recv:
            return None
        return {
            'addr': addr_byte,
            'cmd': cmd_type,
            'length': length,
            'payload': payload,
            'crc': crc_recv
        }

    def receiveUDPCommandFrom1(self, buffer_size=4096):
        while True:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.bind(('0.0.0.0', 10001))
                while True:
                    data, addr = sock.recvfrom(buffer_size)
                    result = self.parse_udp_protocol(data)
                    if result is not None:
                        if result['addr'] == 0x01 and result['cmd'] == 0x01:
                            if len(result['payload']) >= 2:
                                global comm_status_1, bitrate_1
                                comm_status_1 = result['payload'][0]
                                bitrate_1 = result['payload'][1]
            except Exception as e:
                time.sleep(1)
            finally:
                try:
                    sock.close()
                except:
                    pass

    def receiveUDPCommandFrom2(self, buffer_size=4096):
        while True:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.bind(('0.0.0.0', 10011))
                while True:
                    data, addr = sock.recvfrom(buffer_size)
                    result = self.parse_udp_protocol(data)
                    if result is not None:
                        if result['addr'] == 0x01 and result['cmd'] == 0x01:
                            if len(result['payload']) >= 1:
                                global comm_status_2
                                comm_status_2 = result['payload'][0]
                        if result['addr'] == 0x01 and result['cmd'] == 0x06:
                            if len(result['payload']) >= 1:
                                global bitrate_2
                                bitrate_2 = result['payload'][0]
            except Exception as e:
                time.sleep(1)
            finally:
                try:
                    sock.close()
                except:
                    pass

    # 新增方法：持续获取stream1分辨率
    def update_resolution_1(self):
        global resolution_1
        ffprobe_path = os.path.join(os.getcwd(), "ffmpeg", "bin", "ffprobe.exe")
        rtsp_url = "rtsp://localhost:8554/stream1"
        while True:
            try:
                result = subprocess.run([
                    ffprobe_path, "-v", "error", "-select_streams", "v:0",
                    "-show_entries", "stream=width,height",
                    "-of", "default=noprint_wrappers=1",
                    "-i", rtsp_url
                ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=5, creationflags=subprocess.CREATE_NO_WINDOW)
                output = result.stdout.decode()
                width, height = -1, -1
                for line in output.splitlines():
                    if line.startswith("width="):
                        width = int(line.split("=")[1])
                    elif line.startswith("height="):
                        height = int(line.split("=")[1])
                resolution_1 = {"width": width, "height": height}
            except Exception:
                resolution_1 = {"width": -1, "height": -1}
            time.sleep(2)

    # 新增方法：持续获取stream2分辨率
    def update_resolution_2(self):
        global resolution_2
        ffprobe_path = os.path.join(os.getcwd(), "ffmpeg", "bin", "ffprobe.exe")
        rtsp_url = "rtsp://localhost:8554/stream2"
        while True:
            try:
                result = subprocess.run([
                    ffprobe_path, "-v", "error", "-select_streams", "v:0",
                    "-show_entries", "stream=width,height",
                    "-of", "default=noprint_wrappers=1",
                    "-i", rtsp_url
                ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=5, creationflags=subprocess.CREATE_NO_WINDOW)
                output = result.stdout.decode()
                width, height = -1, -1
                for line in output.splitlines():
                    if line.startswith("width="):
                        width = int(line.split("=")[1])
                    elif line.startswith("height="):
                        height = int(line.split("=")[1])
                resolution_2 = {"width": width, "height": height}
            except Exception:
                resolution_2 = {"width": -1, "height": -1}
            time.sleep(2)

    def setup_routes(self):
        @self.app.route('/send_udp', methods=['POST'])
        def send_udp():
            data = self.app.current_request.get_json(force=True) if hasattr(self.app, 'current_request') else None
            if data is None:
                data = request.get_json(force=True)
            ip = data.get('ip')
            port = data.get('port')
            hex_str = data.get('hex')
            try:
                udp_data = bytes.fromhex(hex_str)
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.sendto(udp_data, (ip, int(port)))
                sock.close()
                return jsonify({'status': 'success'}), 200
            except Exception as e:
                return jsonify({'status': 'error', 'msg': str(e)}), 400

        @self.app.route('/ffmpeg_status', methods=['GET'])
        def ffmpeg_status():
            status1 = 'running' if self.ffmpeg_process1 and self.ffmpeg_process1.poll() is None else 'stopped'
            status2 = 'running' if self.ffmpeg_process2 and self.ffmpeg_process2.poll() is None else 'stopped'
            return jsonify({
                'ffmpeg_process1': status1,
                'ffmpeg_process2': status2
            })

        @self.app.route('/status_feedback', methods=['GET'])
        def status_feedback():
            # 状态映射
            comm_status_1_map = {-1: "未知", 0: "正常", 1: "异常"}
            bitrate_1_map = {-1: "未知", 1: 8000, 2: 4000, 3: 2000, 4: 1000}
            comm_status_2_map = {-1: "未知", 0: "成功"}
            bitrate_2_map = {-1: "未知", 5: 80, 6: 40, 7: 20, 8: 10}
            return jsonify({
                "comm_status_1_str": comm_status_1_map.get(comm_status_1, "未知"),
                "bitrate_1_value": bitrate_1_map.get(bitrate_1, "未知"),
                "comm_status_2_str": comm_status_2_map.get(comm_status_2, "未知"),
                "bitrate_2_value": bitrate_2_map.get(bitrate_2, "未知"),
                # 新增分辨率信息
                "resolution_1": resolution_1,
                "resolution_2": resolution_2
            })

        @self.app.route('/restart_ffmpeg', methods=['POST'])
        def restart_ffmpeg():
            data = request.get_json(force=True)
            target = data.get('target', 'all')
            killed = []
            if target in ['ffmpeg_process1', 'all']:
                if self.ffmpeg_process1 and self.ffmpeg_process1.poll() is None:
                    self.ffmpeg_process1.kill()
                    killed.append('ffmpeg_process1')
            if target in ['ffmpeg_process2', 'all']:
                if self.ffmpeg_process2 and self.ffmpeg_process2.poll() is None:
                    self.ffmpeg_process2.kill()
                    killed.append('ffmpeg_process2')
            return jsonify({'status': 'ok', 'killed': killed})

        @self.app.route('/ffmpeg_restart_count', methods=['GET'])
        def ffmpeg_restart_count():
            return jsonify({
                'ffmpeg_process1_restart_time': self.ffmpeg_process1_restart_time,
                'ffmpeg_process2_restart_time': self.ffmpeg_process2_restart_time
            })

        @self.app.route('/reset_ffmpeg_restart_count', methods=['POST'])
        def reset_ffmpeg_restart_count():
            data = request.get_json(force=True)
            target = data.get('target', 'all')
            reset = []
            if target in ['ffmpeg_process1', 'all']:
                if self.ffmpeg_process1 and self.ffmpeg_process1.poll() is None:
                    self.ffmpeg_process1_restart_time = 1
                else:
                    self.ffmpeg_process1_restart_time = 0
                reset.append('ffmpeg_process1')
            if target in ['ffmpeg_process2', 'all']:
                if self.ffmpeg_process2 and self.ffmpeg_process2.poll() is None:
                    self.ffmpeg_process2_restart_time = 1
                else:
                    self.ffmpeg_process2_restart_time = 0
                reset.append('ffmpeg_process2')
            return jsonify({'status': 'ok', 'reset': reset})

    def start(self):
        threading.Thread(target=self.reconstructStream1FromH264, daemon=True).start()
        threading.Thread(target=self.reconstructStream2FromH264, daemon=True).start()
        threading.Thread(target=self.receiveUDPDataToReconstruct1, daemon=True).start()
        threading.Thread(target=self.receiveUDPDataToReconstruct2, daemon=True).start()
        threading.Thread(target=self.receiveUDPCommandFrom1, daemon=True).start()
        threading.Thread(target=self.receiveUDPCommandFrom2, daemon=True).start()
        # 新增分辨率线程
        threading.Thread(target=self.update_resolution_1, daemon=True).start()
        threading.Thread(target=self.update_resolution_2, daemon=True).start()
        self.app.run(debug=True, use_reloader=False, port=6060, host="0.0.0.0")

if __name__ == '__main__':
    app = FlaskThread()
    app.start()
