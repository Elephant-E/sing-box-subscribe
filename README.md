# sing-box 订阅转换

根据配置模板和订阅链接生成 sing-box 配置文件。

## 使用方式

### API

```
https://xxxxxxx.vercel.app/config/https://订阅链接?token=xxx&file=https://远程模板URL
```

`file` 参数支持：
- 数字：选择本地模板序号（从1开始）
- URL：使用远程配置模板

### 本地运行

```
python main.py
python main.py --template_index=0
```

### Web 界面

访问部署地址，输入订阅链接，选择模板，点击生成配置。
