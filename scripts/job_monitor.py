#!/usr/bin/env python3
"""
银行产品经理岗位监控脚本
抓取 yinhangzhaopin.com 最新银行/证券招聘公告，按条件筛选，
发现新岗位后通过 QQ 邮箱发送通知。

GitHub Actions 定时运行：周一/三/五 16:00 CST
"""

import os
import re
import json
import ssl
import smtplib
import hashlib
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from urllib.request import urlopen, Request

# ─── 配置 ───────────────────────────────────────────

# 监控来源（new100 全量覆盖，特定来源做补充）
SOURCES = {
    "最新银行招聘": "https://www.yinhangzhaopin.com/new100.htm",
    "南京银行": "https://www.yinhangzhaopin.com/nanjinyh/",
    "江苏农商联合银行": "https://www.yinhangzhaopin.com/jsnx/",
    "南京证券": "https://www.yinhangzhaopin.com/zqgszp/45/",
    "证券公司": "https://www.yinhangzhaopin.com/zqgszp/",
}

# 目标机构关键词（匹配到任一即关注）
TARGET_BANKS = [
    "南京银行", "华泰证券", "江苏农商联合银行", "江苏农村商业联合",
    "江苏银行", "苏银凯基", "南银法巴",
    "利安人寿", "江苏金融租赁", "紫金保险",
    "苏商银行", "江苏苏宁银行",
]

# 岗位关键词（标题中包含任一即匹配）
JOB_KEYWORDS = [
    "产品经理", "产品规划", "产品运营", "产品岗",
    "运营管理", "远程运营", "流程管理",
    "零售金融", "零售管理", "零售业务", "零售信贷",
    "个贷", "个人贷款", "消费贷", "消费金融",
    "网络金融", "数字银行", "数字化运营",
    "财富管理", "财富顾问",
    "普惠金融", "个人金融",
    "私人银行", "私行",
]

# 部门级关键词（用于"目标机构+总行"的宽松匹配）
# 当标题包含目标机构+总行+下列关键词之一时，匹配
DEPT_KEYWORDS = [
    "运营管理部", "零售金融部", "零售金融板块",
    "网络金融部", "个人金融部", "消费金融",
    "财富管理", "数字银行", "普惠金融",
    "资产负债管理部", "产品研发", "远程银行",
]

# 排除关键词
EXCLUDE_KEYWORDS = [
    "校园", "校招", "实习", "应届", "培训生",
    "管培生", "柜员", "驾驶员", "厨师", "保安",
    "博士后",
    "Python", "Java", "前端", "运维", "测试工程师",
    "信息技术部", "信息安全", "系统运维",
    "科技岗", "研发工程师", "开发工程师",
]

# 不被排除的分行/支行关键词
BRANCH_EXCLUDE = ["分行", "支行", "营业部", "村镇银行"]

# 邮件配置
SMTP_SERVER = "smtp.qq.com"
SMTP_PORT = 465
SMTP_USER = os.environ.get("QQ_SMTP_USER", "")
SMTP_PASS = os.environ.get("QQ_SMTP_PASS", "")
RECIPIENT = SMTP_USER  # 发给自己

# 去重文件
SEEN_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "seen_jobs.json")
LOOKBACK_DAYS = 30  # 只看最近 N 天发布的


# ─── 抓取工具 ────────────────────────────────────────

def fetch_page(url: str, encoding: str = "gbk") -> str:
    """抓取页面，返回解码后的 HTML"""
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; JobMonitor/1.0; +https://github.com/zhiminbai/opencode-wiki)",
        "Accept": "text/html",
    }
    req = Request(url, headers=headers)
    try:
        with urlopen(req, timeout=15) as resp:
            raw = resp.read()
            # 尝试多种编码
            for enc in [encoding, "gb2312", "utf-8", "gb18030"]:
                try:
                    return raw.decode(enc)
                except (UnicodeDecodeError, LookupError):
                    continue
            return raw.decode("utf-8", errors="replace")
    except Exception as e:
        print(f"  [WARN] 抓取失败 {url}: {e}")
        return ""


