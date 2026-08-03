from flask import Flask, render_template, request, Response
import json
import os
import sys
import subprocess
import tempfile

app = Flask(__name__, template_folder='../templates')
app.secret_key = 'sing-box'

TEMP_DIR = tempfile.gettempdir()

def get_template_list():
    template_list = []
    config_template_dir = 'config_template'
    template_files = os.listdir(config_template_dir)
    template_list = [os.path.splitext(file)[0] for file in template_files if file.endswith('.json')]
    template_list.sort()
    return template_list

@app.route('/')
def index():
    template_list = get_template_list()
    template_options = [f"{template}" for template in template_list]
    return render_template('index.html', template_options=template_options)

@app.route('/generate_config', methods=['POST'])
def generate_config():
    try:
        payload_str = request.form.get('payload')
        template_index = request.form.get('template_index', '0')
        if not payload_str:
            return Response(json.dumps({'status': 'error', 'message': 'payload is required'}, ensure_ascii=False),
                            content_type='application/json; charset=utf-8', status=400)
        payload = json.loads(payload_str)
        temp_json_data = json.dumps(json.dumps(payload, ensure_ascii=False), ensure_ascii=False)
        subprocess.check_call([sys.executable, 'main.py', '--template_index', template_index, '--temp_json_data', temp_json_data])
        config_file_path = os.path.join('/tmp/', 'config.json')
        if not os.path.exists(config_file_path):
            config_file_path = 'config.json'
        with open(config_file_path, 'r', encoding='utf-8') as config_file:
            config_content = config_file.read()
        return Response(config_content, content_type='text/plain; charset=utf-8')
    except subprocess.CalledProcessError:
        return Response(json.dumps({'status': 'error'}, ensure_ascii=False),
                        content_type='application/json; charset=utf-8', status=500)
    except Exception as e:
        return Response(json.dumps({'status': 'error', 'message': str(e)}, ensure_ascii=False),
                        content_type='application/json; charset=utf-8', status=500)

@app.route('/config/<path:url>', methods=['GET'])
def config(url):
    user_agent = request.headers.get('User-Agent') or ""
    rua_values = os.getenv('RUA')
    if rua_values and any(rua_value in user_agent for rua_value in rua_values.split(',')):
        return Response(json.dumps({'status': 'error', 'message': 'block'}, ensure_ascii=False),
                        content_type='application/json; charset=utf-8', status=403)
    substrings = os.getenv('STR')
    if substrings and any(substring in url for substring in substrings.split(',')):
        return Response(json.dumps({'status': 'error', 'message': 'invalid parameter'}, ensure_ascii=False),
                        content_type='application/json; charset=utf-8', status=403)
    from urllib.parse import unquote, urlparse, quote
    encoded_url = unquote(url)
    query_string = request.query_string.decode('utf-8')
    index_of_colon = encoded_url.find(":")
    if index_of_colon != -1:
        next_char_index = index_of_colon + 2
        if next_char_index < len(encoded_url) and encoded_url[next_char_index] != "/":
            encoded_url = encoded_url[:next_char_index-1] + "/" + encoded_url[next_char_index-1:]
    if query_string:
        full_url = f"{encoded_url}?{query_string}"
    else:
        full_url = encoded_url
    file_param = request.args.get('file', '')
    version_param = request.args.get('version', '')
    params_to_remove = []
    if file_param:
        params_to_remove.extend([f'&file={file_param}', f'file={file_param}'])
    if version_param:
        params_to_remove.extend([f'&version={version_param}', f'version={version_param}'])
    full_url = full_url.replace(',', '%2C')
    for param in params_to_remove:
        if param in full_url:
            full_url = full_url.replace(param, '')
    full_url = unquote(full_url)
    if '/api/v4/projects/' in full_url:
        parts = full_url.split('/api/v4/projects/')
        full_url = parts[0] + '/api/v4/projects/' + parts[1].replace('/', '%2F', 1)
    url_parts = full_url.split('|')
    subscribes = []
    for i, part in enumerate(url_parts):
        subscribes.append({
            "url": part,
            "tag": f"sub_{i+1}",
            "emoji": 1,
            "enabled": True
        })
    payload = {
        "subscribes": subscribes,
        "save_config_path": "./config.json"
    }
    if version_param:
        payload["singbox_version"] = version_param
    try:
        selected_template_index = '0'
        if file_param and file_param.isdigit() and int(file_param) >= 1:
            selected_template_index = str(int(file_param) - 1)
        elif file_param:
            payload["config_template"] = unquote(file_param)
        temp_json_data = json.dumps(json.dumps(payload, ensure_ascii=False), ensure_ascii=False)
        subprocess.check_call([sys.executable, 'main.py', '--template_index', selected_template_index, '--temp_json_data', temp_json_data])
        config_file_path = os.path.join('/tmp/', 'config.json')
        if not os.path.exists(config_file_path):
            config_file_path = 'config.json'
        with open(config_file_path, 'r', encoding='utf-8') as config_file:
            config_content = config_file.read()
        return Response(config_content, content_type='text/plain; charset=utf-8')
    except subprocess.CalledProcessError:
        return Response(json.dumps({'status': 'error'}, ensure_ascii=False),
                        content_type='application/json; charset=utf-8', status=500)
    except Exception as e:
        return Response(json.dumps({'status': 'error', 'message': str(e)}, ensure_ascii=False),
                        content_type='application/json; charset=utf-8', status=500)


class _StripApiPrefix:
    """兼容 Vercel Python Runtime 的路径前缀处理。

    新版 Vercel Python 构建器会将 rewrite 后的路径（如 /api/app）作为
    PATH_INFO 传给 Flask，而应用路由定义的是 /、/generate_config、
    /config/<path>。此中间件剥离 /api/app 前缀，保证路由正常匹配；
    对旧版 runtime（PATH_INFO 已是原始路径）则不做改动。
    """
    def __init__(self, wsgi_app, prefix='/api/app'):
        self.wsgi_app = wsgi_app
        self.prefix = prefix

    def __call__(self, environ, start_response):
        path = environ.get('PATH_INFO', '')
        if path == self.prefix:
            environ['PATH_INFO'] = '/'
        elif path.startswith(self.prefix + '/'):
            environ['PATH_INFO'] = path[len(self.prefix):]
        return self.wsgi_app(environ, start_response)


app.wsgi_app = _StripApiPrefix(app.wsgi_app)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
