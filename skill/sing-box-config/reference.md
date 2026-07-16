# sing-box 完整配置文档

> 版本标签说明：`[1.8+]` 表示自 1.8.0 起可用，`[弃用1.14]` 表示在 1.14.0 中弃用，`[移除1.14]` 表示在 1.14.0 中移除。

## 目录

- [基础结构](#基础结构)
- [Log 配置](#log-配置)
- [DNS 配置](#dns-配置)
- [DNS Rule](#dns-rule)
- [DNS Rule Action](#dns-rule-action)
- [FakeIP](#fakeip)
- [NTP 配置](#ntp-配置)
- [Certificate 配置](#certificate-配置)
- [Route 配置](#route-配置)
- [Route Rule Action](#route-rule-action)
- [Protocol Sniff](#protocol-sniff)
- [Rule Set 配置](#rule-set-配置)
- [Experimental 配置](#experimental-配置)
- [Network Namespace](#network-namespace)
- [Endpoint 配置](#endpoint-配置)
- [Inbound 配置](#inbound-配置)
- [Outbound 配置](#outbound-配置)
- [Shared 配置字段](#shared-配置字段)
  - [Listen Fields](#listen-fields)
  - [Dial Fields](#dial-fields)
  - [HTTP Client](#http-client)
  - [Multiplex](#multiplex)
  - [UDP over TCP](#udp-over-tcp)
  - [TCP Brutal](#tcp-brutal)
  - [TLS](#tls)
  - [V2Ray Transport](#v2ray-transport)
  - [Certificate Provider](#certificate-provider)
  - [Wi-Fi State](#wi-fi-state)
  - [Neighbor Resolution](#neighbor-resolution)
- [Service 配置](#service-配置)
- [sing-box 1.14.0 主要变更](#sing-box-1140-主要变更)
- [命令行工具](#命令行工具)

---

## 基础结构

sing-box 使用 JSON 格式进行配置。

```json
{
  "log": {},
  "dns": {},
  "ntp": {},
  "certificate": {},
  "certificate_providers": [],
  "http_clients": [],
  "network_namespaces": [],
  "endpoints": [],
  "inbounds": [],
  "outbounds": [],
  "route": {},
  "services": [],
  "experimental": {}
}
```

### 字段说明

| 字段 | 格式 | 说明 |
|------|------|------|
| `log` | [Log](#log-配置) | 日志配置 |
| `dns` | [DNS](#dns-配置) | DNS 配置 |
| `ntp` | [NTP](#ntp-配置) | NTP 配置 |
| `certificate` | [Certificate](#certificate-配置) | 证书配置 |
| `certificate_providers` | [Certificate Provider](#certificate-provider) | 证书提供者列表 |
| `http_clients` | [HTTP Client](#http-client) | HTTP 客户端列表 |
| `network_namespaces` | [Network Namespace](#network-namespace) | 网络命名空间列表 |
| `endpoints` | [Endpoint](#endpoint-配置) | 端点列表 |
| `inbounds` | [Inbound](#inbound-配置) | 入站列表 |
| `outbounds` | [Outbound](#outbound-配置) | 出站列表 |
| `route` | [Route](#route-配置) | 路由配置 |
| `services` | [Service](#service-配置) | 服务列表 |
| `experimental` | [Experimental](#experimental-配置) | 实验性功能配置 |

---

## Log 配置

### 结构

```json
{
  "log": {
    "disabled": false,
    "level": "info",
    "output": "box.log",
    "timestamp": true
  }
}
```

### 字段

#### disabled

禁用日志，启动后不输出。

#### level

日志级别。可选值：`trace`、`debug`、`info`、`warn`、`error`、`fatal`、`panic`。

#### output

输出文件路径。启用后将不写入控制台。

#### timestamp

为每行添加时间戳。

---

## DNS 配置

### 结构

```json
{
  "dns": {
    "servers": [],
    "rules": [],
    "final": "",
    "strategy": "",
    "disable_cache": false,
    "disable_expire": false,
    "independent_cache": false,
    "cache_capacity": 0,
    "optimistic": false,
    "timeout": "",
    "reverse_mapping": false,
    "client_subnet": "",
    "fakeip": {}
  }
}
```

### 字段

#### servers

DNS 服务器列表。参见 [DNS Server](#dns-server)。

#### rules

DNS 规则列表。参见 [DNS Rule](#dns-rule)。

#### fakeip

FakeIP 配置。参见 [FakeIP](#fakeip)。

#### final

默认 DNS 服务器标签。如果为空，则使用第一个服务器。

#### strategy

默认域名解析策略。可选值：`prefer_ipv4`、`prefer_ipv6`、`ipv4_only`、`ipv6_only`。

#### disable_cache

禁用 DNS 缓存。与 `optimistic` 冲突。

#### disable_expire

禁用 DNS 缓存过期。与 `optimistic` 冲突。

#### independent_cache

[弃用1.14]

使每个 DNS 服务器的缓存独立。如果启用，会略微降低性能。

#### cache_capacity

[1.11+]

LRU 缓存容量。小于 1024 的值将被忽略。

#### optimistic

[1.14+]

启用乐观 DNS 缓存。当缓存的 DNS 条目已过期但仍在超时窗口内时，会立即返回过期响应，同时在后台触发刷新。

与 `disable_cache` 和 `disable_expire` 冲突。

接受布尔值或对象。设置为 `true` 时，使用默认超时 `3d`。

```json
{
  "optimistic": {
    "enabled": true,
    "timeout": "3d"
  }
}
```

##### enabled

启用乐观 DNS 缓存。

##### timeout

过期缓存条目可以乐观服务的最长时间。默认使用 `3d`。

#### timeout

[1.14+]

每个 DNS 查询的默认超时时间。默认使用 `10s`。

可以被 `rules.[].timeout` 或 `domain_resolver.timeout` 覆盖。

#### reverse_mapping

在响应 DNS 查询后存储 IP 地址的反向映射，以便在路由时提供域名。

#### client_subnet

[1.9+]

默认为每个查询追加指定 IP 前缀的 `edns0-subnet` OPT 额外记录。

---

### DNS Server

#### 结构

```json
{
  "dns": {
    "servers": [
      {
        "type": "",
        "tag": ""
      }
    ]
  }
}
```

#### type

DNS 服务器类型。

| 类型 | 格式 | 说明 |
|------|------|------|
| 空（默认） | [Legacy](#legacy) | 传统格式 |
| `local` | [Local](#local) | 本地 DNS |
| `hosts` | [Hosts](#hosts) | Hosts 文件 |
| `tcp` | [TCP](#tcp) | TCP DNS |
| `udp` | [UDP](#udp) | UDP DNS |
| `tls` | [TLS](#tls) | DNS over TLS |
| `quic` | [QUIC](#quic) | DNS over QUIC |
| `https` | [HTTPS](#https) | DNS over HTTPS |
| `h3` | [HTTP/3](#http3) | DNS over HTTP/3 |
| `dhcp` | [DHCP](#dhcp) | DHCP DNS |
| `mdns` | [mDNS](#mdns) | mDNS |
| `fakeip` | [Fake IP](#fake-ip) | Fake IP |
| `tailscale` | [Tailscale](#tailscale) | Tailscale DNS |
| `resolved` | [Resolved](#resolved) | systemd-resolved |

#### tag

DNS 服务器的标签。

---

## DNS Rule

### 结构

```json
{
  "dns": {
    "rules": [
      {
        "inbound": ["mixed-in"],
        "ip_version": 6,
        "query_type": ["A", "AAAA"],
        "network": ["tcp"],
        "auth_user": ["usera"],
        "protocol": ["dns", "http", "quic"],
        "domain": ["test.com"],
        "domain_suffix": [".cn"],
        "domain_keyword": ["test"],
        "domain_regex": ["^stun\\..+"],
        "geosite": ["cn"],
        "source_geoip": ["private"],
        "geoip": ["cn"],
        "source_ip_cidr": ["10.0.0.0/24"],
        "source_ip_is_private": false,
        "ip_cidr": ["10.0.0.0/24"],
        "ip_is_private": false,
        "source_port": [12345],
        "source_port_range": ["1000:2000"],
        "port": [53],
        "port_range": ["1000:2000"],
        "process_name": ["curl"],
        "process_path": ["/usr/bin/curl"],
        "process_path_regex": ["^/usr/bin/.+"],
        "package_name": ["com.termux"],
        "user": ["sekai"],
        "user_id": [1000],
        "clash_mode": "direct",
        "network_type": ["wifi"],
        "network_is_expensive": false,
        "network_is_constrained": false,
        "wifi_ssid": ["My WIFI"],
        "wifi_bssid": ["00:00:00:00:00:00"],
        "rule_set": ["geoip-cn"],
        "rule_set_ip_cidr_match_source": false,
        "invert": false,
        "action": "route",
        "server": ""
      },
      {
        "type": "logical",
        "mode": "and",
        "rules": [],
        "invert": false,
        "action": "route",
        "server": ""
      }
    ]
  }
}
```

### 匹配逻辑

默认规则使用以下匹配逻辑：
(`domain` || `domain_suffix` || `domain_keyword` || `domain_regex` || `geosite`) &&
(`ip_cidr` || `ip_is_private` || `source_ip_cidr` || `source_ip_is_private` || `source_geoip` || `geoip`) &&
(`port` || `port_range`) &&
(`source_port` || `source_port_range`) &&
`other fields`

### 特有字段

#### query_type

匹配 DNS 查询类型。如 `A`、`AAAA`、`MX`、`TXT` 等。

#### match_response

[1.14+]

匹配 DNS 响应而非请求。需要前置 `evaluate` 类型的 DNS Rule Action。

#### server

[弃用1.11]

已移至 [DNS Rule Action](#dns-rule-action)。

---

## DNS Rule Action

[1.11+]

### route

默认动作，将 DNS 请求路由到指定服务器。

```json
{
  "action": "route",
  "server": "",
  "strategy": "",
  "disable_cache": false,
  "disable_optimistic_cache": false,
  "rewrite_ttl": null,
  "timeout": "",
  "client_subnet": null
}
```

#### server

**必填**

目标 DNS 服务器标签。

#### strategy

[1.12+][弃用1.14]

域名解析策略。可选值：`prefer_ipv4`、`prefer_ipv6`、`ipv4_only`、`ipv6_only`。

#### disable_cache

禁用缓存。

#### disable_optimistic_cache

[1.14+]

禁用乐观 DNS 缓存。

#### rewrite_ttl

重写 DNS 响应中的 TTL。

#### timeout

[1.14+]

覆盖 DNS 查询超时。将覆盖 `dns.timeout`。

#### client_subnet

追加 `edns0-subnet` OPT 额外记录。将覆盖 `dns.client_subnet`。

### evaluate

[1.14+]

向指定服务器发送 DNS 查询并保存评估响应，供后续规则通过 `match_response` 匹配。与 `route` 不同，它**不会**终止规则评估。

```json
{
  "action": "evaluate",
  "server": "",
  "disable_cache": false,
  "disable_optimistic_cache": false,
  "rewrite_ttl": null,
  "timeout": "",
  "client_subnet": null
}
```

只允许在顶层 DNS 规则中使用（不能在逻辑子规则内）。

### respond

[1.14+]

终止规则评估并返回前置 `evaluate` 动作的评估响应。

```json
{
  "action": "respond"
}
```

不会发送新的 DNS 查询，没有额外选项。

### route-options

设置路由选项。

```json
{
  "action": "route-options",
  "disable_cache": false,
  "disable_optimistic_cache": false,
  "rewrite_ttl": null,
  "timeout": "",
  "client_subnet": null
}
```

### reject

拒绝 DNS 请求。

```json
{
  "action": "reject",
  "method": "",
  "no_drop": false
}
```

#### method

- `default`：回复 REFUSED
- `drop`：丢弃请求

#### no_drop

如果未启用，30 秒内触发 50 次后，`method` 将被临时覆盖为 `drop`。

### predefined

[1.12+]

使用预定义 DNS 记录响应。

```json
{
  "action": "predefined",
  "rcode": "",
  "answer": [],
  "ns": [],
  "extra": []
}
```

#### rcode

响应代码。可选值：`NOERROR`、`FORMERR`、`SERVFAIL`、`NXDOMAIN`、`NOTIMP`、`REFUSED`。默认 `NOERROR`。

#### answer

作为回答响应的文本 DNS 记录列表。

示例：
- A 记录：`localhost. IN A 127.0.0.1`
- AAAA 记录：`localhost. IN AAAA ::1`
- TXT 记录：`localhost. IN TXT "Hello"`

#### ns

名称服务器记录列表。

#### extra

额外记录列表。

---

## FakeIP

### 结构

```json
{
  "dns": {
    "fakeip": {
      "enabled": false,
      "inet4_range": "198.18.0.0/15",
      "inet6_range": "fc00::/18"
    }
  }
}
```

### 字段

#### enabled

启用 FakeIP 服务。

#### inet4_range

用于 FakeIP 的 IPv4 地址范围。

#### inet6_range

用于 FakeIP 的 IPv6 地址范围。

---

## NTP 配置

内置 NTP 客户端服务。如果启用，它将为 TLS/Shadowsocks/VMess 等协议提供时间，适用于无法进行时间同步的环境。

### 结构

```json
{
  "ntp": {
    "enabled": false,
    "server": "time.apple.com",
    "server_port": 123,
    "interval": "30m",
    ... // Dial Fields
  }
}
```

### 字段

#### enabled

启用 NTP 服务。

#### server

**必填**

NTP 服务器地址。

#### server_port

NTP 服务器端口。默认使用 123。

#### interval

时间同步间隔。默认使用 30 分钟。

### Dial Fields

参见 [Dial Fields](#dial-fields)。

---

## Certificate 配置

[1.12+]

### 结构

```json
{
  "certificate": {
    "store": "",
    "certificate": [],
    "certificate_path": [],
    "certificate_directory_path": []
  }
}
```

### 字段

#### store

默认 X509 受信任 CA 证书列表。

| 类型 | 说明 |
|------|------|
| `system`（默认） | 系统受信任 CA 证书 |
| `mozilla` | Mozilla 包含列表（移除中国 CA 证书） |
| `chrome` | Chrome Root Store（移除中国 CA 证书） |
| `none` | 空列表 |

#### certificate

要信任的证书行数组，PEM 格式。

#### certificate_path

要信任的证书路径，PEM 格式。文件修改后会自动重新加载。

#### certificate_directory_path

搜索要信任证书的目录路径，PEM 格式。文件修改后会自动重新加载。

---

## Route 配置

### 结构

```json
{
  "route": {
    "rules": [],
    "rule_set": [],
    "final": "",
    "auto_detect_interface": false,
    "override_android_vpn": false,
    "default_interface": "",
    "default_mark": 0,
    "find_process": false,
    "find_neighbor": false,
    "dhcp_lease_files": [],
    "default_http_client": "",
    "default_domain_resolver": "",
    "default_network_strategy": "",
    "default_network_type": [],
    "default_fallback_network_type": [],
    "default_fallback_delay": ""
  }
}
```

### 字段

#### rules

路由规则列表。参见 [Route Rule](#route-rule)。

#### rule_set

[1.8+]

规则集列表。参见 [Rule Set](#rule-set-配置)。

#### final

默认出站标签。如果为空，则使用第一个出站。

#### auto_detect_interface

仅支持 Linux、Windows 和 macOS。

默认将出站连接绑定到默认网卡，以防止 tun 下的路由循环。

如果设置了 `outbound.bind_interface` 则无效。

#### override_android_vpn

仅支持 Android。

当启用 `auto_detect_interface` 时，接受 Android VPN 作为上游网卡。

#### default_interface

仅支持 Linux、Windows 和 macOS。

默认将出站连接绑定到指定网卡。

如果设置了 `auto_detect_interface` 则无效。

#### default_mark

仅支持 Linux。

默认设置路由标记。

如果设置了 `outbound.routing_mark` 则无效。

#### find_process

仅支持 Linux、Windows 和 macOS。

当没有 `process_name`、`process_path`、`package_name`、`user` 或 `user_id` 规则时，启用进程搜索以进行日志记录。

#### find_neighbor

[1.14+]

仅支持 Linux 和 macOS。

当没有 `source_mac_address` 或 `source_hostname` 规则时，启用邻居解析以进行日志记录。

参见 [Neighbor Resolution](#neighbor-resolution)。

#### dhcp_lease_files

[1.14+]

仅支持 Linux 和 macOS。

用于主机名和 MAC 地址解析的自定义 DHCP 租约文件路径。

如果为空，则从常见 DHCP 服务器（dnsmasq、odhcpd、ISC dhcpd、Kea）自动检测。

#### default_http_client

[1.14+]

远程规则集使用的默认 [HTTP Client](#http-client) 标签。

如果为空且定义了 `http_clients`，则使用第一个 HTTP 客户端。

#### default_domain_resolver

[1.12+]

参见 [Dial Fields](#dial-fields) 中的 `domain_resolver`。

可以被 `outbound.domain_resolver` 覆盖。

#### default_network_strategy

[1.11+]

参见 [Dial Fields](#dial-fields) 中的 `network_strategy`。

如果设置了 `outbound.bind_interface`、`outbound.inet4_bind_address` 或 `outbound.inet6_bind_address` 则无效。

可以被 `outbound.network_strategy` 覆盖。

与 `default_interface` 冲突。

#### default_network_type

[1.11+]

参见 [Dial Fields](#dial-fields) 中的 `network_type`。

#### default_fallback_network_type

[1.11+]

参见 [Dial Fields](#dial-fields) 中的 `fallback_network_type`。

#### default_fallback_delay

[1.11+]

参见 [Dial Fields](#dial-fields) 中的 `fallback_delay`。

---

### Route Rule

#### 结构

```json
{
  "route": {
    "rules": [
      {
        "inbound": ["mixed-in"],
        "ip_version": 6,
        "network": ["tcp"],
        "auth_user": ["usera", "userb"],
        "protocol": ["tls", "http", "quic"],
        "client": ["chromium", "safari", "firefox", "quic-go"],
        "domain": ["test.com"],
        "domain_suffix": [".cn"],
        "domain_keyword": ["test"],
        "domain_regex": ["^stun\\..+"],
        "geosite": ["cn"],
        "source_geoip": ["private"],
        "geoip": ["cn"],
        "source_ip_cidr": ["10.0.0.0/24", "192.168.0.1"],
        "source_ip_is_private": false,
        "ip_cidr": ["10.0.0.0/24", "192.168.0.1"],
        "ip_is_private": false,
        "source_port": [12345],
        "source_port_range": ["1000:2000", ":3000", "4000:"],
        "port": [80, 443],
        "port_range": ["1000:2000", ":3000", "4000:"],
        "process_name": ["curl"],
        "process_path": ["/usr/bin/curl"],
        "process_path_regex": ["^/usr/bin/.+"],
        "package_name": ["com.termux"],
        "package_name_regex": ["^com\\.termux.*"],
        "user": ["sekai"],
        "user_id": [1000],
        "clash_mode": "direct",
        "network_type": ["wifi"],
        "network_is_expensive": false,
        "network_is_constrained": false,
        "interface_address": {
          "en0": ["2000::/3"]
        },
        "network_interface_address": {
          "wifi": ["2000::/3"]
        },
        "default_interface_address": ["2000::/3"],
        "wifi_ssid": ["My WIFI"],
        "wifi_bssid": ["00:00:00:00:00:00"],
        "preferred_by": ["tailscale", "wireguard"],
        "source_mac_address": ["00:11:22:33:44:55"],
        "source_hostname": ["my-device"],
        "rule_set": ["geoip-cn", "geosite-cn"],
        "rule_set_ip_cidr_match_source": false,
        "invert": false,
        "action": "route",
        "outbound": "direct"
      },
      {
        "type": "logical",
        "mode": "and",
        "rules": [],
        "invert": false,
        "action": "route",
        "outbound": "direct"
      }
    ]
  }
}
```

#### 默认规则匹配逻辑

默认规则使用以下匹配逻辑：
(`domain` || `domain_suffix` || `domain_keyword` || `domain_regex` || `geosite` || `geoip` || `ip_cidr` || `ip_is_private`) &&
(`port` || `port_range`) &&
(`source_geoip` || `source_ip_cidr` || `source_ip_is_private`) &&
(`source_port` || `source_port_range`) &&
`other fields`

#### 字段说明

##### inbound

入站标签列表。

##### ip_version

IP 版本，4 或 6。为空则不限制。

##### auth_user

用户名，参见各入站详情。

##### protocol

嗅探协议，参见 [Protocol Sniff](#protocol-sniff)。

##### client

[1.10+]

嗅探客户端类型，参见 [Protocol Sniff](#protocol-sniff)。

##### network

[1.13+变更]

匹配网络类型：`tcp`、`udp` 或 `icmp`。

自 1.13.0 起，可以通过 `icmp` 网络匹配 ICMP echo（ping）请求。

##### domain

匹配完整域名。

##### domain_suffix

匹配域名后缀。

##### domain_keyword

使用关键字匹配域名。

##### domain_regex

使用正则表达式匹配域名。

##### geosite

[弃用1.8]

匹配 geosite。

##### source_geoip

[弃用1.8]

匹配源 geoip。

##### geoip

[弃用1.8]

匹配 geoip。

##### source_ip_cidr

匹配源 IP CIDR。

##### ip_is_private

[1.8+]

匹配非公共 IP。

##### ip_cidr

匹配 IP CIDR。

##### source_ip_is_private

[1.8+]

匹配非公共源 IP。

##### source_port

匹配源端口。

##### source_port_range

匹配源端口范围。

##### port

匹配端口。

##### port_range

匹配端口范围。

##### process_name

仅支持 Linux、Windows 和 macOS。

匹配进程名。

##### process_path

仅支持 Linux、Windows 和 macOS。

匹配进程路径。

##### process_path_regex

[1.10+]

仅支持 Linux、Windows 和 macOS。

使用正则表达式匹配进程路径。

##### package_name

匹配 Android 包名。

##### package_name_regex

[1.14+]

使用正则表达式匹配 Android 包名。

##### user

仅支持 Linux。

匹配用户名。

##### user_id

仅支持 Linux。

匹配用户 ID。

##### clash_mode

匹配 Clash 模式。

##### network_type

[1.11+]

仅支持 Android 和 Apple 平台的图形客户端。

匹配网络类型。可用值：`wifi`、`cellular`、`ethernet`、`other`。

##### network_is_expensive

[1.11+]

仅支持 Android 和 Apple 平台的图形客户端。

匹配网络是否被视为计量网络（Android）或昂贵网络（Apple 平台）。

##### network_is_constrained

[1.11+]

仅支持 Apple 平台的图形客户端。

匹配网络是否处于低数据模式。

##### interface_address

[1.13+]

仅支持 Linux、Windows 和 macOS。

匹配接口地址。

##### network_interface_address

[1.13+]

仅支持 Android 和 Apple 平台的图形客户端。

匹配网络接口地址。

##### default_interface_address

[1.13+]

仅支持 Linux、Windows 和 macOS。

匹配默认接口地址。

##### wifi_ssid

匹配 WiFi SSID。参见 [Wi-Fi State](#wi-fi-state)。

##### wifi_bssid

匹配 WiFi BSSID。参见 [Wi-Fi State](#wi-fi-state)。

##### preferred_by

[1.13+]

匹配指定出站的首选路由。

| 类型 | 匹配 |
|------|------|
| `tailscale` | 匹配 MagicDNS 域名和对等端的允许 IP |
| `wireguard` | 匹配对等端的允许 IP |

##### source_mac_address

[1.14+]

仅支持 Linux、macOS 或 Android 和 macOS 的图形客户端。参见 [Neighbor Resolution](#neighbor-resolution)。

匹配源设备 MAC 地址。

##### source_hostname

[1.14+]

仅支持 Linux、macOS 或 Android 和 macOS 的图形客户端。参见 [Neighbor Resolution](#neighbor-resolution)。

从 DHCP 租约匹配源设备主机名。

##### rule_set

[1.8+]

匹配规则集。

##### rule_set_ip_cidr_match_source

[1.10+]

使规则集中的 `ip_cidr` 匹配源 IP。

##### invert

反转匹配结果。

##### action

**必填**

参见 [Route Rule Action](#route-rule-action)。

##### outbound

[弃用1.11]

已移至 [Route Rule Action](#route-rule-action)。

#### 逻辑规则字段

##### type

`logical`

##### mode

**必填**

`and` 或 `or`

##### rules

**必填**

包含的规则列表。

---

## Route Rule Action

### 终止动作

#### route

```json
{
  "action": "route",
  "outbound": "",
  ... // route-options Fields
}
```

`route` 继承经典规则行为，将连接路由到指定出站。

##### outbound

**必填**

目标出站标签。

#### bypass

[1.13+]

仅支持 Linux 且启用了 `auto_redirect`。

```json
{
  "action": "bypass",
  "outbound": "",
  ... // route-options Fields
}
```

`bypass` 在内核级别绕过 sing-box 的 auto redirect 连接。

对于非 auto-redirect 连接和已建立的连接，如果指定了 `outbound`，行为与 `route` 相同；否则跳过该规则。

##### outbound

目标出站标签。如果未指定，该规则仅在 auto redirect 的 pre-match 中匹配。

#### reject

[1.13+变更]

自 1.13.0 起，可以使用 `reject` 动作拒绝（或直接回复）ICMP echo（ping）请求。

```json
{
  "action": "reject",
  "method": "default",
  "no_drop": false
}
```

##### method

对于 TCP 和 UDP 连接：
- `default`：TCP 回复 RST，UDP 回复 ICMP port unreachable
- `drop`：丢弃数据包

对于 ICMP echo 请求：
- `default`：回复 ICMP host unreachable
- `drop`：丢弃数据包
- `reply`：回复 ICMP echo reply

##### no_drop

如果未启用，30 秒内触发 50 次后，`method` 将被临时覆盖为 `drop`。`method` 为 `drop` 时不可用。

#### hijack-dns

```json
{
  "action": "hijack-dns"
}
```

`hijack-dns` 劫持 DNS 请求到 sing-box DNS 模块。

### 非终止动作

#### route-options

```json
{
  "action": "route-options",
  "override_address": "",
  "override_port": 0,
  "network_strategy": "",
  "network_type": [],
  "fallback_network_type": [],
  "fallback_delay": "",
  "udp_disable_domain_unmapping": false,
  "udp_connect": false,
  "udp_timeout": "",
  "tls_fragment": false,
  "tls_fragment_fallback_delay": "",
  "tls_record_fragment": "",
  "tls_spoof": "",
  "tls_spoof_method": ""
}
```

`route-options` 设置路由选项。

##### override_address

覆盖连接目标地址。

##### override_port

覆盖连接目标端口。

##### network_strategy

参见 [Dial Fields](#dial-fields) 中的 `network_strategy`。仅在出站为 direct 且未设置 `bind_interface` 等时生效。

##### network_type

参见 [Dial Fields](#dial-fields) 中的 `network_type`。

##### fallback_network_type

参见 [Dial Fields](#dial-fields) 中的 `fallback_network_type`。

##### fallback_delay

参见 [Dial Fields](#dial-fields) 中的 `fallback_delay`。

##### udp_disable_domain_unmapping

如果启用，对于以域名寻址的 UDP 代理请求，将在响应中发送原始数据包地址而非映射域名。

##### udp_connect

如果启用，尝试将 UDP 连接连接到目标而不是监听。

##### udp_timeout

UDP 连接超时。

默认值（按嗅探协议）：

| 超时 | 协议 |
|------|------|
| `10s` | `dns`、`ntp`、`stun` |
| `30s` | `quic`、`dtls` |

##### tls_fragment

[1.12+]

分片 TLS 握手以绕过防火墙。此功能旨在绕过基于明文数据包匹配的简单防火墙。

由于性能较差，优先尝试 `tls_record_fragment`，仅应用于已知被阻止的服务器名称。

##### tls_fragment_fallback_delay

[1.12+]

TLS 分片无法自动确定等待时间时的回退值。默认 `500ms`。

##### tls_record_fragment

[1.12+]

将 TLS 握手分片为多个 TLS 记录以绕过防火墙。

##### tls_spoof

[1.14+]

仅支持 Linux、macOS 和 Windows，需要提升权限。

在真实 ClientHello 之前注入携带此 SNI 的伪造 TLS ClientHello，以欺骗 SNI 过滤中间件。

##### tls_spoof_method

[1.14+]

伪造段如何被真实服务器拒绝。参见出站 TLS `spoof_method`。

#### sniff

```json
{
  "action": "sniff",
  "sniffer": [],
  "timeout": ""
}
```

`sniff` 对连接执行协议嗅探。

##### sniffer

启用的嗅探器。默认启用所有嗅探器。可用值参见 [Protocol Sniff](#protocol-sniff)。

##### timeout

嗅探超时。默认 `300ms`。

#### resolve

```json
{
  "action": "resolve",
  "server": "",
  "strategy": "",
  "disable_cache": false,
  "disable_optimistic_cache": false,
  "rewrite_ttl": null,
  "timeout": "",
  "client_subnet": null
}
```

`resolve` 将请求目标从域名解析为 IP 地址。

##### server

指定 DNS 服务器标签。

##### strategy

DNS 解析策略。可选值：`prefer_ipv4`、`prefer_ipv6`、`ipv4_only`、`ipv6_only`。

##### disable_cache

[1.12+]

禁用缓存。

##### disable_optimistic_cache

[1.14+]

禁用乐观 DNS 缓存。

##### rewrite_ttl

[1.12+]

重写 DNS 响应中的 TTL。

##### timeout

[1.14+]

覆盖 DNS 查询超时。将覆盖 `dns.timeout`。

##### client_subnet

[1.12+]

追加 `edns0-subnet` OPT 额外记录。将覆盖 `dns.client_subnet`。

---

## Protocol Sniff

### 可用协议

| 协议 | 说明 |
|------|------|
| `http` | HTTP 请求 |
| `tls` | TLS ClientHello |
| `quic` | QUIC 初始包 |
| `dns` | DNS 查询 |
| `stun` | STUN 消息 |
| `ntp` | NTP 包 |

### 可用客户端类型

[1.10+]

| 客户端 | 说明 |
|--------|------|
| `chromium` | Chromium 内核浏览器 |
| `safari` | Safari 浏览器 |
| `firefox` | Firefox 浏览器 |
| `quic-go` | quic-go 库 |

---

## Rule Set 配置

[1.8+]

### 结构

#### 内联规则集（自 sing-box 1.10.0 起）

```json
{
  "type": "inline",
  "tag": "",
  "rules": []
}
```

#### 本地文件规则集

```json
{
  "type": "local",
  "tag": "",
  "format": "source",
  "path": ""
}
```

#### 远程文件规则集

如果启用 `experimental.cache_file.enabled`，远程规则集将被缓存。

```json
{
  "type": "remote",
  "tag": "",
  "format": "source",
  "url": "",
  "http_client": "",
  "update_interval": "",
  "download_detour": ""
}
```

### 字段

#### type

**必填**

规则集类型：`inline`、`local` 或 `remote`。

#### tag

**必填**

规则集标签。

### 内联字段

[1.10+]

#### rules

**必填**

[Headless Rule](#headless-rule) 列表。

### 本地或远程字段

#### format

**必填**

规则集文件格式：`source` 或 `binary`。

当 `path` 或 `url` 使用 `json` 或 `srs` 扩展名时可选。

### 本地字段

#### path

**必填**

规则集文件路径。自 sing-box 1.10.0 起，文件修改后会自动重新加载。

### 远程字段

#### url

**必填**

规则集下载 URL。

#### http_client

[1.14+]

用于下载规则集的 HTTP 客户端。

参见 [HTTP Client](#http-client)。

为空时使用默认 HTTP 客户端。

#### update_interval

规则集更新间隔。为空则使用 `1d`。

#### download_detour

[弃用1.14]

下载规则集的出站标签。

---

## Experimental 配置

### 结构

```json
{
  "experimental": {
    "cache_file": {},
    "clash_api": {},
    "v2ray_api": {}
  }
}
```

### 字段

| 键 | 格式 |
|------|------|
| `cache_file` | [Cache File](#cache-file) |
| `clash_api` | [Clash API](#clash-api) |
| `v2ray_api` | [V2Ray API](#v2ray-api) |

### Cache File

```json
{
  "cache_file": {
    "enabled": false,
    "path": "",
    "cache_id": "",
    "store_fakeip": false,
    "store_rdrc": false,
    "rdrc_timeout": ""
  }
}
```

#### enabled

启用缓存文件。

#### path

缓存文件路径。默认使用 `cache.db`。

#### cache_id

缓存 ID。用于区分不同配置的缓存。

#### store_fakeip

将 FakeIP 映射存储到缓存文件中。

#### store_rdrc

[1.10+]

将拒绝的 DNS 响应缓存存储到缓存文件中。

#### rdrc_timeout

[1.10+]

拒绝的 DNS 响应缓存超时。默认使用 `7d`。

### Clash API

```json
{
  "clash_api": {
    "external_controller": "",
    "external_ui": "",
    "external_ui_download_detour": "",
    "external_ui_download_url": "",
    "secret": "",
    "default_mode": ""
  }
}
```

#### external_controller

RESTful API 监听地址。

#### external_ui

外部 UI 目录路径。

#### secret

RESTful API 密钥。

#### default_mode

默认 Clash 模式。可选值：`direct`、`rule`、`global`。

### V2Ray API

```json
{
  "v2ray_api": {
    "listen": "",
    "stats": {},
    "observatory": {}
  }
}
```

---

## Network Namespace

[1.14+]

仅支持 Linux。

网络命名空间允许入站和出站在独立的 Linux 网络命名空间内运行，通过标签从 [tun](#tun-inbound)、[Listen Fields](#listen-fields) 和 [Dial Fields](#dial-fields) 中引用。

### 结构

```json
{
  "network_namespaces": [
    {
      "type": "",
      "tag": ""
    }
  ]
}
```

### 字段

#### type

网络命名空间类型。默认使用 `default`。

| 类型 | 格式 |
|------|------|
| `default` | [Default](#default) |
| `unshare` | [Unshare](#unshare) |

#### tag

**必填**

网络命名空间的标签。

### Default

使用默认网络命名空间。

### Unshare

创建新的网络命名空间（使用 Linux unshare）。

---

## Endpoint 配置

[1.11+]

端点是具有入站和出站行为的协议。

### 结构

```json
{
  "endpoints": [
    {
      "type": "",
      "tag": ""
    }
  ]
}
```

### 字段

| 类型 | 格式 |
|------|------|
| `wireguard` | [WireGuard](#wireguard-endpoint) |
| `tailscale` | [Tailscale](#tailscale-endpoint) |

#### tag

端点的标签。

---

## Inbound 配置

### 结构

```json
{
  "inbounds": [
    {
      "type": "",
      "tag": ""
    }
  ]
}
```

### 字段

| 类型 | 格式 | 可注入 |
|------|------|--------|
| `direct` | [Direct](#direct-inbound) | |
| `mixed` | [Mixed](#mixed-inbound) | TCP |
| `socks` | [SOCKS](#socks-inbound) | TCP |
| `http` | [HTTP](#http-inbound) | TCP |
| `shadowsocks` | [Shadowsocks](#shadowsocks-inbound) | TCP |
| `vmess` | [VMess](#vmess-inbound) | TCP |
| `trojan` | [Trojan](#trojan-inbound) | TCP |
| `naive` | [Naive](#naive-inbound) | |
| `hysteria` | [Hysteria](#hysteria-inbound) | |
| `shadowtls` | [ShadowTLS](#shadowtls-inbound) | TCP |
| `tuic` | [TUIC](#tuic-inbound) | |
| `hysteria2` | [Hysteria2](#hysteria2-inbound) | |
| `vless` | [VLESS](#vless-inbound) | TCP |
| `anytls` | [AnyTLS](#anytls-inbound) | TCP |
| `snell` | [Snell](#snell-inbound) | TCP |
| `tun` | [Tun](#tun-inbound) | |
| `redirect` | [Redirect](#redirect-inbound) | |
| `tproxy` | [TProxy](#tproxy-inbound) | |
| `cloudflared` | [Cloudflared](#cloudflared-inbound) | |

#### tag

入站的标签。

---

### Mixed Inbound

`mixed` 入站是 socks4、socks4a、socks5 和 http 服务器。

#### 结构

```json
{
  "type": "mixed",
  "tag": "mixed-in",
  ... // Listen Fields
  "users": [
    {
      "username": "admin",
      "password": "admin"
    }
  ],
  "set_system_proxy": false
}
```

#### 字段

##### users

SOCKS 和 HTTP 用户。为空则不需要认证。

##### set_system_proxy

仅支持 Linux、Android、Windows 和 macOS。

启动时自动设置系统代理配置，停止时清理。

---

### Tun Inbound

仅支持 Linux、Windows 和 macOS。

#### 结构

```json
{
  "type": "tun",
  "tag": "tun-in",
  "interface_name": "tun0",
  "address": [
    "172.18.0.1/30",
    "fdfe:dcba:9876::1/126"
  ],
  "mtu": 9000,
  "dns_mode": "hijack",
  "dns_address": [
    "172.18.0.2",
    "fdfe:dcba:9876::2"
  ],
  "auto_route": true,
  "iproute2_table_index": 2022,
  "iproute2_rule_index": 9000,
  "auto_redirect": true,
  "auto_redirect_input_mark": "0x2023",
  "auto_redirect_output_mark": "0x2024",
  "auto_redirect_reset_mark": "0x2025",
  "auto_redirect_nfqueue": 100,
  "auto_redirect_iproute2_fallback_rule_index": 32768,
  "exclude_mptcp": false,
  "loopback_address": ["10.7.0.1"],
  "strict_route": true,
  "route_address": [
    "0.0.0.0/1",
    "128.0.0.0/1",
    "::/1",
    "8000::/1"
  ],
  "route_exclude_address": [
    "192.168.0.0/16",
    "fc00::/7"
  ],
  "route_address_set": ["geoip-cloudflare"],
  "route_exclude_address_set": ["geoip-cn"],
  "endpoint_independent_nat": false,
  "udp_timeout": "5m",
  "stack": "system",
  "include_interface": ["lan0"],
  "exclude_interface": ["lan1"],
  "include_uid": [0],
  "include_uid_range": ["1000:99999"],
  "exclude_uid": [1000],
  "exclude_uid_range": ["1000:99999"],
  "include_android_user": [0, 10],
  "include_package": ["com.android.chrome"],
  "exclude_package": ["com.android.captiveportallogin"],
  "include_mac_address": ["00:11:22:33:44:55"],
  "exclude_mac_address": ["66:77:88:99:aa:bb"],
  "platform": {
    "http_proxy": {
      "enabled": false,
      "server": "127.0.0.1",
      "server_port": 8080,
      "bypass_domain": [],
      "match_domain": []
    }
  },
  ... // Listen Fields
}
```

#### 主要字段

##### interface_name

虚拟设备名称，为空则自动选择。

##### address

[1.10+]

tun 接口的 IPv4 和 IPv6 前缀。

##### mtu

最大传输单元。

##### dns_mode

[1.14+]

TUN 接口上 DNS 的处理方式。

| 模式 | 说明 |
|------|------|
| `disabled` | 不配置原生 DNS，也不劫持 DNS 流量 |
| `native` | 尽可能设置平台原生接口 DNS |
| `hijack` | 与 `native` 相同，并额外劫持端口 53（默认） |

##### dns_address

[1.14+]

`dns_mode` 使用的 DNS 服务器地址列表。

##### auto_route

设置到 Tun 的默认路由。

##### auto_redirect

[1.10+]

仅支持 Linux 且启用了 `auto_route`。

使用 nftables 改进 TUN 路由和性能。

##### strict_route

启用 `auto_route` 时强制严格路由规则。

##### stack

TCP/IP 栈。

| 栈 | 说明 |
|------|------|
| `system` | 使用系统网络栈进行 L3 到 L4 转换 |
| `gvisor` | 使用 gVisor 虚拟网络栈 |
| `mixed` | 混合 `system` TCP 栈和 `gvisor` UDP 栈 |

默认使用 `mixed` 栈（如果启用 gVisor 构建标签），否则默认使用 `system` 栈。

##### include_interface / exclude_interface

接口规则仅支持 Linux 且需要 auto_route。

限制/排除路由中的接口。

##### include_uid / exclude_uid

UID 规则仅支持 Linux 且需要 auto_route。

限制/排除路由中的用户。

##### include_package / exclude_package

限制/排除路由中的 Android 包。

##### include_mac_address / exclude_mac_address

[1.14+]

仅支持 Linux 且启用了 `auto_route` 和 `auto_redirect`。

限制/排除路由中的 MAC 地址。

---

## Outbound 配置

### 结构

```json
{
  "outbounds": [
    {
      "type": "",
      "tag": ""
    }
  ]
}
```

### 字段

| 类型 | 格式 |
|------|------|
| `direct` | [Direct](#direct-outbound) |
| `bridge` | [Bridge](#bridge-outbound) |
| `block` | [Block](#block-outbound) |
| `socks` | [SOCKS](#socks-outbound) |
| `http` | [HTTP](#http-outbound) |
| `shadowsocks` | [Shadowsocks](#shadowsocks-outbound) |
| `vmess` | [VMess](#vmess-outbound) |
| `trojan` | [Trojan](#trojan-outbound) |
| `naive` | [NaiveProxy](#naive-outbound) |
| `wireguard` | [WireGuard](#wireguard-outbound) |
| `hysteria` | [Hysteria](#hysteria-outbound) |
| `shadowtls` | [ShadowTLS](#shadowtls-outbound) |
| `vless` | [VLESS](#vless-outbound) |
| `tuic` | [TUIC](#tuic-outbound) |
| `hysteria2` | [Hysteria2](#hysteria2-outbound) |
| `anytls` | [AnyTLS](#anytls-outbound) |
| `snell` | [Snell](#snell-outbound) |
| `tor` | [Tor](#tor-outbound) |
| `ssh` | [SSH](#ssh-outbound) |
| `dns` | [DNS](#dns-outbound) |
| `selector` | [Selector](#selector-outbound) |
| `urltest` | [URLTest](#urltest-outbound) |

#### tag

出站的标签。

---

### Shadowsocks Outbound

#### 结构

```json
{
  "type": "shadowsocks",
  "tag": "ss-out",
  "server": "127.0.0.1",
  "server_port": 1080,
  "method": "2022-blake3-aes-128-gcm",
  "password": "8JCsPssfgS8tiRwiMlhARg==",
  "plugin": "",
  "plugin_opts": "",
  "network": "udp",
  "udp_over_tcp": false,
  "multiplex": {},
  ... // Dial Fields
}
```

#### 字段

##### server

**必填**

服务器地址。

##### server_port

**必填**

服务器端口。

##### method

**必填**

加密方法：

- `2022-blake3-aes-128-gcm`
- `2022-blake3-aes-256-gcm`
- `2022-blake3-chacha20-poly1305`
- `none`
- `aes-128-gcm`
- `aes-192-gcm`
- `aes-256-gcm`
- `chacha20-ietf-poly1305`
- `xchacha20-ietf-poly1305`

传统加密方法：

- `aes-128-ctr`
- `aes-192-ctr`
- `aes-256-ctr`
- `aes-128-cfb`
- `aes-192-cfb`
- `aes-256-cfb`
- `rc4-md5`
- `chacha20-ietf`
- `xchacha20`

##### password

**必填**

Shadowsocks 密码。

##### plugin

Shadowsocks SIP003 插件，内部实现。仅支持 `obfs-local` 和 `v2ray-plugin`。

##### plugin_opts

Shadowsocks SIP003 插件选项。

##### network

启用网络：`tcp` 或 `udp`。默认两者都启用。

##### udp_over_tcp

UDP over TCP 配置。参见 [UDP over TCP](#udp-over-tcp)。

与 `multiplex` 冲突。

##### multiplex

参见 [Multiplex](#multiplex)。

---

## Shared 配置字段

### Listen Fields

#### 结构

```json
{
  "listen": "",
  "listen_port": 0,
  "bind_interface": "",
  "routing_mark": 0,
  "reuse_addr": false,
  "netns": "",
  "tcp_fast_open": false,
  "tcp_multi_path": false,
  "disable_tcp_keep_alive": false,
  "tcp_keep_alive": "",
  "tcp_keep_alive_interval": "",
  "udp_fragment": false,
  "udp_timeout": "",
  "detour": ""
}
```

#### 字段

##### listen

**必填**

监听地址。

##### listen_port

监听端口。

##### bind_interface

[1.12+]

要绑定的网络接口。

##### routing_mark

[1.12+]

仅支持 Linux。

设置 netfilter 路由标记。支持整数（如 `1234`）和字符串十六进制（如 `"0x1234"`）。

##### reuse_addr

[1.12+]

重用监听器地址。

##### netns

[1.12+]

仅支持 Linux。

设置网络命名空间，名称或路径。

自 sing-box 1.14.0 起，也可以使用 [Network Namespace](#network-namespace) 的标签。

##### tcp_fast_open

启用 TCP Fast Open。

##### tcp_multi_path

需要 Go 1.21。

启用 TCP Multi Path。

##### disable_tcp_keep_alive

[1.13+]

禁用 TCP keep alive。

##### tcp_keep_alive

[1.13+]

默认值从 `10m` 改为 `5m`。

TCP keep alive 初始周期。默认使用 `5m`。

##### tcp_keep_alive_interval

TCP keep alive 间隔。默认使用 `75s`。

##### udp_fragment

启用 UDP 分片。

##### udp_timeout

UDP NAT 过期时间。默认使用 `5m`。

##### detour

如果设置，连接将被转发到指定的入站。

---

### Dial Fields

#### 结构

```json
{
  "detour": "",
  "bind_interface": "",
  "inet4_bind_address": "",
  "inet6_bind_address": "",
  "bind_address_no_port": false,
  "routing_mark": 0,
  "reuse_addr": false,
  "netns": "",
  "connect_timeout": "",
  "tcp_fast_open": false,
  "tcp_multi_path": false,
  "disable_tcp_keep_alive": false,
  "tcp_keep_alive": "",
  "tcp_keep_alive_interval": "",
  "udp_fragment": false,
  "domain_resolver": "",
  "network_strategy": "",
  "network_type": [],
  "fallback_network_type": [],
  "fallback_delay": "",
  "domain_strategy": ""
}
```

#### 字段

##### detour

上游出站的标签。如果启用，将忽略所有其他字段。

##### bind_interface

要绑定的网络接口。

##### inet4_bind_address

要绑定的 IPv4 地址。

##### inet6_bind_address

要绑定的 IPv6 地址。

##### bind_address_no_port

[1.13+]

仅支持 Linux。

绑定源地址时不保留端口。

##### routing_mark

仅支持 Linux。

设置 netfilter 路由标记。支持整数（如 `1234`）和字符串十六进制（如 `"0x1234"`）。

##### reuse_addr

重用监听器地址。

##### netns

[1.12+]

仅支持 Linux。

设置网络命名空间，名称或路径。

自 sing-box 1.14.0 起，也可以使用 [Network Namespace](#network-namespace) 的标签。

##### connect_timeout

连接超时，采用 golang 的 Duration 格式。

##### tcp_fast_open

启用 TCP Fast Open。

##### tcp_multi_path

需要 Go 1.21。

启用 TCP Multi Path。

##### disable_tcp_keep_alive

[1.13+]

禁用 TCP keep alive。

##### tcp_keep_alive

[1.13+]

默认值从 `10m` 改为 `5m`。

TCP keep alive 初始周期。默认使用 `5m`。

##### tcp_keep_alive_interval

[1.13+]

TCP keep alive 间隔。默认使用 `75s`。

##### udp_fragment

启用 UDP 分片。

##### domain_resolver

[1.14+]

设置用于解析域名的域名解析器。

此选项使用与 [DNS Rule Action](#dns-rule-action) 相同的格式（不含 `action` 字段）。

将此选项直接设置为字符串等同于设置此选项的 `server`。

##### network_strategy

[1.11+]

仅支持 Android 和 Apple 平台的图形客户端且启用了 `auto_detect_interface`。

选择网络接口的策略。

可用值：

- `default`（默认）：按顺序连接默认网络或 `network_type` 中指定的网络。
- `hybrid`：同时连接所有网络或 `network_type` 中指定的网络。
- `fallback`：同时连接默认网络或 `network_type` 中指定的首选网络，不可用或超时时尝试回退网络。

与 `bind_interface`、`inet4_bind_address` 和 `inet6_bind_address` 冲突。

##### network_type

[1.11+]

仅支持 Android 和 Apple 平台的图形客户端且启用了 `auto_detect_interface`。

使用 `default` 或 `hybrid` 网络策略时的网络类型，或使用 `fallback` 网络策略时的首选网络类型。

可用值：`wifi`、`cellular`、`ethernet`、`other`。

默认使用设备默认网络。

##### fallback_network_type

[1.11+]

仅支持 Android 和 Apple 平台的图形客户端且启用了 `auto_detect_interface`。

使用 `fallback` 网络策略时，首选网络不可用或超时时的回退网络类型。

默认使用除首选外的所有其他网络。

##### fallback_delay

[1.11+]

仅支持 Android 和 Apple 平台的图形客户端且启用了 `auto_detect_interface`。

在生成 RFC 6555 快速回退连接之前等待的时间长度。

对于 `domain_strategy`，是在假设 IPv4/IPv6 配置错误并回退到其他类型地址之前等待连接成功的时间。

对于 `network_strategy`，是在回退到其他接口之前等待连接成功的时间。

仅在设置 `domain_strategy` 或 `network_strategy` 时生效。

默认使用 `300ms`。

##### domain_strategy

[弃用1.12]

可用值：`prefer_ipv4`、`prefer_ipv6`、`ipv4_only`、`ipv6_only`。

如果设置，请求的域名将在连接前解析为 IP。

---

### HTTP Client

[1.14+]

### 结构

字符串或对象。

当为字符串时，为顶层 `http_clients` 中定义的共享 [HTTP Client](#http-client) 标签。

当为对象时：

```json
{
  "engine": "",
  "version": 0,
  "disable_version_fallback": false,
  "headers": {},

  ... // HTTP2 Fields

  "tls": {},

  ... // Dial Fields
}
```

### 字段

#### engine

HTTP 引擎。可选值：`go`（默认）、`apple`。

`apple` 使用 NSURLSession，仅在 Apple 平台可用。

#### version

HTTP 版本。可选值：`1`、`2`、`3`。默认使用 `2`。

当为 `3` 时，HTTP2 Fields 被 QUIC Fields 替代。

#### disable_version_fallback

禁用自动回退到较低的 HTTP 版本。

#### headers

自定义 HTTP 头。`Host` 头用作请求主机。

### HTTP2 Fields

当 `version` 为 `2`（默认）时。参见 [HTTP2 Fields](#http2-fields)。

### QUIC Fields

当 `version` 为 `3` 时。参见 [QUIC Fields](#quic-fields)。

### TLS Fields

参见 [TLS](#tls)。

### Dial Fields

参见 [Dial Fields](#dial-fields)。

---

### Multiplex

#### 入站

```json
{
  "enabled": true,
  "padding": false,
  "brutal": {}
}
```

#### 出站

```json
{
  "enabled": true,
  "protocol": "smux",
  "max_connections": 4,
  "min_streams": 4,
  "max_streams": 0,
  "padding": false,
  "brutal": {}
}
```

#### 入站字段

##### enabled

启用多路复用支持。

##### padding

如果启用，将拒绝非填充连接。

##### brutal

参见 [TCP Brutal](#tcp-brutal)。

#### 出站字段

##### enabled

启用多路复用。

##### protocol

多路复用协议。

| 协议 | 说明 |
|------|------|
| `smux` | https://github.com/xtaci/smux |
| `yamux` | https://github.com/hashicorp/yamux |
| `h2mux` | https://golang.org/x/net/http2 |

默认使用 `h2mux`。

##### max_connections

最大连接数。与 `max_streams` 冲突。

##### min_streams

在打开新连接之前，连接中的最小多路复用流数。与 `max_streams` 冲突。

##### max_streams

在打开新连接之前，连接中的最大多路复用流数。与 `max_connections` 和 `min_streams` 冲突。

##### padding

启用填充。需要 sing-box 服务端版本 1.3-beta9 或更高。

##### brutal

参见 [TCP Brutal](#tcp-brutal)。

---

### UDP over TCP

```json
{
  "enabled": true,
  "version": 2
}
```

#### enabled

启用 UDP over TCP。

#### version

UDP over TCP 协议版本。可选值：`1`、`2`。默认使用 `2`。

---

### TCP Brutal

```json
{
  "enabled": true,
  "up_mbps": 100,
  "down_mbps": 100
}
```

#### enabled

启用 TCP Brutal。

#### up_mbps

上传带宽，单位 Mbps。

#### down_mbps

下载带宽，单位 Mbps。

---

### TLS

#### 出站 TLS

```json
{
  "tls": {
    "enabled": true,
    "server_name": "",
    "insecure": false,
    "alpn": [],
    "min_version": "",
    "max_version": "",
    "cipher_suites": [],
    "curve_preferences": [],
    "certificate": [],
    "certificate_path": [],
    "disable_sni": false,
    "utls": {
      "enabled": true,
      "fingerprint": ""
    },
    "reality": {
      "enabled": true,
      "public_key": "",
      "short_id": ""
    },
    "ech": {
      "enabled": true,
      "config": [],
      "pq_signature_schemes_enabled": false,
      "dynamic_record_sizing_disabled": false
    },
    "spoof": "",
    "spoof_method": ""
  }
}
```

##### enabled

启用 TLS。

##### server_name

服务器名称。

##### insecure

允许不安全连接。

##### alpn

TLS ALPN 协议列表。

##### disable_sni

禁用 SNI 扩展。

##### utls

uTLS 指纹模拟。

###### fingerprint

uTLS 指纹。常见值：`chrome`、`firefox`、`safari`、`ios`、`random`、`randomized`。

##### reality

REALITY 协议配置。

###### public_key

REALITY 公钥。

###### short_id

REALITY 短 ID。

##### ech

Encrypted Client Hello 配置。

##### spoof

[1.14+]

注入伪造的 TLS ClientHello 以欺骗 SNI 过滤中间件。

##### spoof_method

[1.14+]

伪造段如何被真实服务器拒绝。

---

### V2Ray Transport

V2Ray 传输层配置，用于 VMess、VLESS 等协议。

```json
{
  "type": "",
  "host": [],
  "path": "",
  "method": "",
  "headers": {},
  "service_name": "",
  "idle_timeout": "",
  "ping_timeout": ""
}
```

#### type

传输类型。可选值：`http`、`ws`、`quic`、`grpc`、`httpupgrade`。

---

### Certificate Provider

证书提供者列表。

| 类型 | 格式 |
|------|------|
| `acme` | [ACME](#acme) |
| `tailscale` | [Tailscale Certificate](#tailscale-certificate) |
| `cloudflare` | [Cloudflare Origin CA](#cloudflare-origin-ca) |

---

### Wi-Fi State

用于 `wifi_ssid` 和 `wifi_bssid` 规则字段的 Wi-Fi 状态信息。

仅支持 Android 和 Apple 平台的图形客户端。

---

### Neighbor Resolution

[1.14+]

仅支持 Linux 和 macOS。

邻居解析功能用于将源 MAC 地址和主机名映射到 IP 地址，供 `source_mac_address` 和 `source_hostname` 规则使用。

数据来源：
1. ARP/NDP 缓存
2. DHCP 租约文件（通过 `route.dhcp_lease_files` 配置）

---

## Service 配置

### 结构

```json
{
  "services": [
    {
      "type": "",
      "tag": ""
    }
  ]
}
```

### 字段

| 类型 | 格式 | 说明 |
|------|------|------|
| `api` | [sing-box API](#sing-box-api) | sing-box API 服务 |
| `derp` | [DERP](#derp) | DERP 中继服务 |
| `resolved` | [Resolved](#resolved-service) | systemd-resolved 服务 |
| `ssm-api` | [SSM API](#ssm-api) | SSM API 服务 |
| `ccm` | [CCM](#ccm) | CCM 服务 |
| `ocm` | [OCM](#ocm) | OCM 服务 |
| `hysteria-realm` | [Hysteria Realm](#hysteria-realm) | Hysteria Realm 服务 |
| `usbip-server` | [USB/IP Server](#usbip-server) | USB/IP 服务端 |
| `usbip-client` | [USB/IP Client](#usbip-client) | USB/IP 客户端 |

#### tag

服务的标签。

---

## sing-box 1.14.0 主要变更

### 新增功能

1. **DNS 配置**
   - 新增 `optimistic` 乐观 DNS 缓存
   - 新增 `timeout` 默认 DNS 查询超时

2. **DNS Rule Action**
   - 新增 `evaluate` 动作（评估 DNS 响应供后续规则匹配）
   - 新增 `respond` 动作（返回评估的 DNS 响应）
   - 新增 `disable_optimistic_cache` 禁用乐观缓存
   - 新增 `timeout` 覆盖查询超时
   - 弃用 `strategy` 字段

3. **Route 配置**
   - 新增 `default_http_client` 默认 HTTP 客户端
   - 新增 `find_neighbor` 邻居解析
   - 新增 `dhcp_lease_files` DHCP 租约文件

4. **Route Rule Action**
   - 新增 `tls_spoof` 伪造 TLS ClientHello
   - 新增 `tls_spoof_method` 伪造方法
   - 新增 `resolve.disable_optimistic_cache` 禁用乐观缓存
   - 新增 `resolve.timeout` 覆盖查询超时

5. **Route Rule**
   - 新增 `source_mac_address` 源 MAC 地址匹配
   - 新增 `source_hostname` 源主机名匹配
   - 新增 `package_name_regex` 包名正则匹配

6. **Tun Inbound**
   - 新增 `dns_mode` DNS 处理模式
   - 新增 `dns_address` DNS 服务器地址
   - 新增 `include_mac_address` / `exclude_mac_address` MAC 地址过滤

7. **Rule Set**
   - 新增 `http_client` HTTP 客户端配置
   - 弃用 `download_detour`

8. **Dial Fields**
   - 新增 `domain_resolver` 域名解析器

9. **Listen Fields**
   - `netns` 支持引用 Network Namespace 标签

10. **Network Namespace**
    - 全新功能，支持独立的 Linux 网络命名空间

11. **HTTP Client**
    - 全新共享配置，用于远程规则集和 DNS over HTTPS

### 弃用项目

1. `dns.independent_cache` - 将在 1.14.0 中移除
2. `rule_set.download_detour` - 将在 1.16.0 中移除
3. `dial_fields.domain_strategy` - 将在 1.14.0 中移除
4. `dns_rule_action.strategy` - 将在 1.16.0 中移除

---

## 命令行工具

### 检查配置

```bash
sing-box check
```

### 格式化配置

```bash
sing-box format -w -c config.json -D config_directory
```

### 合并配置

```bash
sing-box merge output.json -c config.json -D config_directory
```

---

## 参考链接

- 官方文档：https://sing-box.sagernet.org
- GitHub：https://github.com/SagerNet/sing-box
