# sing-box 配置生成 Skill

## 触发条件

当用户需要生成、修改、调试 sing-box 配置文件时触发。关键词：sing-box 配置、sing-box config、代理配置、翻墙配置、分流规则。

## 工作流程

### 第1步：收集需求

向用户询问以下信息（如果用户未提供）：

1. **使用场景**
   - 目标设备？（Android / iOS / macOS / Windows / Linux / 路由器，不确定则生成通用配置）
   - 代理协议？（shadowsocks / vmess / vless / trojan / hysteria2 / tuic / wireguard / 其他）
   - 入站模式？（TUN 透明代理 / TUN+Mixed / Mixed 系统代理，不确定则默认 TUN+Mixed）
   - sing-box 版本？（1.11 / 1.12 / 1.13 / 1.14，不确定则默认 1.14）

2. **网络环境**
   - IPv4 only 还是 IPv4+IPv6？（不确定则默认 IPv4 only，避免 IPv6 网络不通时连接失败）
   - rule_set 下载方式？（直连下载 / 通过代理下载 / 使用国内镜像，不确定则默认直连+镜像兜底）
   - DNS 是否被污染？（国内 UDP DNS 通常被污染，建议使用 DoH/DoT。不确定则默认 DoH）

3. **分流需求**
   - 国内直连、国外走代理？（默认是）
   - 有无特殊分流？（如指定域名/IP 走指定出站、广告拦截等）
   - 是否需要 FakeIP？
   - 是否需要广告拦截？（默认不启用，启用则在路由规则中添加 reject 广告域名规则集）

4. **路由选项**
   - 是否需要 resolve 动作？（在 GeoIP 匹配前将域名解析为 IP，使 GeoIP 规则能匹配域名请求。默认启用，如不需要可关闭）
   - TUN 模式下是否启用 http_proxy？（在 iOS/macOS 上，部分应用不经过 TUN 但支持 HTTP 代理，启用后 TUN 内置 HTTP 代理兜底。默认不启用）

5. **DNS 需求**
   - 国内 DNS 服务器？（默认阿里 223.5.5.5）
   - 国外 DNS 服务器？（默认 Google 8.8.8.8 或 Cloudflare 1.1.1.1）
   - 是否需要 DNS over HTTPS / TLS？

6. **节点与出站**
   - 是否使用订阅链接？（参考项目 config_template 中的占位符 `{all}`）
   - 还是手动填写节点？（需要服务器地址、端口、密码/UUID 等）
   - 出站分组方式？（仅 Auto+Direct / 按地区分组如香港/日本/美国，默认仅 Auto+Direct）
   - 是否需要节点筛选？（排除/包含特定关键词，如排除"过期"/包含"香港"）

7. **管理功能**
   - 是否需要 Clash API？（启用后可用 Web 面板管理节点切换、查看流量。默认不启用）
   - 是否需要 NTP 同步？（时间不准的环境如路由器需要，默认不启用）

8. **迁移需求**
   - 是否从旧版本升级？（提供旧配置，AI 自动处理弃用字段和格式变更）
   - 是否从 Clash/V2Ray 迁移？（提供原配置，AI 转换为 sing-box 格式）

### 第2步：生成配置

根据收集的信息和 `reference.md` 中的配置文档，生成完整的 sing-box 配置 JSON。

**生成规则：**

1. 只生成用户目标版本支持的配置项，参考 `reference.md` 中的版本标签（如 `[1.14+]` 表示 1.14.0 起可用，`[弃用1.14]` 表示在 1.14.0 中弃用）
2. 弃用字段不使用，改用新替代方案
3. 如果用户使用订阅链接，outbounds 中使用 `{all}` 占位符
4. 必须包含基本的路由规则：sniff → hijack-dns → 私有IP直连 → 分流规则 → final
5. 必须包含 DNS 配置
6. TUN 模式必须设置 `auto_route` 和 `strict_route`
7. 默认在 GeoIP 规则前包含 `{"action": "resolve"}`，将域名解析为 IP 以便 GeoIP 匹配。如用户不需要可移除
8. TUN 的 `platform.http_proxy` 默认不启用，如用户需要则在 tun inbound 中添加：
   ```json
   "platform": {
     "http_proxy": {
       "enabled": true,
       "server": "127.0.0.1",
       "server_port": 7890
     }
   }
   ```