def parse_posts(html: str, source_name: str) -> list[dict]:
    """从 HTML 中提取招聘公告列表"""
    posts = []

    # 匹配模式: <a href="相对路径">标题</a> ... 日期
    # yinhangzhaopin 的文章列表格式: <a href="/path/...">title</a> ... YYYY-MM-DD
    pattern = re.compile(
        r'<a\s+href\s*=\s*"([^"]+\.html?)"[^>]*>(.*?)</a>.*?(\d{4}-\d{2}-\d{2})',
        re.DOTALL | re.IGNORECASE,
    )

    for match in pattern.finditer(html):
        url = match.group(1)
        title_raw = match.group(2)
        date_str = match.group(3)

        # 清理标题中残留的 HTML 标签
        title = re.sub(r"<[^>]+>", "", title_raw).strip()
        title = re.sub(r"\s+", " ", title)
        # 去掉标题前面的 [地区] 标签如 [江苏]
        title = re.sub(r"^\[.*?\]", "", title).strip()

        if not title or len(title) < 8:
            continue

        # 构造完整 URL
        if url.startswith("http"):
            full_url = url
        elif url.startswith("//"):
            full_url = "https:" + url
        else:
            full_url = "https://www.yinhangzhaopin.com" + (url if url.startswith("/") else "/" + url)

        # 生成唯一 ID（跨来源去重：用标准化标题+日期组合）
        normalized = re.sub(r"[\s（）\(\)\u3000]", "", title)
        job_id = hashlib.md5(f"{normalized}|{date_str}".encode()).hexdigest()

        posts.append({
            "id": job_id,
            "title": title,
            "url": full_url,
            "date": date_str,
            "source": source_name,
        })

    return posts


# ─── 筛选逻辑 ────────────────────────────────────────

def match_job(post: dict) -> tuple[bool, str]:
    """
    判断岗位是否匹配。
    两级匹配：
      Tier 1 - 精确：标题含岗位名+目标机构+总行
      Tier 2 - 部门级：目标机构+总行+相关部门关键词
    """
    title = post["title"]

    # 1. 排除规则
    for kw in EXCLUDE_KEYWORDS:
        if kw in title:
            return False, f"排除:{kw}"

    # 2. 必须包含目标机构
    matched_bank = [b for b in TARGET_BANKS if b in title]
    if not matched_bank:
        return False, "非目标机构"

    # 3. 排除分行/支行（除非同时有总行/总部）
    has_branch = any(kw in title for kw in BRANCH_EXCLUDE)
    has_headquarters = "总行" in title or "总部" in title
    if has_branch and not has_headquarters:
        return False, "分行/支行层级"

    # 4. Tier 1: 精确岗位关键词匹配
    matched_keywords = [kw for kw in JOB_KEYWORDS if kw in title]
    if matched_keywords:
        reasons = [f"岗位:{','.join(matched_keywords)}", f"机构:{matched_bank[0]}"]
        return True, " | ".join(reasons)

    # 5. Tier 2: 目标机构+总行+相关部门关键词（宽松匹配）
    if has_headquarters:
        matched_dept = [kw for kw in DEPT_KEYWORDS if kw in title]
        if matched_dept:
            reasons = [f"总行部门:{','.join(matched_dept)}", f"机构:{matched_bank[0]}"]
            return True, " | ".join(reasons)

    return False, "无匹配关键词"


# ─── 去重 ────────────────────────────────────────────

def load_seen() -> dict:
    """加载已见过的岗位记录"""
    if os.path.exists(SEEN_FILE):
        try:
            with open(SEEN_FILE, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return {"last_run": None, "job_ids": [], "total_seen": 0}


def save_seen(seen: dict):
    """保存已见岗位"""
    os.makedirs(os.path.dirname(SEEN_FILE), exist_ok=True)
    with open(SEEN_FILE, "w") as f:
        json.dump(seen, f, ensure_ascii=False, indent=2)


# ─── 邮件发送 ────────────────────────────────────────

def send_email(new_jobs: list[dict]):
    """通过 QQ SMTP 发送新岗位邮件"""
    if not SMTP_USER or not SMTP_PASS:
        print("[ERROR] 邮箱未配置，跳过发送")
        return False

    now = datetime.now().strftime("%Y-%m-%d")
    count = len(new_jobs)

    # 构建 HTML 邮件
    subject = f"[求职监控] {now} 新增 {count} 个匹配岗位"

    html_parts = [
        f"<h2>🔔 银行产品经理岗位监控 — {now}</h2>",
        f"<p><strong>本轮发现 {count} 个新岗位：</strong></p>",
        "<div style='font-size:14px'>",
    ]

    for job in new_jobs:
        html_parts.append(f"""
        <div style='border-left:4px solid #1a73e8; margin:12px 0; padding:8px 12px; background:#f8f9fa'>
          <div style='font-weight:bold; font-size:15px; color:#1a73e8'>{job['title']}</div>
          <div style='color:#666; margin-top:4px'>
            📅 {job['date']} &nbsp;|&nbsp; 📍 {job['reason']} &nbsp;|&nbsp; 🔗 <a href="{job['url']}">查看详情</a>
          </div>
        </div>
        """)

    html_parts.append("</div>")
    html_parts.append(
        f"<hr><p style='color:#999;font-size:12px'>"
        f"GitHub Actions 自动监控 · 每周一三五发送 · "
        f"<a href='https://github.com/zhiminbai/opencode-wiki'>配置管理</a></p>"
    )

    html_body = "\n".join(html_parts)

    # 发送
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = SMTP_USER
    msg["To"] = RECIPIENT
    msg.attach(MIMEText(f"本轮发现 {count} 个新岗位，请查看 HTML 邮件。", "plain", "utf-8"))
    msg.attach(MIMEText(html_body, "html", "utf-8"))

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=context) as server:
            server.login(SMTP_USER, SMTP_PASS)
            server.sendmail(SMTP_USER, [RECIPIENT], msg.as_string())
        print(f"[OK] 邮件已发送至 {RECIPIENT}")
        return True
    except Exception as e:
        print(f"[ERROR] 邮件发送失败: {e}")
        return False


