#!/usr/bin/env python3
"""Create Feishu doc with daily briefing (2026.06.05)."""
import json, datetime
from pathlib import Path
from urllib.request import Request, urlopen

env_path = Path.home() / ".hermes" / ".env"
app_id = app_secret = None
for line in env_path.read_text().splitlines():
    if line.startswith("FEISHU_APP_ID="):
        app_id = line.split("=", 1)[1].strip().strip("\"'")
    elif line.startswith("FEISHU_APP_SECRET="):
        app_secret = line.split("=", 1)[1].strip().strip("\"'")

BASE = "https://open.feishu.cn"

def api(method, path, token, body=None):
    data = json.dumps(body).encode() if body else None
    req = Request(BASE + path, data=data, method=method)
    req.add_header("Content-Type", "application/json; charset=utf-8")
    if token:
        req.add_header("Authorization", "Bearer " + token)
    try:
        with urlopen(req, timeout=15) as resp:
            return json.loads(resp.read())
    except Exception as e:
        if hasattr(e, 'read'):
            return json.loads(e.read().decode())
        raise

r = api("POST", "/open-apis/auth/v3/tenant_access_token/internal", None,
        {"app_id": app_id, "app_secret": app_secret})
token = r["tenant_access_token"]

today = datetime.date.today()
title = f"今日AI简报 | AI冲击学术 · 递归进化 | {today.year}.{today.month:02d}.{today.day:02d}"

r = api("POST", "/open-apis/docx/v1/documents", token, {"title": title})
doc_id = r["data"]["document"]["document_id"]
doc_url = f"https://bytedance.feishu.cn/docx/{doc_id}"
print(f"DOC_URL:{doc_url}")
print(f"TITLE:{title}")

# Helpers
def T(content, bold=False, color=None):
    el = {"text_run": {"content": content}}
    style = {}
    if bold:
        style["bold"] = True
    if color is not None:
        style["text_color"] = color
    if style:
        el["text_run"]["text_element_style"] = style
    return el

def TX(elements):
    if not isinstance(elements, list):
        elements = [elements]
    return {"block_type": 2, "text": {"elements": elements}}

def H2(text):
    return {"block_type": 4, "heading2": {
        "elements": [{"text_run": {"content": text, "text_element_style": {"text_color": 5}}}],
        "style": {"align": 2}
    }}

def ST(text):
    """Section title: centered blue bold underlined text block."""
    return {"block_type": 2, "text": {
        "elements": [{"text_run": {"content": text, "text_element_style": {"bold": True, "text_color": 5, "underline": True}}}],
        "style": {"align": 2}
    }}

def DV():
    return {"block_type": 22, "divider": {}}

P = lambda t: TX([T(t)])            # plain text
BOL = lambda s: TX([T('\u25b8 '), T(s, True), T('')])  # bold lead
L = lambda t: TX([T('\u25b8 '), T(t)])  # list item
SP = lambda: TX([T('')])            # spacing

c = []

# --- Opening ---
c.append(P(
    '今日HN榜首话题\u2014\u2014伯克利CS课程因AI使用导致挂科率飙升\uff08717\U0001f525\uff09\u2014\u2014揭示了一个无法回避的现实：'
    '当LLM能轻松解答编程作业时，学术体系正在经历结构性冲击。而同一周，Anthropic连续发布两则重磅消息\u2014\u2014'
    '递归自我改进进展\uff08245\U0001f525\uff09和AI漏洞发现框架\uff08179\U0001f525\uff09\u2014\u2014'
    '勾勒出AI进化的双面性：它在自我增强的同时，也在重塑与之共存的人类体系。'
))
c.append(DV())

# --- Key points (2) ---
c.append(L('伯克利CS挂科率飙升 717\U0001f525\u2014\u2014AI辅助编程导致数学能力下降，教育体系急待重新设计'))
c.append(L('Anthropic递归自我改进 245\U0001f525\u2014\u2014从\u201c工具\u201d向\u201c自主进化体\u201d迈进'))
c.append(DV())

# --- Tech AI news (2 items, mixed domestic+international) ---
c.append(ST('\U0001f525 科技圈AI动态'))
c.append(BOL('伯克利CS学业危机：AI利用率上升与数学能力下降的因果链（717\U0001f525）'))
c.append(P(
    'UC Berkeley计算机系的教授们发现，随着AI编程助手在课堂上普及，学生的数学推导能力显著下降，'
    '导致基础课程挂科率创下历史新高。这场讨论的核心不是\u201c禁用AI\u201d，'
    '而是如何重新设计课程体系和评估方式\u2014\u2014当编程作业可以被AI瞬间完成，我们衡量的到底是谁的能力？'
))
c.append(SP())
c.append(BOL('Anthropic双响炮：递归自我改进 + 开源漏洞发现框架'))
c.append(P(
    'Anthropic在官方博客公布了递归自我改进（Recursive Self-Improvement）研究进展（245\U0001f525），'
    '展示了AI系统对自己生成的代码进行审查和改进的能力。同时发布开源框架defending-code-reference-harness（179\U0001f525），'
    '让安全团队可以用AI驱动的自动化方式发现应用漏洞。两条消息形成微妙呼应：'
    '同一技术在推进AI自主性的同时，也在增强人类对AI系统的防御能力。'
))
c.append(DV())

