import os
import subprocess
from http.server import SimpleHTTPRequestHandler, HTTPServer
import urllib.parse
import json
import sys
import logging
import base64

# 设置日志记录，输出到文件
logging.basicConfig(filename='fnWifi.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 读取配置文件
config_path = os.path.join(os.path.dirname(__file__), 'config.json')
with open(config_path) as config_file:
    config = json.load(config_file)

USERNAME = config['username']
PASSWORD = config['password']

def run_subprocess(command):
    try:
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode != 0:
            logging.error(f"Command '{' '.join(command)}' failed: {result.stderr}")
            return None, result.stderr
        return result.stdout.strip(), None
    except Exception as e:
        logging.error(f"An error occurred while running command '{' '.join(command)}': {str(e)}")
        return None, str(e)

def list_wifi_networks():
    stdout, stderr = run_subprocess(['nmcli', '-t', '-f', 'SSID,SECURITY,SIGNAL', 'dev', 'wifi'])
    if stderr:
        return []
    wifi_list = [line.split(':') for line in stdout.split('\n') if line]
    wifi_list.sort(key=lambda x: int(x[2]), reverse=True)
    return wifi_list

def get_current_wifi():
    stdout, stderr = run_subprocess(['nmcli', '-t', '-f', 'DEVICE,TYPE,STATE,CONNECTION', 'device'])
    if stderr:
        return None
    devices = stdout.split('\n')
    for device in devices:
        fields = device.split(':')
        if len(fields) >= 4 and fields[1] == 'wifi' and fields[2] == 'connected':
            return fields[3]
    return None

def connect_to_wifi(ssid, password):
    _, stderr = run_subprocess(['nmcli', 'dev', 'wifi', 'connect', ssid, 'password', password])
    if stderr:
        return json.dumps({'status': 'error', 'message': stderr})
    return json.dumps({'status': 'success', 'message': '连接成功'})

def disconnect_wifi(ssid):
    _, stderr = run_subprocess(['nmcli', 'connection', 'down', ssid])
    if stderr:
        return json.dumps({'status': 'error', 'message': stderr})
    return json.dumps({'status': 'success', 'message': '断开成功'})

def authenticate(headers):
    auth_header = headers.get('Authorization')
    if auth_header is None:
        return False
    expected_auth = 'Basic ' + str(base64.b64encode(bytes(USERNAME + ':' + PASSWORD, 'utf-8')), 'utf-8')
    return auth_header == expected_auth

class CustomHandler(SimpleHTTPRequestHandler):
    def do_AUTHHEAD(self):
        self.send_response(401)
        self.send_header('WWW-Authenticate', 'Basic realm=\"Test\"')
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def handle_request(self, handler_func):
        if not authenticate(self.headers):
            self.do_AUTHHEAD()
            self.wfile.write(b'not authenticated')
            return
        handler_func()

    def do_GET(self):
        self.handle_request(self.handle_get)

    def handle_get(self):
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
            # 处理静态文件请求
            if self.path == '/':
                requested_path = 'web/index.html'
            else:
                requested_path = os.path.normpath('web' + self.path)

            # 确保请求路径在允许的范围内
            web_dir = os.path.normpath('web')
            requested_path = os.path.normpath(requested_path)
            if not requested_path.startswith(web_dir):
                self.send_response(403)
                self.end_headers()
                self.wfile.write(b'Forbidden')
                return

            # 尝试提供文件
            try:
                with open(requested_path, 'rb') as file:
                    content = file.read()
                    self.send_response(200)
                    mime_type = 'text/plain'
                    if os.path.splitext(requested_path)[1] == '.css':
                        mime_type = 'text/css'
                    elif os.path.splitext(requested_path)[1] == '.js':
                        mime_type = 'application/javascript'
                    elif os.path.splitext(requested_path)[1] == '.html':
                        mime_type = 'text/html'
                    
                    self.send_header('Content-type', mime_type)
                    self.end_headers()
                    self.wfile.write(content)
            except FileNotFoundError:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b'Not Found')
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(f'Internal Server Error: {str(e)}'.encode())

    def do_POST(self):
        self.handle_request(self.handle_post)

    def handle_post(self):
        if self.path == '/connect_wifi':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            try:
                data = urllib.parse.parse_qs(post_data)
                ssid = data.get('ssid', [''])[0]
                password = data.get('password', [''])[0]
                
                if not ssid or not password:
                    self.send_response(400)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({'status': 'error', 'message': 'ssid和password不能为空'}).encode())
                    return
                
                result = connect_to_wifi(ssid, password)
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(result.encode())
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'status': 'error', 'message': str(e)}).encode())
        elif self.path == '/disconnect_wifi':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            try:
                data = urllib.parse.parse_qs(post_data)
                ssid = data.get('ssid', [''])[0]
                
                if not ssid:
                    self.send_response(400)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({'status': 'error', 'message': 'ssid不能为空'}).encode())
                    return
                
                result = disconnect_wifi(ssid)
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(result.encode())
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'status': 'error', 'message': str(e)}).encode())

def main():
    # 检查是否以sudo权限运行
    if os.geteuid() != 0:
        print("请使用sudo权限运行此脚本")
        sys.exit(1)

    server_address = ('', 8100)
    httpd = HTTPServer(server_address, CustomHandler)
    print("Serving on port 8100")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n服务器已停止")

if __name__ == "__main__":
    main()