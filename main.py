import json, os, tool, time, requests, sys, importlib, argparse, ruamel.yaml
import re

from urllib.parse import urlparse
from collections import OrderedDict
from parsers.clash2base64 import clash2v2ray

parsers_mod = {}
providers = None
color_code = [31, 32, 33, 34, 35, 36, 91, 92, 93, 94, 95, 96]

VERSION_OUTBOUND_MAP = {
    'shadowtls': (1, 11),
    'anytls': (1, 12),
}


def loop_color(text):
    text = '\033[1;{color}m{text}\033[0m'.format(color=color_code[0], text=text)
    color_code.append(color_code.pop(0))
    return text


def init_parsers():
    b = os.walk('parsers')
    for path, dirs, files in b:
        for file in files:
            f = os.path.splitext(file)
            if f[1] == '.py':
                parsers_mod[f[0]] = importlib.import_module('parsers.' + f[0])


def get_template():
    template_dir = 'config_template'
    template_files = os.listdir(template_dir)
    template_list = [os.path.splitext(file)[0] for file in template_files if file.endswith('.json')]
    template_list.sort()
    return template_list


def load_json(path):
    return json.loads(tool.readFile(path))


def get_singbox_version():
    version_str = providers.get('singbox_version', '1.14')
    try:
        parts = version_str.split('.')
        return (int(parts[0]), int(parts[1]))
    except:
        return (1, 14)


def filter_by_version(nodes):
    version = get_singbox_version()
    filtered = []
    for node in nodes:
        node_type = node.get('type', '')
        min_version = VERSION_OUTBOUND_MAP.get(node_type)
        if min_version and version < min_version:
            print(f'过滤不兼容节点: {node.get("tag", "")} ({node_type} 需要 >={min_version[0]}.{min_version[1]})')
            continue
        filtered.append(node)
    return filtered


def process_subscribes(subscribes):
    nodes = {}
    for subscribe in subscribes:
        if 'sing-box-subscribe-doraemon.vercel.app' in subscribe['url']:
            continue
        _nodes = get_nodes(subscribe['url'])
        if _nodes and len(_nodes) > 0:
            _nodes = filter_by_version(_nodes)
            for node in _nodes:
                node['tag'] = tool.rename(node['tag'])
                if node.get('detour'):
                    node['detour'] = tool.rename(node['detour'])
            if not nodes.get(subscribe['tag']):
                nodes[subscribe['tag']] = []
            nodes[subscribe['tag']] += _nodes
        else:
            print('没有在此订阅下找到节点，跳过')
    tool.proDuplicateNodeName(nodes)
    return nodes


def nodes_filter(nodes, filter, group):
    for a in filter:
        if a.get('for') and group not in a['for']:
            continue
        nodes = action_keywords(nodes, a['action'], a['keywords'])
    return nodes


def action_keywords(nodes, action, keywords):
    temp_nodes = []
    flag = False
    if action == 'exclude':
        flag = True
    combined_pattern = '|'.join(keywords)
    if not combined_pattern or combined_pattern.isspace():
        return nodes
    compiled_pattern = re.compile(combined_pattern)
    for node in nodes:
        name = node['tag']
        match_flag = bool(compiled_pattern.search(name))
        if match_flag ^ flag:
            temp_nodes.append(node)
    return temp_nodes


def get_nodes(url):
    if url.startswith('sub://'):
        url = tool.b64Decode(url[6:]).decode('utf-8')
    urlstr = urlparse(url)
    if not urlstr.scheme:
        try:
            content = tool.b64Decode(url).decode('utf-8')
            data = parse_content(content)
            return _process_shadowtls(data)
        except:
            content = get_content_form_file(url)
    else:
        content = get_content_from_url(url)
    if type(content) == dict:
        if 'proxies' in content:
            share_links = []
            for proxy in content['proxies']:
                share_links.append(clash2v2ray(proxy))
            data = '\n'.join(share_links)
            data = parse_content(data)
            return _process_shadowtls(data)
        elif 'outbounds' in content:
            outbounds = []
            excluded_types = {"selector", "urltest", "direct", "block", "dns"}
            filtered_outbounds = [outbound for outbound in content['outbounds'] if outbound.get("type") not in excluded_types]
            outbounds.extend(filtered_outbounds)
            return outbounds
    else:
        data = parse_content(content)
        return _process_shadowtls(data)


def _process_shadowtls(data):
    processed_list = []
    for item in data:
        if isinstance(item, tuple):
            processed_list.extend([item[0], item[1]])
        else:
            processed_list.append(item)
    return processed_list


