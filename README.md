# sing-box 订阅转换

根据配置模板和订阅链接生成 sing-box 配置文件。

支持 sing-box 1.11 / 1.12 / 1.13 / 1.14，自动根据模板版本过滤不兼容协议。

## API

### 基本用法

```
https://你的域名/config/订阅链接
```

### 参数

| 参数 | 说明 | 示例 |
|------|------|------|
| `file` | 配置模板。数字=本地模板序号（从1开始），URL=远程模板 | `&file=1` 或 `&file=https://example.com/template.json` |
| `version` | sing-box 版本，用于协议兼容性过滤。不指定时从模板文件名自动提取 | `&version=1.13` |

### 示例

使用本地模板（第1个）：
```
https://你的域名/config/https://sub.example.com/sub?token=xxx&file=1
```

使用远程模板：
```
https://你的域名/config/https://sub.example.com/sub?token=xxx&file=https://raw.githubusercontent.com/.../1.13.x.json
```

使用自定义模板并指定版本：
```
https://你的域名/config/https://sub.example.com/sub?token=xxx&file=https://example.com/my-config.json&version=1.14
```

多个订阅链接（用 `|` 分隔）：
```
https://你的域名/config/https://sub1.example.com|https://sub2.example.com&file=1
```

### 版本过滤规则

| 协议 | 最低版本 |
|------|---------|
| shadowtls | 1.11 |
| anytls | 1.12 |

使用低于最低版本的模板时，对应协议节点会被自动过滤。

## 本地运行

```bash
pip install -r requirements.txt
python main.py
python main.py --template_index=0
```

## Web 界面

访问部署地址，输入订阅链接，选择模板，点击生成配置。

## 配置模板

| 模板 | 版本 | 说明 |
|------|------|------|
| 1.11.x-IPv4 | 1.11 | IPv4 |
| 1.11.x-IPv6 | 1.11 | IPv6 |
| 1.12.x | 1.12 | |
| 1.13.x | 1.13 | |
| 1.14.x | 1.14 | |

## 自定义模板

模板是标准的 sing-box 配置文件，只需在出站的 `outbounds` 列表中使用占位符：

- `{all}` — 插入所有节点
- `{tag名}` — 插入对应订阅的节点（如 `{sub_1}`）

示例：

```json
{
  "outbounds": [
    {
      "type": "selector",
      "tag": "Proxy",
      "outbounds": ["{all}"]
    },
    {
      "type": "direct",
      "tag": "Direct"
    }
  ]
}
```

模板文件名建议包含版本号（如 `1.14.x.json`），项目会自动识别并过滤不兼容协议。

## 部署

### Vercel

1. Fork 本仓库
2. 在 Vercel 导入仓库
3. 部署完成

## 支持的协议

vmess、vless、shadowsocks、trojan、tuic、hysteria、hysteria2、wireguard、socks、http、anytls、shadowtls