# ─── 企业微信机器人推送 ──────────────────────────────

WECOM_KEY = os.environ.get("WECOM_KEY", "")
WECOM_URL = f"https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key={WECOM_KEY}"


def send_wecom(new_jobs: list[dict]):
    """通过企业微信机器人发送新岗位通知"""
    if not WECOM_KEY:
        print("[INFO] 企业微信机器人未配置，跳过推送")
        return False

    now = datetime.now().strftime("%Y-%m-%d")
    count = len(new_jobs)

    # 构建 Markdown 消息（企微机器人支持的格式）
    lines = [
        f"## 🔔 银行产品经理岗位监控",
        f"**{now}**  |  新增 **{count}** 个匹配岗位",
        "",
    ]

    for i, job in enumerate(new_jobs[:10], 1):  # 最多推 10 条
        lines.append(f"{i}. [{job['title']}]({job['url']})")
        lines.append(f"> {job['date']} | {job['reason']}")

    if len(new_jobs) > 10:
        lines.append(f"")
        lines.append(f"> 更多 {len(new_jobs) - 10} 条请查看邮件")

    payload = {
        "msgtype": "markdown",
        "markdown": {
            "content": "\n".join(lines)
        }
    }

    try:
        req = Request(WECOM_URL, data=json.dumps(payload).encode("utf-8"),
                      headers={"Content-Type": "application/json"})
        with urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            if result.get("errcode") == 0:
                print(f"[OK] 企业微信推送成功")
                return True
            else:
                print(f"[ERROR] 企业微信推送失败: {result}")
                return False
    except Exception as e:
        print(f"[ERROR] 企业微信推送异常: {e}")
        return False



# ─── 主流程 ──────────────────────────────────────────

def main():
    print(f"=== 银行产品经理岗位监控 ===")
    print(f"运行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # 加载去重记录
    seen = load_seen()
    seen_ids = set(seen.get("job_ids", []))
    print(f"已记录岗位数: {len(seen_ids)}")

    # 收集所有岗位
    all_posts = []
    for source_name, url in SOURCES.items():
        print(f"抓取: {source_name} ...")
        html = fetch_page(url)
        if html:
            posts = parse_posts(html, source_name)
            print(f"  获取 {len(posts)} 条")
            all_posts.extend(posts)
        else:
            print(f"  无数据")

    # 去重（跨来源 + 跨轮）
    run_ids = set()
    unique_posts = []
    for p in all_posts:
        pid = p["id"]
        if pid not in seen_ids and pid not in run_ids:
            run_ids.add(pid)
            unique_posts.append(p)
    print(f"\n去重前: {len(all_posts)} 条, 去重后: {len(unique_posts)} 条")

    # 时间过滤
    cutoff = (datetime.now() - timedelta(days=LOOKBACK_DAYS)).strftime("%Y-%m-%d")
    recent_posts = [p for p in unique_posts if p["date"] >= cutoff]
    print(f"时间过滤(>{cutoff}): {len(recent_posts)} 条")

    # 规则匹配
    matched = []
    for post in recent_posts:
        ok, reason = match_job(post)
        if ok:
            post["reason"] = reason
            matched.append(post)

    print(f"规则匹配: {len(matched)} 条")
    for m in matched:
        print(f"  ✓ {m['date']} [{m['source']}] {m['title'][:60]}... ({m['reason']})")

    # 更新去重记录
    seen["last_run"] = datetime.now().isoformat()
    seen["job_ids"] = list(seen_ids | run_ids)
    seen["total_seen"] = len(seen["job_ids"])
    save_seen(seen)

    # 发送通知
    if matched:
        print(f"\n发送通知: {len(matched)} 个新岗位")
        send_email(matched)
        send_wecom(matched)
    else:
        print(f"\n无新岗位，跳过通知")

    print(f"\n完成。seen_jobs.json 已更新 ({seen['total_seen']} 条已记录)")


if __name__ == "__main__":
    main()