def parse_content(content):
    nodelist = []
    for t in content.splitlines():
        t = t.strip()
        if len(t) == 0:
            continue
        factory = get_parser(t)
        if not factory:
            continue
        try:
            node = factory(t)
        except Exception as e:
            pass
        if node:
            nodelist.append(node)
    return nodelist


def get_parser(node):
    proto = tool.get_protocol(node)
    if not proto or proto not in parsers_mod.keys():
        return None
    return parsers_mod[proto].parse


def get_content_from_url(url, n=10):
    print('处理: \033[31m' + url + '\033[0m')
    prefixes = ["vmess://", "vless://", "ss://", "ssr://", "trojan://", "tuic://", "hysteria://", "hysteria2://",
                "hy2://", "wg://", "wireguard://", "http2://", "socks://", "socks5://"]
    if any(url.startswith(prefix) for prefix in prefixes):
        response_text = tool.noblankLine(url)
        return response_text
    response = tool.getResponse(url)
    concount = 1
    while concount <= n and not response:
        print('连接出错，正在进行第 ' + str(concount) + ' 次重试，最多重试 ' + str(n) + ' 次...')
        response = tool.getResponse(url)
        concount = concount + 1
        time.sleep(1)
    if not response:
        print('获取错误，跳过此订阅')
        print('----------------------------')
        return None
    try:
        response_content = response.content
        response_text = response_content.decode('utf-8-sig')
    except:
        return ''
    if response_text.isspace():
        print('没有从订阅链接获取到任何内容')
        return None
    if not response_text:
        response = tool.getResponse(url, custom_user_agent='clashmeta')
        response_text = response.text
    if any(response_text.startswith(prefix) for prefix in prefixes):
        response_text = tool.noblankLine(response_text)
        return response_text
    elif 'proxies' in response_text:
        yaml_content = response.content.decode('utf-8')
        response_text_no_tabs = yaml_content.replace('\t', ' ')
        ryaml = ruamel.yaml.YAML()
        try:
            response_text = dict(ryaml.load(response_text_no_tabs))
            return response_text
        except:
            pass
    elif 'outbounds' in response_text:
        try:
            response_text = json.loads(response.text)
            return response_text
        except:
            try:
                import re as _re
                response_text = _re.sub(r'//.*', '', response_text)
                response_text = json.loads(response_text)
                return response_text
            except:
                pass
    else:
        try:
            response_text = tool.b64Decode(response_text)
            response_text = response_text.decode(encoding="utf-8")
        except:
            pass
    return response_text


def get_content_form_file(url):
    print('处理: \033[31m' + url + '\033[0m')
    file_extension = os.path.splitext(url)[1]
    if file_extension.lower() == '.yaml':
        with open(url, 'rb') as file:
            content = file.read()
        ryaml = ruamel.yaml.YAML()
        yaml_data = dict(ryaml.load(content))
        share_links = []
        for proxy in yaml_data['proxies']:
            share_links.append(clash2v2ray(proxy))
        node = '\n'.join(share_links)
        processed_list = tool.noblankLine(node)
        return processed_list
    else:
        data = tool.readFile(url)
        data = bytes.decode(data, encoding='utf-8')
        data = tool.noblankLine(data)
        return data