# --- GitHub head projects (1-2) ---
c.append(ST('\U0001f525 GitHub 头部项目'))
c.append(BOL('n8n-io/n8n \u2b50 191,109'))
c.append(P(
    '工作流自动化平台，400+集成，原生AI能力。n8n持续保持高速增长，本周接近20万星。'
    '核心卖点是将AI能力嵌入可视化工作流，让运营团队无需编写代码即可编排LLM推理、RAG管道和自动化任务。'
    '新增的AI Agent节点支持在工作流中直接调用多步推理的AI Agent，而非单一LLM调用。'
))
c.append(SP())
c.append(BOL('affaan-m/ECC \u2b50 207,165'))
c.append(P(
    'Agent运行时优化框架，短短数月飙升至20万星以上。涵盖技能管理、记忆系统、安全控制等模块，'
    '核心思想是在Agent执行层面进行性能调优\u2014\u2014\u201c不是换更好的模型，而是让现有Agent运行得更高效\u201d。'
    '与今天的效率主题一脉相承。'
))
c.append(DV())

# --- New projects (2) ---
c.append(ST('\U0001f525 新锐项目'))
c.append(BOL('mksglu/context-mode \u2b50 16,423'))
c.append(P(
    'AI编码Agent上下文窗口优化工具。通过沙箱化工具输出、智能压缩中间结果，宣称将上下文消耗降低98%。'
    '2026年2月发布，不到4个月即获1.6万星，说明开发者对\u201c成本控制型AI工具\u201d的需求极为迫切。'
    '这不仅是一个工具，更代表了一种趋势：当Token成本成为规模化瓶颈，每一分上下文都要精打细算。'
))
c.append(SP())
c.append(BOL('huawei-csl/KVarN \u2b50 177（HN 107\U0001f525）'))
c.append(P(
    '华为开源免校准KV-cache量化方案，作为vLLM的原生后端运行。'
    '在保持FP16精度的前提下将上下文窗口扩展3-5倍，吞吐量超过FP16。'
    '虽然刚发布星星不多，但107\U0001f525的HN热度和华为品牌效应让它在社区快速传播。'
    '推理效率优化是2026年最热的工程方向之一。'
))
c.append(DV())

# --- Community (2 items) ---
c.append(ST('\U0001f4ac 社区热议'))
c.append(BOL('\u201cNSA采用Anthropic Mythos用于网络攻击\u201d（59\U0001f525）'))
c.append(P(
    '金融时报报道NSA正在将Anthropic的Mythos模型用于网络攻防场景。'
    '这条消息与Anthropic同日发布的漏洞发现框架形成有趣对照\u2014\u2014'
    '同一家公司的AI能力同时被用于攻击和防御的探讨。社区讨论集中在：'
    '红队测试方法论是否需要与AI协同演进？传统安全审计在AI自主漏洞发现能力面前是否仍然有效？'
))
c.append(SP())
c.append(BOL('伯克利CS教育反思：AI时代的CS应该教什么？（717\U0001f525）'))
c.append(P(
    'HN评论区已经发展到第二层讨论：不是\u201c禁用还是允许AI\u201d，'
    '而是\u201c当AI让解题变得无意义后，教育应该教什么？\u201d'
    '有教授提出将课程重点从代码实现转为系统设计、AI协作评估和能力边界认知\u2014\u2014'
    '这可能是未来CS教育改革的重要方向。'
))
c.append(DV())

# --- Editorial (1-2 paragraphs) ---
c.append(ST('\U0001f4dd 编辑点评'))
c.append(P(
    '今天的消息呈现出AI行业一个有趣的\u201c辩证分裂\u201d：一边是AI自我进化的加速'
    '（Anthropic递归改进、KVarN推理优化），另一边是AI对人类系统造成的冲击'
    '（伯克利学术危机、安全攻防转换）。这两条线并非孤立存在\u2014\u2014'
    'AI越强，它对社会结构的影响越大；社会结构越需要适应，越需要更聪明的AI来帮助解决适应过程中产生的问题。'
))
c.append(SP())
c.append(P(
    '一个更实际的观察：今天涌现的多个项目（context-mode、KVarN、ECC）都在追求同一个目标\u2014\u2014'
    '让现有AI系统运行得更高效、更便宜。当行业从\u201c大模型竞赛\u201d转向\u201c工程效率竞赛\u201d，'
    '真正值得关注的可能不是下一个突破性模型，而是那些让现有模型能被更多人有效使用的工具。'
    '效率工具正在成为AI民主化的关键推手。'
))

total = len(c)
print(f"Blocks: {total}")
for i in range(0, total, 4):
    batch = c[i:i+4]
    r = api("POST", f"/open-apis/docx/v1/documents/{doc_id}/blocks/{doc_id}/children", token,
            {"children": batch, "index": i})
    ok = r.get("code") == 0
    print(f"  [{i:2d}] {'OK' if ok else 'FAIL: ' + str(r.get('msg'))}")

print(f"\nDONE: {doc_url}")
