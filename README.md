# 监听站1379 · AI 每日简报

自动化的 AI 科技日报系统，每日采集国内外 AI 动态，生成结构化日报并推送至飞书/微信。

## 功能概述

- **每日定时采集** — 从 GitHub、Hacker News、ArXiv 等多源抓取 AI 热点
- **结构化输出** — 6-8 条深度分析，叙事型风格，不堆砌信息
- **飞书文档** — 通过 Open API 创建富文本文档，蓝色居中板块标题
- **封面生成** — Pillow 生成 1200×630 公众号风格封面图
- **多渠道分发** — 飞书 + 微信（手动粘贴至公众号 App）

## 目录结构

```
├── skill/
│   ├── SKILL.md                    # daily-briefing 技能定义
│   └── feishu-doc-api.md           # 飞书文档 API 技能
├── scripts/
│   ├── create_daily_briefing_doc.py   # 主脚本：创建飞书日报文档
│   ├── create-feishu-briefing-doc.py  # 备用脚本
│   └── generate-cover.py              # 封面图生成
├── references/
│   ├── feishu-color-reference.md      # 飞书文字颜色对照
│   ├── feishu-doc-briefing-api.md     # 飞书 API 参考
│   ├── wechat-account-setup.md        # 公众号注册指南
│   └── wechat-official-account-format.md
├── templates/
│   ├── ai-daily-briefing-prompt.md     # Cron prompt 模板
│   └── feishu-doc-briefing-prompt.md   # 飞书版 prompt
├── CRON_SETUP.md                    # 定时任务配置
└── README.md                        # 本文件
```

## 工作流程

```
数据采集 (GitHub, HN, ArXiv)
    ↓
生成结构化日报 (6-8 条)
    ↓
创建飞书文档 (Rich text + 蓝色标题)
    ↓
生成封面图 (1200×630)
    ↓
飞书推送: ①日报链接 ②标题 ③封面
```

## 格式规范

| 板块 | 数量 | 说明 |
|------|:----:|------|
| 开场总述 | 1段 | 当日核心焦点 |
| ▸ 要点预览 | 2条 | 关键词 + 一句话 |
| 🔥 科技圈AI动态 | 2条 | 国内国际混排 |
| 🔥 GitHub 头部项目 | 1-2条 | 高星项目 |
| 🔥 新锐项目 | 2条 | 低星活跃项目 |
| 💬 社区热议 | 0-2条 | 优质内容 |
| 📝 编辑点评 | 1-2段 | 深度分析 |

- 热度标记用 🔥（U+1F525）
- 每条正文 2-3 句
- 无"今日互动"板块
- 无"数据来源"行
- 无 Hermes Agent 品牌标识