**网络环境适配：**

9. IPv4 only 时，DNS strategy 设为 `ipv4_only`，避免 AAAA 查询导致连接失败
10. rule_set 下载：1.14+ 使用 `http_clients` + `default_http_client` 配置下载出站；1.13 及以下使用 `download_detour` 字段
11. 国内镜像 rule_set URL 示例：`https://gh-proxy.com/https://raw.githubusercontent.com/...` 或 `https://cdn.jsdelivr.net/gh/...`

**功能配置：**

12. Clash API 配置示例：
    ```json
    "experimental": {
      "clash_api": {
        "external_controller": "127.0.0.1:9090",
        "secret": "your-secret"
      }
    }
    ```
13. NTP 配置示例：
    ```json
    "ntp": {
      "enabled": true,
      "server": "time.apple.com",
      "server_port": 123,
      "interval": "30m"
    }
    ```
14. 广告拦截：在路由规则中添加 reject 规则集，如 `{"action": "reject", "rule_set": ["GeoSite-Ad"]}`
15. 多出站分组：使用 selector + filter 按关键词分组，如香港节点用 `{"action": "include", "keywords": ["香港"]}`
16. Docker 部署：不使用 TUN，用 mixed/socks 暴露端口，如 `"listen": "0.0.0.0"` 而非 `127.0.0.1`

**版本迁移：**

17. 旧版本升级时，自动处理以下变更：
    - 1.11→1.12：`download_detour` 替代方案、DNS strategy 位置变更
    - 1.12→1.13：`independent_cache` 弃用、`inbound.sniff` 移至 route rule action
    - 1.13→1.14：`download_detour` 弃用改用 `http_client`、`domain_strategy` 弃用改用 `domain_resolver`、DNS `strategy` 弃用
18. Clash/V2Ray 迁移时，参考以下映射：
    - Clash proxy-groups → sing-box selector/urltest
    - Clash rules → sing-box route.rules
    - Clash dns → sing-box dns
    - V2Ray outbound → sing-box 对应 outbound（vmess/vless/trojan 等协议基本一致）

### 第3步：校验与输出

1. 输出完整 JSON 配置
2. 提示用户可用 `sing-box check` 验证
3. 如有订阅链接，提示用户可通过本项目的订阅转换 API 使用
4. 如有 Clash API，提示用户可访问 `http://127.0.0.1:9090/ui` 管理面板

## 常见场景模板

### 场景1：TUN 透明代理 + 国内直连国外代理

典型配置结构：
- log: info
- dns: 本地DNS + FakeIP
- inbound: tun（auto_route + strict_route）
- outbound: urltest(selector) + direct
- route: sniff → hijack-dns → 私有IP直连 → 国内直连 → 国外代理 → final=代理
- rule_set: GeoSite-CN / GeoIP-CN / GeoSite-!CN

### 场景2：TUN + Mixed + 国内直连国外代理（最常见）

典型配置结构：
- log: info
- dns: 本地DNS + 远程DNS over HTTPS
- inbound: tun（auto_route + strict_route）+ mixed（127.0.0.1:7890）
- outbound: urltest(selector) + direct
- route: sniff → hijack-dns → 私有IP直连 → 国内直连 → 国外代理 → final=代理
- rule_set: GeoSite-CN / GeoIP-CN / GeoSite-!CN

### 场景3：仅代理（无分流）

典型配置结构：
- log: info
- dns: 本地DNS
- inbound: tun + mixed
- outbound: selector + direct
- route: final=代理

### 场景4：Docker 部署