def save_config(path, nodes):
    try:
        if os.path.exists(path):
            os.remove(path)
            print(f"已删除文件，并重新保存：\033[33m{path}\033[0m")
        else:
            print(f"文件不存在，正在保存：\033[33m{path}\033[0m")
        tool.saveFile(path, json.dumps(nodes, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"保存配置文件时出错：{str(e)}")
        config_file_path = os.path.join('/tmp', 'config.json')
        try:
            if os.path.exists(config_file_path):
                os.remove(config_file_path)
                print(f"已删除文件，并重新保存：\033[33m{config_file_path}\033[0m")
            else:
                print(f"文件不存在，正在保存：\033[33m{config_file_path}\033[0m")
            tool.saveFile(config_file_path, json.dumps(nodes, indent=2, ensure_ascii=False))
        except Exception as e2:
            print(f"再次保存配置文件时出错：{str(e2)}")


def pro_node_template(data_nodes, config_outbound, group):
    if config_outbound.get('filter'):
        data_nodes = nodes_filter(data_nodes, config_outbound['filter'], group)
    return [node.get('tag') for node in data_nodes]


def combin_to_config(config, data):
    config_outbounds = config["outbounds"] if config.get("outbounds") else None
    temp_outbounds = []
    if config_outbounds:
        direct_item = next((item for item in config_outbounds if item.get('type') == 'direct'), None)
        for po in config_outbounds:
            if po.get("outbounds"):
                if '{all}' in po["outbounds"]:
                    o1 = []
                    for item in po["outbounds"]:
                        if item.startswith('{') and item.endswith('}'):
                            _item = item[1:-1]
                            if _item == 'all':
                                o1.append(item)
                        else:
                            o1.append(item)
                    po['outbounds'] = o1
                t_o = []
                check_dup = []
                for oo in po["outbounds"]:
                    if oo in check_dup:
                        continue
                    else:
                        check_dup.append(oo)
                    if oo.startswith('{') and oo.endswith('}'):
                        oo = oo[1:-1]
                        if data.get(oo):
                            nodes = data[oo]
                            t_o.extend(pro_node_template(nodes, po, oo))
                        else:
                            if oo == 'all':
                                for group in data:
                                    nodes = data[group]
                                    t_o.extend(pro_node_template(nodes, po, group))
                    else:
                        t_o.append(oo)
                if len(t_o) == 0:
                    t_o.append(direct_item['tag'])
                    print('发现 {} 出站下的节点数量为 0 ，会导致sing-box无法运行，请检查config模板是否正确。'.format(po['tag']))
                po['outbounds'] = t_o
                if po.get('filter'):
                    del po['filter']
    for group in data:
        temp_outbounds.extend(data[group])
    config['outbounds'] = config_outbounds + temp_outbounds

    version = get_singbox_version()
    wireguard_items = [item for item in config['outbounds'] if item.get('type') == 'wireguard']
    if wireguard_items:
        if version >= (1, 11):
            endpoints = []
            for item in wireguard_items:
                ep = dict(item)
                if 'local_address' in ep:
                    ep['address'] = ep.pop('local_address')
                if 'peers' in ep:
                    for peer in ep['peers']:
                        if 'server' in peer:
                            peer['address'] = peer.pop('server')
                        if 'server_port' in peer:
                            peer['port'] = peer.pop('server_port')
                ep.pop('type', None)
                endpoints.append(ep)
            new_config = OrderedDict()
            for key, value in config.items():
                new_config[key] = value
                if key == 'outbounds':
                    new_config['endpoints'] = endpoints
            config = new_config
            config['outbounds'] = [item for item in config['outbounds'] if item.get('type') != 'wireguard']
    return config


def display_template(tl):
    print_str = ''
    for i in range(len(tl)):
        print_str += loop_color('{index}、{name} '.format(index=i + 1, name=tl[i]))
    print(print_str)


def select_config_template(tl, selected_template_index=None):
    if selected_template_index is not None:
        return selected_template_index
    uip = input('输入序号，载入对应config模板（直接回车默认选第一个配置模板）：')
    try:
        if uip == '':
            return 0
        uip = int(uip)
        if uip < 1 or uip > len(tl):
            print('输入了错误信息！重新输入')
            return select_config_template(tl)
        else:
            uip -= 1
    except:
        print('输入了错误信息！重新输入')
        return select_config_template(tl)
    return uip


def parse_json(value):
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        raise argparse.ArgumentTypeError(f"Invalid JSON: {value}")


if __name__ == '__main__':
    init_parsers()
    parser = argparse.ArgumentParser()
    parser.add_argument('--temp_json_data', type=parse_json, help='临时内容')
    parser.add_argument('--template_index', type=int, help='模板序号')
    args = parser.parse_args()
    temp_json_data = args.temp_json_data

    if temp_json_data and temp_json_data != '{}':
        providers = json.loads(temp_json_data)
    else:
        providers = load_json('providers.json')
    if providers.get('config_template'):
        config_template_path = providers['config_template']
        print('选择: \033[33m' + config_template_path + '\033[0m')
        response = requests.get(providers['config_template'])
        response.raise_for_status()
        config = response.json()
        template_name = config_template_path.rstrip('/').rsplit('/', 1)[-1].replace('.json', '')
    else:
        template_list = get_template()
        if len(template_list) < 1:
            print('没有找到模板文件')
            sys.exit()
        display_template(template_list)
        uip = select_config_template(template_list, selected_template_index=args.template_index)
        config_template_path = 'config_template/' + template_list[uip] + '.json'
        print('选择: \033[33m' + template_list[uip] + '.json\033[0m')
        config = load_json(config_template_path)
        template_name = template_list[uip]
    version_match = re.match(r'(\d+\.\d+)', template_name)
    if version_match:
        providers['singbox_version'] = version_match.group(1)
    nodes = process_subscribes(providers["subscribes"])
    final_config = combin_to_config(config, nodes)
    save_config(providers["save_config_path"], final_config)
