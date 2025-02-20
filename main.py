import os
import subprocess
from http.server import SimpleHTTPRequestHandler, HTTPServer
import urllib.parse
import json
import sys
import shlex

def list_wifi_networks():
    result = subprocess.run(['nmcli', '-t', '-f', 'SSID,SECURITY,SIGNAL', 'dev', 'wifi'], capture_output=True, text=True)
    wifi_list = result.stdout.strip().split('\n')
    wifi_list = [line.split(':') for line in wifi_list if line]
    wifi_list.sort(key=lambda x: int(x[2]), reverse=True)  # 按信号强度排序
    return wifi_list

def get_current_wifi():
    result = subprocess.run(['nmcli', '-t', '-f', 'DEVICE,TYPE,STATE,CONNECTION', 'device'], capture_output=True, text=True)
    devices = result.stdout.strip().split('\n')
    for device in devices:
        fields = device.split(':')
        if fields[1] == 'wifi' and fields[2] == 'connected':
            return fields[3]
    return None

def connect_to_wifi(ssid, password):
    result = subprocess.run(['sudo', 'nmcli', 'dev', 'wifi', 'connect', ssid, 'password', password], capture_output=True, text=True)
    if result.returncode == 0:
        return json.dumps({'status': 'success', 'message': '连接成功'})
    else:
        return json.dumps({'status': 'error', 'message': result.stderr})

def disconnect_wifi(ssid):
    result = subprocess.run(['sudo', 'nmcli', 'connection', 'down', ssid], capture_output=True, text=True)
    if result.returncode == 0:
        return json.dumps({'status': 'success', 'message': '断开成功'})
    else:
        return json.dumps({'status': 'error', 'message': result.stderr})

class CustomHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/wifi_list':
            wifi_list = list_wifi_networks()
            current_wifi = get_current_wifi()
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                'wifi_list': wifi_list,
                'current_wifi': current_wifi
            }
            self.wfile.write(json.dumps(response).encode())
        else:
            # 提供静态文件
            if self.path == '/':
                self.path = '/web/index.html'
            elif self.path.startswith('/web/'):
                self.path = self.path
            else:
                self.path = '/web' + self.path

            # 验证路径是否在允许的目录中
            requested_path = os.path.normpath(self.path)
            web_dir = os.path.normpath('/web')
            if not os.path.commonprefix([requested_path, web_dir]) == web_dir:
                self.send_response(403)
                self.end_headers()
                self.wfile.write(b'Forbidden')
                return

            return SimpleHTTPRequestHandler.do_GET(self)

    def do_POST(self):
        if self.path == '/connect_wifi':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = urllib.parse.parse_qs(post_data.decode('utf-8'))
            ssid = data['ssid'][0]
            password = data['password'][0]
            result = connect_to_wifi(ssid, password)
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(result.encode())
        elif self.path == '/disconnect_wifi':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = urllib.parse.parse_qs(post_data.decode('utf-8'))
            ssid = data['ssid'][0]
            result = disconnect_wifi(ssid)
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(result.encode())

def main():
    # 检查是否以sudo权限运行
    if os.geteuid() != 0:
        print("请使用sudo权限运行此脚本")
        sys.exit(1)

    server_address = ('', 8100)
    httpd = HTTPServer(server_address, CustomHandler)
    print("Serving on port 8100")
    httpd.serve_forever()

if __name__ == "__main__":
    main()
