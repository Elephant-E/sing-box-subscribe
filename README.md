# sing-box 订阅转换

Based on [Toperlock/sing-box-subscribe](https://github.com/Toperlock/sing-box-subscribe)

根据配置模板和订阅链接生成 sing-box 配置文件。

支持 sing-box 1.11 / 1.12 / 1.13 / 1.14 / 1.15（1.15 目前为 alpha），自动根据模板版本过滤不兼容协议。

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
| tailcat | 1.15 |

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
| 1.15.x | 1.15 | 1.15 为 alpha，配置与 1.14 一致 |

## sing-box 1.15 变更说明

1.15 目前仍为 alpha（最新 1.15.0-alpha.13），稳定版为 1.14.4。与配置文件相关的变更：

| 变更 | 影响 |
|------|------|
| TUN 改用新版内置 TCP/IP 栈 | 删除 `stack` 选项即启用；`stack` 自 1.15 废弃、将在 1.17.0 移除。本模板未使用 `stack`，无需调整 |
| HTTP 代理实现重写 | HTTP outbound 默认走 HTTP/2，失败自动回退 HTTP/1.1；配置了 `path` 或 `Host` 头时仍用 HTTP/1.1；HTTP/3 通过 `version` 选项开启；新增 CONNECT-UDP（UDP over HTTP） |
| 新增 MASQUE 客户端 / 服务端 endpoint | CONNECT-IP 形式的 IP 代理，可选能力，模板未启用 |
| 新增 Tailcat inbound / outbound | Tailscale 的数据面（经 DERP 引导的 WireGuard 点对点隧道）；订阅中出现该类型时，1.15 以下版本会被过滤 |
| 新增 TLS 证书 pinning | `certificate_sha256` / `client_certificate_sha256`，与原有公钥 pinning 互补 |
| 新增 DNS / 路由规则项 | `dns_server_address`、`dns_search_domain` |
| 新增 endpoint `on_demand` 选项 | WireGuard / Tailscale / OpenVPN Client / OpenConnect |
| 缓存文件写入缓冲 | 性能优化 |

另附 1.14 遗留的废弃项（将于 1.16.0 移除）：`download_detour` 由 `http_client` 取代；隐式默认 HTTP client 需显式配置 `http_clients` 与 `route.default_http_client`。本项目的 1.14 / 1.15 模板均已按新写法配置。

## 自定义模板

模板是标准的 sing-box 配置文件，在出站的 `outbounds` 中使用占位符插入节点：

| 占位符 | 说明 |
|--------|------|
| `{all}` | 插入所有节点 |
| `{sub_1}` | 插入第1个订阅的节点（多个订阅时用 sub_1、sub_2...） |

### 节点筛选

在出站中添加 `filter` 字段，按关键词筛选节点：

```json
{
  "type": "selector",
  "tag": "Proxy",
  "outbounds": ["{all}"]
}
```

排除包含"香港"的节点（创建独立分组，如 `No-HK`）：

```json
{
  "type": "selector",
  "tag": "No-HK",
  "outbounds": ["{all}"],
  "filter": [
    {
      "action": "exclude",
      "keywords": ["香港"]
    }
  ]
}
```

仅包含匹配的节点：

```json
"filter": [
  {
    "action": "include",
    "keywords": ["日本", "新加坡"]
  }
]
```

### 版本识别

模板文件名包含版本号（如 `1.15.x.json`）时，自动按该版本过滤不兼容协议；文件名不含版本号时回退到 `providers.json` 的 `singbox_version`（缺省 1.14）。

优先级：`&version=` 参数 > 模板文件名 > `providers.json`。需要用非模板版本测试时，用 `&version=1.15`（或命令行 `--singbox_version 1.15`）强制指定。

## 部署

### Vercel

1. Fork 本仓库
2. 在 Vercel 导入仓库
3. 部署完成

## 支持的协议

vmess、vless、shadowsocks、trojan、tuic、hysteria、hysteria2、wireguard、socks、http、anytls、shadowtls

## AI 辅助配置生成

项目内置了 sing-box 配置生成 Skill，可配合 AI 助手（如 CodeArts）使用，自动引导生成配置。

### 使用方式

1. 在 AI 助手中加载 `skill/sing-box-config/skill.md`
2. 告诉 AI 你的需求，例如：
   - "帮我生成一个 TUN 模式的 sing-box 1.14 配置，国内直连国外走代理"
   - "我要一个 mixed 系统代理配置，用 FakeIP"
3. AI 会逐步询问你的需求，然后生成完整配置

### Skill 目录结构

```
skill/sing-box-config/
├── skill.md                              # 工作流指令
├── reference.md                          # sing-box 完整配置参考文档
└── examples/                             # 示例配置
    ├── tun-fakeip-cn-direct.json         # TUN + FakeIP + 国内直连
    └── tun-mixed-cn-direct.json          # TUN + Mixed + 国内直连
```