典型配置结构：
- log: info
- dns: 本地DNS + DoH
- inbound: mixed（0.0.0.0:7890）+ socks（0.0.0.0:7891）
- outbound: urltest + direct
- route: 国内直连 → 国外代理 → final=代理

### 场景5：路由器（OpenWrt）

典型配置结构：
- log: info
- ntp: 启用（路由器时间通常不准）
- dns: 本地DNS + FakeIP
- inbound: tun（auto_route + auto_redirect）
- outbound: urltest + direct
- route: sniff → hijack-dns → 国内直连 → 国外代理 → final=代理

## 设备适配规则

根据用户指定的目标设备，自动调整配置中的平台相关字段：

### Android

- TUN inbound 可用
- 支持 `include_package` / `exclude_package` 按应用分流
- 支持 `network_type` / `network_is_expensive` / `network_is_constrained` 网络类型匹配
- 不支持 `process_name` / `process_path`
- 不支持 `platform.http_proxy`
- Mixed inbound 不支持 `set_system_proxy`
- 图形客户端：sing-box 官方 Android 客户端

### iOS / iPadOS / tvOS / macOS（Apple 平台）

- TUN inbound 可用
- 支持 `platform.http_proxy`（部分应用不经过 TUN 但支持 HTTP 代理，如 App Store）
- 支持 `network_type` / `network_is_expensive` / `network_is_constrained`
- 不支持 `process_name` / `process_path` / `include_package` / `exclude_package`
- Mixed inbound 不支持 `set_system_proxy`
- 图形客户端：sing-box 官方 Apple 客户端（SFM）
- macOS 桌面端也可用 `process_name` / `process_path`

### Windows

- TUN inbound 可用（需要管理员权限）
- 支持 `process_name` / `process_path`
- 不支持 `include_package` / `exclude_package`
- 不支持 `network_type` / `network_is_expensive`
- Mixed inbound 支持 `set_system_proxy`
- 不支持 `platform.http_proxy`
- 图形客户端：Hiddify / Clash Verge 等

### Linux

- TUN inbound 可用（需要 root 权限）
- 支持 `process_name` / `process_path` / `user` / `user_id`
- 支持 `auto_redirect`（nftables 增强 TUN 路由）
- 支持 `include_interface` / `exclude_interface`
- 支持 `routing_mark`
- Mixed inbound 不支持 `set_system_proxy`
- 不支持 `platform.http_proxy`
- 不支持 `include_package` / `exclude_package`

### 路由器（OpenWrt 等）

- 仅 Linux 规则适用
- 通常使用 TUN + auto_redirect 模式
- 需要特别注意 `auto_route` 与现有路由表的冲突
- 不需要 Mixed inbound
- 建议启用 NTP 同步

## 注意事项

1. 所有 JSON 字段名和值必须严格遵循 `reference.md` 中的定义
2. rule_set 的 URL 需要使用可访问的地址，推荐使用 MetaCubeX 的规则集
3. TUN 模式需要管理员/root 权限运行
4. FakeIP 需要配合 DNS 规则使用，仅对外网域名启用
5. 生成配置后提醒用户根据实际网络环境调整 DNS 和 rule_set 的 URL
6. `resolve` 动作的作用：在 GeoIP 规则前将域名请求解析为 IP，否则 GeoIP 只能匹配 IP 请求而无法匹配域名请求。使用 FakeIP 时 resolve 尤其重要
7. TUN 的 `platform.http_proxy` 适用于 iOS/macOS 图形客户端，部分应用（如 App Store）不经过 TUN 但支持系统 HTTP 代理，启用后可兜底
8. IPv4 only 环境务必设置 `strategy: "ipv4_only"`，否则 AAAA 查询可能返回不可用的 IPv6 地址导致连接超时
9. Docker 部署时 mixed/socks 监听地址用 `0.0.0.0` 而非 `127.0.0.1`，否则容器外无法访问
10. 多配置合并可使用 `sing-box merge` 命令，将多个 JSON 文件合并为一个配置
