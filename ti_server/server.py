#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
天鯨威胁情报服务器 (ti_server) v2
==================================
独立的威胁情报数据服务端，可与流影/天鯨 SOC 平台 threatinfo 接口对接。

v2 特性：
- 数据库：MySQL/MariaDB（pymysql），独立数据库实例
- 双端口隔离：管理端口（Web 界面 + 管理 API）与查询端口（情报查询协议）分离
- HTTPS：管理界面支持上传 PFX 证书并启用 HTTPS 访问
- JWT 签发协议兼容流影 threatinfo（响应体即 token，纯文本）
- 多类型威胁情报：IP / 域名 / URL / 文件哈希

启动：
    python3 server.py --init --db-pass <密码>          # 初始化数据库
    python3 server.py --db-pass <密码>                 # 启动（管理 8090 / 查询 8091）
    python3 server.py --manage-port 8443 --query-port 8091 --db-pass <密码>
"""

import argparse
import base64
import csv
import hashlib
import hmac
import http.server
import io
import ipaddress
import json
import os
import re
import secrets
import socket
import ssl
import subprocess
import sys
import threading
import time
import urllib.parse
import urllib.request

try:
    import pymysql
except ImportError:
    print("[ERROR] 需要 pymysql：yum install -y python3-PyMySQL 或 pip install pymysql")
    sys.exit(1)

# ---------------------------------------------------------------------------
# 常量
# ---------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
CERTS_DIR = os.path.join(BASE_DIR, "certs")
CERT_PFX = os.path.join(CERTS_DIR, "ti_server.pfx")
CERT_PEM = os.path.join(CERTS_DIR, "cert.pem")
CERT_KEY = os.path.join(CERTS_DIR, "key.pem")

DEFAULT_MANAGE_PORT = 8090
DEFAULT_QUERY_PORT = 8091
SESSION_TIMEOUT = 8 * 3600
JWT_EXPIRE = 300
DEFAULT_ADMIN = ("admin", "admin")
IOC_TYPES = ("ip", "domain", "url", "hash")

# 开源情报源
SOURCE_TYPES = ("threatfox", "urlhaus", "feodo", "iplist", "csv")
DEFAULT_THREATFOX_URL = "https://threatfox.abuse.ch/export/csv/recent/"
DEFAULT_URLHAUS_URL = "https://urlhaus.abuse.ch/downloads/csv_recent/"
DEFAULT_FEODO_URL = "https://feodotracker.abuse.ch/downloads/ipblocklist.csv"
HTTP_UA = "ti_server/2.1 (threat intelligence collector; contact: soc-admin)"

DB_CFG = {"host": "127.0.0.1", "user": "root", "password": "", "name": "ti_server"}

# ---------------------------------------------------------------------------
# 数据库（MySQL / MariaDB）
# ---------------------------------------------------------------------------
def get_db():
    conn = pymysql.connect(
        host=DB_CFG["host"], user=DB_CFG["user"], password=DB_CFG["password"],
        database=DB_CFG["name"], charset="utf8mb4", cursorclass=pymysql.cursors.DictCursor,
        autocommit=False,
    )
    return conn


def init_db():
    conn = pymysql.connect(
        host=DB_CFG["host"], user=DB_CFG["user"], password=DB_CFG["password"],
        charset="utf8mb4", autocommit=True,
    )
    cur = conn.cursor(pymysql.cursors.DictCursor)
    cur.execute(
        f"CREATE DATABASE IF NOT EXISTS `{DB_CFG['name']}` "
        "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
    )
    cur.execute(f"USE `{DB_CFG['name']}`")
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS t_user (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user VARCHAR(64) UNIQUE NOT NULL,
            pass_hash VARCHAR(64) NOT NULL,
            salt VARCHAR(64) NOT NULL,
            created BIGINT NOT NULL
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS t_ioc (
            id INT AUTO_INCREMENT PRIMARY KEY,
            type VARCHAR(16) NOT NULL,
            value VARCHAR(512) NOT NULL,
            threat VARCHAR(64) DEFAULT '',
            score INT DEFAULT 50,
            tags VARCHAR(255) DEFAULT '',
            source VARCHAR(255) DEFAULT '',
            confidence INT DEFAULT 80,
            expire BIGINT DEFAULT 0,
            note VARCHAR(512) DEFAULT '',
            created BIGINT NOT NULL,
            updated BIGINT NOT NULL,
            INDEX idx_ioc_type (type),
            INDEX idx_ioc_value (value(191))
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS t_client (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(128) NOT NULL,
            order_no VARCHAR(64) DEFAULT '',
            contact VARCHAR(255) DEFAULT '',
            cli_key VARCHAR(64) UNIQUE NOT NULL,
            cli_token VARCHAR(64) UNIQUE NOT NULL,
            allowed_ips VARCHAR(512) DEFAULT '',
            update_window VARCHAR(32) DEFAULT '',
            enabled TINYINT DEFAULT 1,
            update_log TEXT DEFAULT '',
            last_update BIGINT DEFAULT 0,
            created BIGINT NOT NULL,
            updated BIGINT NOT NULL
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS t_config (
            k VARCHAR(64) PRIMARY KEY,
            v TEXT
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS t_source (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(128) NOT NULL,
            type VARCHAR(32) NOT NULL,
            url VARCHAR(512) DEFAULT '',
            api_key VARCHAR(255) DEFAULT '',
            interval_min INT DEFAULT 1440,
            keep_days INT DEFAULT 30,
            mapping VARCHAR(1024) DEFAULT '',
            enabled TINYINT DEFAULT 1,
            last_pull BIGINT DEFAULT 0,
            last_status VARCHAR(16) DEFAULT '',
            last_count INT DEFAULT 0,
            last_error VARCHAR(512) DEFAULT '',
            pull_log TEXT DEFAULT '',
            created BIGINT NOT NULL,
            updated BIGINT NOT NULL
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """
    )
    cur.execute("SELECT COUNT(*) AS n FROM t_user")
    if cur.fetchone()["n"] == 0:
        user, pwd = DEFAULT_ADMIN
        salt = secrets.token_hex(16)
        cur.execute(
            "INSERT INTO t_user (user, pass_hash, salt, created) VALUES (%s,%s,%s,%s)",
            (user, hash_password(pwd, salt), salt, int(time.time())),
        )
    defaults = {
        "service_key": secrets.token_hex(16),
        "jwt_secret": secrets.token_hex(32),
        "jwt_expire": str(JWT_EXPIRE),
        "query_url": "/query",
        "https_enabled": "0",
        "cert_subject": "",
        "cert_not_after": "",
    }
    for k, v in defaults.items():
        cur.execute("INSERT IGNORE INTO t_config (k, v) VALUES (%s,%s)", (k, v))
    # 默认客户端（兼容旧 service_key 配置）
    cur.execute("SELECT COUNT(*) AS n FROM t_client")
    if cur.fetchone()["n"] == 0:
        cur.execute("SELECT v FROM t_config WHERE k='service_key'")
        svc_key = cur.fetchone()["v"]
        now = int(time.time())
        cur.execute(
            "INSERT INTO t_client (name,order_no,contact,cli_key,cli_token,allowed_ips,update_window,"
            "enabled,update_log,last_update,created,updated) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
            ("默认客户端", "", "兼容旧 service_key 配置", svc_key, secrets.token_hex(24),
             "", "", 1, "", 0, now, now),
        )
    conn.close()


def hash_password(pwd, salt):
    return hashlib.sha256((salt + pwd).encode("utf-8")).hexdigest()

# ---------------------------------------------------------------------------
# JWT（HMAC-SHA256）
# ---------------------------------------------------------------------------
def b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def b64url_decode(s: str) -> bytes:
    pad = "=" * (-len(s) % 4)
    return base64.urlsafe_b64decode(s + pad)


def make_jwt(payload: dict, secret: str) -> str:
    header = b64url(json.dumps({"alg": "HS256", "typ": "JWT"}, separators=(",", ":")).encode())
    body = b64url(json.dumps(payload, separators=(",", ":")).encode())
    sign = b64url(hmac.new(secret.encode(), f"{header}.{body}".encode(), hashlib.sha256).digest())
    return f"{header}.{body}.{sign}"


def verify_jwt(token: str, secret: str):
    try:
        header, body, sign = token.split(".")
        expect = b64url(hmac.new(secret.encode(), f"{header}.{body}".encode(), hashlib.sha256).digest())
        if not hmac.compare_digest(sign, expect):
            return None
        payload = json.loads(b64url_decode(body))
        if payload.get("exp", 0) < time.time():
            return None
        return payload
    except Exception:
        return None

# ---------------------------------------------------------------------------
# 情报匹配
# ---------------------------------------------------------------------------
def match_ioc(conn, query):
    rows = []
    for ioc_type in IOC_TYPES:
        value = query.get(ioc_type, "").strip()
        if not value:
            continue
        now = int(time.time())
        cur = conn.cursor()
        cur.execute(
            "SELECT * FROM t_ioc WHERE type=%s AND (expire=0 OR expire>%s) "
            "AND (value=%s OR %s LIKE REPLACE(value,'*','%%')) LIMIT 50",
            (ioc_type, now, value, value),
        )
        rows.extend(cur.fetchall())
    return rows


def ioc_to_intel(r):
    return {
        "ip": r["value"] if r["type"] == "ip" else "",
        "domain": r["value"] if r["type"] == "domain" else "",
        "url": r["value"] if r["type"] == "url" else "",
        "hash": r["value"] if r["type"] == "hash" else "",
        "threat": r["threat"],
        "score": r["score"],
        "tag": r["tags"],
        "source": r["source"],
        "confidence": r["confidence"],
    }


# ---------------------------------------------------------------------------
# 开源情报源：拉取适配器 + 入库 + 定时调度
# ---------------------------------------------------------------------------
PULL_LOCK = threading.Lock()
PULL_LOCKS = {}


def http_get_text(url, api_key="", timeout=60):
    """标准库拉取文本内容（带 UA，可选 Bearer 认证），失败抛异常。"""
    req = urllib.request.Request(url, headers={"User-Agent": HTTP_UA})
    if api_key:
        req.add_header("Authorization", "Bearer " + api_key)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", errors="replace")


def classify_ioc(value):
    """自动归类原始值为 ip/domain/url/hash，返回 (type, 规范化值) 或 (None, None)。"""
    v = str(value or "").strip().strip('"')
    if not v:
        return None, None
    try:
        ipaddress.ip_address(v)
        return "ip", v
    except ValueError:
        pass
    m = re.match(r"^(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):\d+$", v)
    if m:
        return "ip", m.group(1)
    if v.startswith(("http://", "https://")):
        return "url", v
    if re.match(r"^[0-9a-fA-F]{32}$", v):
        return "hash", v.lower()
    if re.match(r"^[0-9a-fA-F]{40}$", v):
        return "hash", v.lower()
    if re.match(r"^[0-9a-fA-F]{64}$", v):
        return "hash", v.lower()
    if re.match(r"^[a-zA-Z0-9._-]+\.[a-zA-Z]{2,}$", v):
        return "domain", v.lower()
    return None, None


def store_iocs_bulk(conn, cur, items, source_name):
    """批量入库：items=[(type,value,threat,score,tags,confidence,expire)]。
    先加载全库 (type,value) 去重集合，新条目批量 INSERT，已有条目 UPDATE。返回 (new, update)。"""
    cur.execute("SELECT type, value FROM t_ioc")
    seen = {(r["type"], r["value"]) for r in cur.fetchall()}
    now = int(time.time())
    batch = []
    cnt_new = cnt_upd = 0
    for t, v, threat, score, tags, conf, expire in items:
        if not t or not v:
            continue
        # 字段长度保护（t_ioc 列宽限制，超长值直接跳过或截断）
        if len(v) > 510:
            continue
        threat = (threat or "")[:60]
        tags = (tags or "")[:250]
        src = (source_name or "")[:250]
        key = (t, v)
        if key in seen:
            cur.execute(
                "UPDATE t_ioc SET threat=%s, score=%s, tags=%s, source=%s, confidence=%s, "
                "expire=%s, updated=%s WHERE type=%s AND value=%s",
                (threat, score, tags, src, conf, expire, now, t, v),
            )
            cnt_upd += 1
        else:
            seen.add(key)
            batch.append((t, v, threat, score, tags, src, conf, expire, "", now, now))
            cnt_new += 1
        if len(batch) >= 2000:
            cur.executemany(
                "INSERT INTO t_ioc (type,value,threat,score,tags,source,confidence,expire,note,created,updated) "
                "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", batch,
            )
            batch = []
    if batch:
        cur.executemany(
            "INSERT INTO t_ioc (type,value,threat,score,tags,source,confidence,expire,note,created,updated) "
            "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", batch,
        )
    conn.commit()
    return cnt_new, cnt_upd


def _parse_csv_lines(text, use_first_as_header=False):
    """通用 CSV 解析：过滤 # 注释行；use_first_as_header=True 时首行非注释行为表头。返回 (header, rows)。"""
    data_lines = [l for l in text.splitlines() if l.strip() and not l.strip().startswith("#")]
    if not data_lines:
        return None, []
    rows = list(csv.reader(data_lines))
    if use_first_as_header:
        header = [c.strip().strip('"') for c in rows[0]]
        return header, rows[1:]
    return None, rows


def clean_source_iocs(conn, cur, source, keep_days):
    """清理该源保留天数前的旧条目，返回删除条数。"""
    if not keep_days:
        return 0
    cutoff = int(time.time()) - keep_days * 86400
    cur.execute("DELETE FROM t_ioc WHERE source=%s AND created<%s", (source["name"], cutoff))
    return cur.rowcount


def _threatfox_rows(text):
    """解析 ThreatFox CSV：注释行（# 开头，其中 '# "列名...' 为表头），数据行为标准 CSV。"""
    header = None
    data_lines = []
    for line in text.splitlines():
        s = line.strip()
        if not s:
            continue
        if s.startswith("#"):
            if s.startswith('# "') and header is None:
                header = [c.strip().strip('"') for c in s[2:].split(",")]
            continue
        data_lines.append(s)
    if not header:
        return [], []
    return header, list(csv.reader(data_lines))


def pull_threatfox(conn, cur, source):
    """ThreatFox（abuse.ch）公开 CSV 适配器：ioc_value/threat_type/ioc_type/malware_printable/confidence_level/tags。"""
    url = (source["url"] or "").strip() or DEFAULT_THREATFOX_URL
    text = http_get_text(url, source["api_key"])
    header, rows = _threatfox_rows(text)
    if not header or not rows:
        return {"ok": False, "msg": "ThreatFox 返回数据为空或格式不识别"}

    def col(row, name):
        try:
            return (row[header.index(name)] or "").strip().strip('"')
        except (ValueError, IndexError):
            return ""

    tf_type = {
        "ip": "ip", "ip:port": "ip", "domain": "domain", "url": "url",
        "md5_hash": "hash", "sha1_hash": "hash", "sha256_hash": "hash",
    }
    score_map = {
        "botnet_cc": 95, "c2": 95, "ransomware": 95, "payload_delivery": 90,
        "malware": 85, "trojan": 85, "phishing": 80, "scan": 65, "anonymous": 60,
    }
    now = int(time.time())
    expire = now + source["keep_days"] * 86400 if source["keep_days"] else 0
    items = []
    for row in rows:
        ioc = col(row, "ioc_value")
        if not ioc:
            continue
        ioc_type = tf_type.get(col(row, "ioc_type").lower())
        if not ioc_type:
            ioc_type, norm = classify_ioc(ioc)
            ioc = norm or ioc
        if not ioc_type:
            continue
        if ioc_type == "ip" and ":" in ioc and not ioc.startswith(("http://", "https://")):
            m = re.match(r"^(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):\d+$", ioc)
            if m:
                ioc = m.group(1)
        threat = col(row, "threat_type").replace("_", " ")
        malware = col(row, "malware_printable")
        tags = col(row, "tags")
        if malware and malware != "None" and malware not in tags:
            tags = (malware + "," + tags) if tags else malware
        try:
            confidence = int(col(row, "confidence_level") or 50)
        except Exception:
            confidence = 50
        score = score_map.get(col(row, "threat_type"), 75)
        items.append((ioc_type, ioc, threat, score, tags, confidence, expire))
    cnt_new, cnt_upd = store_iocs_bulk(conn, cur, items, source["name"])
    removed = clean_source_iocs(conn, cur, source, source["keep_days"])
    conn.commit()
    return {"ok": True, "msg": "ThreatFox 拉取成功", "new": cnt_new, "update": cnt_upd, "removed": removed}


def pull_csv(conn, cur, source):
    """通用 CSV 适配器：mapping JSON 指定列（{\"skip_header\":true,\"cols\":{\"ioc\":0,\"type\":1,...}}，-1=无）。"""
    text = http_get_text(source["url"], source["api_key"])
    mapping = {}
    try:
        mapping = json.loads(source["mapping"] or "{}")
    except Exception:
        pass
    cols = mapping.get("cols", {})
    rows = list(csv.reader(io.StringIO(text)))
    if mapping.get("skip_header") and rows:
        rows = rows[1:]
    def col(i, row):
        idx = cols.get(i, -1)
        if idx is None or idx < 0 or idx >= len(row):
            return ""
        return (row[idx] or "").strip().strip('"')
    now = int(time.time())
    expire = now + source["keep_days"] * 86400 if source["keep_days"] else 0
    items = []
    for row in rows:
        if not row or not any(c.strip() for c in row):
            continue
        ioc = col("ioc", row)
        if not ioc:
            continue
        ioc_type = (col("type", row) or "").lower()
        if ioc_type not in IOC_TYPES:
            ioc_type, norm = classify_ioc(ioc)
            ioc = norm or ioc
        if not ioc_type:
            continue
        try:
            score = int(col("score", row) or 75)
        except Exception:
            score = 75
        try:
            confidence = int(col("confidence", row) or 80)
        except Exception:
            confidence = 80
        items.append((ioc_type, ioc, col("threat", row), score, col("tags", row), confidence, expire))
    cnt_new, cnt_upd = store_iocs_bulk(conn, cur, items, source["name"])
    removed = clean_source_iocs(conn, cur, source, source["keep_days"])
    conn.commit()
    return {"ok": True, "msg": "CSV 拉取成功", "new": cnt_new, "update": cnt_upd, "removed": removed}


def pull_urlhaus(conn, cur, source):
    """URLhaus（abuse.ch）适配器：无表头 CSV，固定列序 id,dateadded,url,url_status,last_online,threat,tags,link,reporter。"""
    url = (source["url"] or "").strip() or DEFAULT_URLHAUS_URL
    text = http_get_text(url, source["api_key"])
    _, rows = _parse_csv_lines(text)
    if not rows:
        return {"ok": False, "msg": "URLhaus 返回数据为空"}
    score_map = {
        "malware_download": 90, "malware": 85, "botnet_cc": 95, "c2": 95,
        "ransomware": 95, "phishing": 80, "banking": 85, "coinminer": 80,
    }
    now = int(time.time())
    expire = now + source["keep_days"] * 86400 if source["keep_days"] else 0
    items = []
    for row in rows:
        if len(row) < 7:
            continue
        u = (row[2] or "").strip().strip('"')
        if not u:
            continue
        ioc_type, norm = classify_ioc(u)
        if not ioc_type:
            continue
        threat = (row[5] or "").strip().strip('"').replace("_", " ")
        tags = (row[6] or "").strip().strip('"')
        score = score_map.get(threat.replace(" ", "_"), 75)
        items.append((ioc_type, norm, threat, score, tags, 90, expire))
    cnt_new, cnt_upd = store_iocs_bulk(conn, cur, items, source["name"])
    removed = clean_source_iocs(conn, cur, source, source["keep_days"])
    conn.commit()
    return {"ok": True, "msg": "URLhaus 拉取成功", "new": cnt_new, "update": cnt_upd, "removed": removed}


def pull_feodo(conn, cur, source):
    """Feodo Tracker（abuse.ch）适配器：表头含 dst_ip/dst_port/c2_status/malware，僵尸网络 C2 情报。"""
    url = (source["url"] or "").strip() or DEFAULT_FEODO_URL
    text = http_get_text(url, source["api_key"])
    header, rows = _parse_csv_lines(text, use_first_as_header=True)
    if not header or not rows:
        return {"ok": False, "msg": "Feodo Tracker 返回数据为空"}

    def col(row, name):
        try:
            return (row[header.index(name)] or "").strip().strip('"')
        except (ValueError, IndexError):
            return ""

    now = int(time.time())
    expire = now + source["keep_days"] * 86400 if source["keep_days"] else 0
    items = []
    for row in rows:
        ip = col(row, "dst_ip")
        ioc_type, norm = classify_ioc(ip)
        if not ioc_type:
            continue
        malware = col(row, "malware")
        tags = malware if malware and malware != "None" else ""
        items.append((ioc_type, norm, "botnet c2", 95, tags, 90, expire))
    cnt_new, cnt_upd = store_iocs_bulk(conn, cur, items, source["name"])
    removed = clean_source_iocs(conn, cur, source, source["keep_days"])
    conn.commit()
    return {"ok": True, "msg": "Feodo Tracker 拉取成功", "new": cnt_new, "update": cnt_upd, "removed": removed}


def pull_iplist(conn, cur, source):
    """纯文本 IP 列表适配器：每行一个 IP/CIDR（支持 # 注释与空格分隔）；mapping 可配默认威胁/评分/标签/置信度。"""
    text = http_get_text(source["url"], source["api_key"])
    mapping = {}
    try:
        mapping = json.loads(source["mapping"] or "{}")
    except Exception:
        pass
    default_threat = str(mapping.get("threat", "")).strip()
    default_tags = str(mapping.get("tags", "")).strip()
    try:
        default_score = int(mapping.get("score", 70) or 70)
    except Exception:
        default_score = 70
    try:
        default_confidence = int(mapping.get("confidence", 80) or 80)
    except Exception:
        default_confidence = 80
    now = int(time.time())
    expire = now + source["keep_days"] * 86400 if source["keep_days"] else 0
    items = []
    seen = set()
    for line in text.splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        tok = s.split()[0] if s.split() else ""
        if "/" in tok:
            tok = tok.split("/")[0]
        ioc_type, norm = classify_ioc(tok)
        if ioc_type != "ip" or norm in seen:
            continue
        seen.add(norm)
        items.append((ioc_type, norm, default_threat, default_score, default_tags, default_confidence, expire))
    cnt_new, cnt_upd = store_iocs_bulk(conn, cur, items, source["name"])
    removed = clean_source_iocs(conn, cur, source, source["keep_days"])
    conn.commit()
    return {"ok": True, "msg": "IP 列表拉取成功", "new": cnt_new, "update": cnt_upd, "removed": removed}


def do_pull(conn, source):
    """按源类型执行拉取，更新状态与日志；返回结果 dict。"""
    cur = conn.cursor()
    started = time.time()
    try:
        if source["type"] == "threatfox":
            res = pull_threatfox(conn, cur, source)
        elif source["type"] == "urlhaus":
            res = pull_urlhaus(conn, cur, source)
        elif source["type"] == "feodo":
            res = pull_feodo(conn, cur, source)
        elif source["type"] == "iplist":
            res = pull_iplist(conn, cur, source)
        elif source["type"] == "csv":
            res = pull_csv(conn, cur, source)
        else:
            res = {"ok": False, "msg": "不支持的情报源类型: %s" % source["type"]}
    except Exception as e:
        res = {"ok": False, "msg": "%s: %s" % (type(e).__name__, e)}
    now = int(time.time())
    if res.get("ok"):
        total = res.get("new", 0) + res.get("update", 0)
        log_line = "[%s] 拉取成功 %d 条（新增 %d / 更新 %d / 清理 %d），耗时 %.1fs" % (
            time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(now)),
            total, res.get("new", 0), res.get("update", 0), res.get("removed", 0),
            time.time() - started,
        )
        cur.execute(
            "UPDATE t_source SET last_pull=%s, last_status='ok', last_count=%s, last_error='', "
            "pull_log=%s, updated=%s WHERE id=%s",
            (now, total, _append_log(source["pull_log"], log_line), now, source["id"]),
        )
    else:
        log_line = "[%s] 拉取失败: %s" % (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(now)), res["msg"])
        cur.execute(
            "UPDATE t_source SET last_pull=%s, last_status='fail', last_count=0, "
            "last_error=%s, pull_log=%s, updated=%s WHERE id=%s",
            (now, res["msg"][:500], _append_log(source["pull_log"], log_line), now, source["id"]),
        )
    conn.commit()
    return res


def _append_log(old_log, line):
    lines = (old_log or "").splitlines()
    lines.append(line)
    return "\n".join(lines[-20:])


def pull_source_worker(source_id):
    """带并发锁的拉取入口（供 API 与调度线程共用），返回结果 dict。"""
    with PULL_LOCK:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT * FROM t_source WHERE id=%s", (source_id,))
        source = cur.fetchone()
        if not source:
            conn.close()
            return {"ok": False, "msg": "情报源不存在"}
        lock = PULL_LOCKS.setdefault(source["id"], threading.Lock())
        if not lock.acquire(blocking=False):
            conn.close()
            return {"ok": False, "msg": "该源正在拉取中，请稍候"}
        try:
            return do_pull(conn, source)
        finally:
            lock.release()
            conn.close()


def source_scheduler(stop_event):
    """后台调度线程：每 60 秒检查启用中的情报源，到期自动拉取。"""
    while not stop_event.is_set():
        try:
            conn = get_db()
            cur = conn.cursor()
            cur.execute("SELECT id, last_pull, interval_min FROM t_source WHERE enabled=1")
            sources = cur.fetchall()
            conn.close()
            now = int(time.time())
            for s in sources:
                interval = max(10, s["interval_min"] or 1440) * 60
                if now - s["last_pull"] >= interval:
                    try:
                        pull_source_worker(s["id"])
                    except Exception:
                        pass
        except Exception:
            pass
        stop_event.wait(60)


# ---------------------------------------------------------------------------
# 客户端认证（key / token / 来源 IP / 更新时间窗口）
# ---------------------------------------------------------------------------
def ip_in_allowed(client_ip, allowed_ips):
    """校验来源 IP 是否在客户端允许列表（逗号分隔，支持单 IP 与 CIDR；空=不限制）。"""
    if not allowed_ips or not client_ip:
        return True
    try:
        addr = ipaddress.ip_address(client_ip)
    except ValueError:
        return False
    for item in allowed_ips.split(","):
        item = item.strip()
        if not item:
            continue
        try:
            if "/" in item:
                if addr in ipaddress.ip_network(item, strict=False):
                    return True
            elif addr == ipaddress.ip_address(item):
                return True
        except ValueError:
            continue
    return False


def client_by_key(cur, key):
    cur.execute("SELECT * FROM t_client WHERE cli_key=%s", (key,))
    return cur.fetchone()


def client_by_token(cur, token):
    cur.execute("SELECT * FROM t_client WHERE cli_token=%s", (token,))
    return cur.fetchone()


def client_check(cur, client_row, client_ip):
    """校验客户端启用状态与来源 IP，返回 (ok, msg)。"""
    if not client_row:
        return False, "client invalid"
    if client_row["enabled"] != 1:
        return False, "client disabled"
    if not ip_in_allowed(client_ip, client_row["allowed_ips"]):
        return False, "ip not allowed"
    return True, ""


def window_check(update_window):
    """校验当前日期是否已超过允许更新截止日期（空=不限）。格式 YYYY-MM-DD。"""
    if not update_window:
        return True, ""
    try:
        deadline = time.strptime(update_window, "%Y-%m-%d")
        today = time.strptime(time.strftime("%Y-%m-%d"), "%Y-%m-%d")
        return deadline >= today, "已超过允许更新截止日期（%s）" % update_window
    except Exception:
        # 兼容旧格式数据（HH:MM-HH:MM）与异常值：视为不限
        return True, ""

# ---------------------------------------------------------------------------
# HTTP 服务（双端口）
# ---------------------------------------------------------------------------
SESSIONS = {}


def make_handler(role):
    """按角色生成 Handler 子类：manage=管理端口，query=查询端口。"""

    class Handler(http.server.BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.1"
        server_role = role

        def log_message(self, fmt, *args):
            pass

        def _send(self, code, body, ctype="application/json; charset=utf-8"):
            data = body if isinstance(body, bytes) else json.dumps(body, ensure_ascii=False).encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", "GET,POST,PUT,DELETE,OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type,Authorization")
            self.end_headers()
            try:
                self.wfile.write(data)
            except (BrokenPipeError, ConnectionResetError):
                pass

        def _json(self, code, obj):
            self._send(code, obj)

        def _read_json(self):
            try:
                n = int(self.headers.get("Content-Length", 0))
                if n <= 0:
                    return {}
                return json.loads(self.rfile.read(n).decode("utf-8"))
            except Exception:
                return {}

        def _query_params(self):
            u = urllib.parse.urlparse(self.path)
            return urllib.parse.parse_qs(u.query)

        def _check_session(self):
            auth = self.headers.get("Authorization", "")
            token = auth[7:] if auth.startswith("Bearer ") else ""
            sess = SESSIONS.get(token)
            if not sess:
                return None
            if sess[1] < time.time():
                SESSIONS.pop(token, None)
                return None
            return sess[0]

        def do_OPTIONS(self):
            self._send(200, {})

        def do_GET(self):
            self._route("GET")

        def do_POST(self):
            self._route("POST")

        def do_PUT(self):
            self._route("PUT")

        def do_DELETE(self):
            self._route("DELETE")

        def _route(self, method):
            u = urllib.parse.urlparse(self.path)
            path = u.path
            q = self._query_params()

            # ============ 查询端口：仅对外情报查询协议 ============
            if self.server_role == "query":
                if path == "/query" and method in ("GET", "POST"):
                    return self.api_query(q)
                if path == "/export" and method in ("GET", "POST"):
                    return self.api_export(q)
                if path in ("/", "") and method == "POST":
                    return self.api_query(q)
                if path in ("/", "") and method == "GET" and q.get("jwt"):
                    return self.api_query(q)
                if path == "/apisix/plugin/jwt/sign":
                    return self.api_sign(q)
                return self._json(404, {"code": 404, "msg": "查询端口仅提供情报查询接口"})

            # ============ 管理端口：界面 + 管理 API ============
            if path == "/api/login" and method == "POST":
                return self.api_login()
            # 静态界面（页面本身可访问）
            if method == "GET" and path in ("/", "/index.html"):
                return self._serve_static("index.html")
            if method == "GET" and path.startswith("/static/"):
                return self._serve_static(path[len("/static/"):])
            # 证书状态查询无需登录（界面展示需要）
            if path == "/api/cert" and method == "GET":
                return self.api_cert_status()
            # 以下均需登录
            if not self._check_session():
                return self._json(401, {"code": 401, "msg": "未登录或会话已过期"})
            if path == "/api/logout" and method == "POST":
                return self.api_logout()
            if path == "/api/stats" and method == "GET":
                return self.api_stats()
            if path == "/api/config" and method == "GET":
                return self.api_config_get()
            if path == "/api/config" and method == "POST":
                return self.api_config_set()
            if path == "/api/password" and method == "POST":
                return self.api_password()
            if path == "/api/cert" and method == "POST":
                return self.api_cert_upload()
            if path == "/api/clients" and method == "GET":
                return self.api_client_list()
            if path == "/api/clients" and method == "POST":
                return self.api_client_add()
            if path.startswith("/api/clients/") and method == "PUT":
                return self.api_client_update(path)
            if path.startswith("/api/clients/") and method == "DELETE":
                return self.api_client_delete(path)
            if path.startswith("/api/clients/") and path.endswith("/regen") and method == "POST":
                return self.api_client_regen(path)
            if path.startswith("/api/clients/") and path.endswith("/log") and method == "GET":
                return self.api_client_log(path)
            if path == "/api/iocs" and method == "GET":
                return self.api_ioc_list(q)
            if path == "/api/iocs" and method == "POST":
                return self.api_ioc_add()
            if path == "/api/iocs/batch" and method == "POST":
                return self.api_ioc_batch()
            if path.startswith("/api/iocs/") and method == "PUT":
                return self.api_ioc_update(path)
            if path.startswith("/api/iocs/") and method == "DELETE":
                return self.api_ioc_delete(path)
            if path == "/api/sources" and method == "GET":
                return self.api_source_list()
            if path == "/api/sources" and method == "POST":
                return self.api_source_add()
            if path.startswith("/api/sources/") and path.endswith("/pull") and method == "POST":
                return self.api_source_pull(path)
            if path.startswith("/api/sources/") and path.endswith("/log") and method == "GET":
                return self.api_source_log(path)
            if path.startswith("/api/sources/") and method == "PUT":
                return self.api_source_update(path)
            if path.startswith("/api/sources/") and method == "DELETE":
                return self.api_source_delete(path)
            return self._json(404, {"code": 404, "msg": "接口不存在"})

        def _serve_static(self, name):
            fp = os.path.normpath(os.path.join(STATIC_DIR, name))
            if not fp.startswith(STATIC_DIR) or not os.path.isfile(fp):
                return self._json(404, {"code": 404, "msg": "文件不存在"})
            ext = os.path.splitext(fp)[1].lower()
            ctype = {
                ".html": "text/html; charset=utf-8",
                ".css": "text/css; charset=utf-8",
                ".js": "application/javascript; charset=utf-8",
            }.get(ext, "application/octet-stream")
            with open(fp, "rb") as f:
                self._send(200, f.read(), ctype)

        # ---------- 对外查询协议 ----------
        def api_sign(self, q):
            key = q.get("key", [""])[0]
            if not key:
                return self._json(403, {"code": 403, "msg": "key invalid"})
            conn = get_db()
            cur = conn.cursor()
            client_ip = self.client_address[0]
            cid = 0
            # 优先匹配客户端 key（校验启用 + 来源 IP）
            row = client_by_key(cur, key)
            if row:
                ok, msg = client_check(cur, row, client_ip)
                if not ok:
                    conn.close()
                    return self._json(403, {"code": 403, "msg": msg})
                cid = row["id"]
            else:
                # 兼容旧 service_key 配置
                cur.execute("SELECT v FROM t_config WHERE k='service_key'")
                svc = cur.fetchone()
                if not svc or not hmac.compare_digest(svc["v"], key):
                    conn.close()
                    return self._json(403, {"code": 403, "msg": "key invalid"})
            cur.execute("SELECT v FROM t_config WHERE k='jwt_secret'")
            secret = cur.fetchone()["v"]
            cur.execute("SELECT v FROM t_config WHERE k='jwt_expire'")
            expire = int(cur.fetchone()["v"])
            conn.close()
            token = make_jwt({"sub": "ti_query", "cid": cid, "exp": int(time.time()) + expire}, secret)
            # 兼容流影 threatinfo：响应体即 token（客户端直接拼接 URL，不解析 JSON）
            self._send(200, token.encode("utf-8"), "text/plain; charset=utf-8")

        def api_query(self, q):
            conn = get_db()
            cur = conn.cursor()
            client_ip = self.client_address[0]
            cur.execute("SELECT v FROM t_config WHERE k='jwt_secret'")
            secret = cur.fetchone()["v"]
            jwt = q.get("jwt", [""])[0]
            token = q.get("token", [""])[0]
            cid = 0
            if token:
                # 客户端长期 token 直查
                row = client_by_token(cur, token)
                ok, msg = client_check(cur, row, client_ip)
                if not ok:
                    conn.close()
                    return self._json(403, {"code": 403, "msg": msg})
                cid = row["id"]
            elif jwt and verify_jwt(jwt, secret):
                payload = verify_jwt(jwt, secret)
                cid = int(payload.get("cid", 0))
                if cid > 0:
                    cur.execute("SELECT * FROM t_client WHERE id=%s", (cid,))
                    row = cur.fetchone()
                    ok, msg = client_check(cur, row, client_ip)
                    if not ok:
                        conn.close()
                        return self._json(403, {"code": 403, "msg": msg})
            else:
                conn.close()
                return self._json(403, {"code": 403, "msg": "token invalid"})
            query = {k: (v[0] if isinstance(v, list) else v) for k, v in q.items()}
            rows = match_ioc(conn, query)
            conn.close()
            return self._json(200, [ioc_to_intel(r) for r in rows])

        def api_export(self, q):
            """全量情报导出（客户端离线更新），校验 token + 启用 + IP + 更新截止日期。"""
            token = q.get("token", [""])[0]
            conn = get_db()
            cur = conn.cursor()
            client_ip = self.client_address[0]
            row = client_by_token(cur, token)
            ok, msg = client_check(cur, row, client_ip)
            if not ok:
                conn.close()
                return self._json(403, {"code": 403, "msg": msg})
            win_ok, win_msg = window_check(row["update_window"])
            if not win_ok:
                conn.close()
                return self._json(403, {"code": 403, "msg": win_msg})
            cur.execute("SELECT * FROM t_ioc")
            rows = cur.fetchall()
            now = int(time.time())
            log_line = f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 来自 {client_ip} 导出 {len(rows)} 条"
            new_log = (row["update_log"] + "\n" + log_line).strip()
            cur.execute("UPDATE t_client SET update_log=%s, last_update=%s WHERE id=%s",
                        (new_log, now, row["id"]))
            conn.commit()
            conn.close()
            return self._json(200, {"code": 200, "total": len(rows), "exported_at": now,
                                    "data": [ioc_to_intel(r) for r in rows]})

        # ---------- 管理 API ----------
        def api_login(self):
            data = self._read_json()
            user = str(data.get("user", ""))
            pwd = str(data.get("pass", ""))
            conn = get_db()
            cur = conn.cursor()
            cur.execute("SELECT * FROM t_user WHERE user=%s", (user,))
            row = cur.fetchone()
            conn.close()
            if not row or hash_password(pwd, row["salt"]) != row["pass_hash"]:
                return self._json(401, {"code": 401, "msg": "用户名或密码错误"})
            token = secrets.token_hex(32)
            SESSIONS[token] = (user, time.time() + SESSION_TIMEOUT)
            return self._json(200, {"code": 200, "token": token, "user": user})

        def api_logout(self):
            auth = self.headers.get("Authorization", "")
            token = auth[7:] if auth.startswith("Bearer ") else ""
            SESSIONS.pop(token, None)
            return self._json(200, {"code": 200, "msg": "已退出"})

        def api_stats(self):
            conn = get_db()
            cur = conn.cursor()
            stats = {}
            for t in IOC_TYPES:
                cur.execute("SELECT COUNT(*) AS n FROM t_ioc WHERE type=%s", (t,))
                stats[t] = cur.fetchone()["n"]
            cur.execute("SELECT COUNT(*) AS n FROM t_ioc")
            total = cur.fetchone()["n"]
            cur.execute("SELECT COUNT(*) AS n FROM t_ioc WHERE expire>0 AND expire<%s", (int(time.time()),))
            expired = cur.fetchone()["n"]
            conn.close()
            return self._json(200, {"code": 200, "total": total, "expired": expired, "by_type": stats})

        def api_config_get(self):
            conn = get_db()
            cur = conn.cursor()
            cur.execute("SELECT * FROM t_config")
            cfg = {r["k"]: r["v"] for r in cur.fetchall()}
            conn.close()
            return self._json(200, {"code": 200, "config": cfg})

        def api_config_set(self):
            data = self._read_json()
            allowed = ("service_key", "jwt_secret", "jwt_expire", "query_url")
            conn = get_db()
            cur = conn.cursor()
            for k in allowed:
                if k in data and str(data[k]):
                    cur.execute("UPDATE t_config SET v=%s WHERE k=%s", (str(data[k]), k))
            conn.commit()
            conn.close()
            return self._json(200, {"code": 200, "msg": "配置已保存"})

        def api_password(self):
            data = self._read_json()
            old = str(data.get("old", ""))
            new = str(data.get("new", ""))
            if len(new) < 4:
                return self._json(400, {"code": 400, "msg": "新密码至少 4 位"})
            user = self._check_session()
            conn = get_db()
            cur = conn.cursor()
            cur.execute("SELECT * FROM t_user WHERE user=%s", (user,))
            row = cur.fetchone()
            if not row or hash_password(old, row["salt"]) != row["pass_hash"]:
                conn.close()
                return self._json(401, {"code": 401, "msg": "原密码错误"})
            salt = secrets.token_hex(16)
            cur.execute("UPDATE t_user SET pass_hash=%s, salt=%s WHERE id=%s",
                        (hash_password(new, salt), salt, row["id"]))
            conn.commit()
            conn.close()
            return self._json(200, {"code": 200, "msg": "密码已修改"})

        def api_ioc_list(self, q):
            ioc_type = q.get("type", [""])[0]
            threat = q.get("threat", [""])[0]
            keyword = q.get("q", [""])[0].strip()
            page = max(1, int(q.get("page", ["1"])[0] or 1))
            size = min(200, max(1, int(q.get("size", ["20"])[0] or 20)))
            sql = "SELECT * FROM t_ioc WHERE 1=1"
            args = []
            if ioc_type in IOC_TYPES:
                sql += " AND type=%s"
                args.append(ioc_type)
            if threat:
                sql += " AND threat LIKE %s"
                args.append(f"%{threat}%")
            if keyword:
                sql += " AND (value LIKE %s OR tags LIKE %s OR note LIKE %s)"
                args += [f"%{keyword}%"] * 3
            conn = get_db()
            cur = conn.cursor()
            cur.execute(sql.replace("SELECT *", "SELECT COUNT(*) AS n"), args)
            total = cur.fetchone()["n"]
            cur.execute(sql + " ORDER BY id DESC LIMIT %s OFFSET %s", args + [size, (page - 1) * size])
            rows = cur.fetchall()
            conn.close()
            return self._json(200, {"code": 200, "total": total, "page": page,
                                    "size": size, "data": rows})

        def _validate_ioc(self, d):
            ioc_type = str(d.get("type", "")).strip()
            value = str(d.get("value", "")).strip()
            if ioc_type not in IOC_TYPES:
                return None, "类型必须为 ip/domain/url/hash"
            if not value:
                return None, "情报值不能为空"
            try:
                score = int(d.get("score", 50))
            except Exception:
                score = 50
            try:
                confidence = int(d.get("confidence", 80))
            except Exception:
                confidence = 80
            try:
                expire = int(d.get("expire", 0))
            except Exception:
                expire = 0
            return {
                "type": ioc_type, "value": value,
                "threat": str(d.get("threat", "")).strip(),
                "score": max(0, min(100, score)),
                "tags": str(d.get("tags", "")).strip(),
                "source": str(d.get("source", "")).strip(),
                "confidence": max(0, min(100, confidence)),
                "expire": expire,
                "note": str(d.get("note", "")).strip(),
            }, None

        def api_ioc_add(self):
            d, err = self._validate_ioc(self._read_json())
            if err:
                return self._json(400, {"code": 400, "msg": err})
            now = int(time.time())
            conn = get_db()
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO t_ioc (type,value,threat,score,tags,source,confidence,expire,note,created,updated) "
                "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                (d["type"], d["value"], d["threat"], d["score"], d["tags"], d["source"],
                 d["confidence"], d["expire"], d["note"], now, now),
            )
            conn.commit()
            conn.close()
            return self._json(200, {"code": 200, "msg": "已添加"})

        def api_ioc_batch(self):
            data = self._read_json()
            items = data if isinstance(data, list) else data.get("items", [])
            if not isinstance(items, list) or not items:
                return self._json(400, {"code": 400, "msg": "导入数据为空"})
            ok = 0
            now = int(time.time())
            conn = get_db()
            cur = conn.cursor()
            for item in items:
                d, err = self._validate_ioc(item)
                if err:
                    continue
                cur.execute(
                    "INSERT IGNORE INTO t_ioc (type,value,threat,score,tags,source,confidence,expire,note,created,updated) "
                    "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                    (d["type"], d["value"], d["threat"], d["score"], d["tags"], d["source"],
                     d["confidence"], d["expire"], d["note"], now, now),
                )
                ok += 1
            conn.commit()
            conn.close()
            return self._json(200, {"code": 200, "msg": f"成功导入 {ok} 条"})

        def api_ioc_update(self, path):
            ioc_id = path.split("/")[-1]
            d, err = self._validate_ioc(self._read_json())
            if err:
                return self._json(400, {"code": 400, "msg": err})
            conn = get_db()
            cur = conn.cursor()
            cur.execute(
                "UPDATE t_ioc SET type=%s,value=%s,threat=%s,score=%s,tags=%s,source=%s,"
                "confidence=%s,expire=%s,note=%s,updated=%s WHERE id=%s",
                (d["type"], d["value"], d["threat"], d["score"], d["tags"], d["source"],
                 d["confidence"], d["expire"], d["note"], int(time.time()), ioc_id),
            )
            conn.commit()
            affected = cur.rowcount
            conn.close()
            if affected == 0:
                return self._json(404, {"code": 404, "msg": "记录不存在"})
            return self._json(200, {"code": 200, "msg": "已更新"})

        def api_ioc_delete(self, path):
            ioc_id = path.split("/")[-1]
            conn = get_db()
            cur = conn.cursor()
            cur.execute("DELETE FROM t_ioc WHERE id=%s", (ioc_id,))
            conn.commit()
            affected = cur.rowcount
            conn.close()
            if affected == 0:
                return self._json(404, {"code": 404, "msg": "记录不存在"})
            return self._json(200, {"code": 200, "msg": "已删除"})

        # ---------- HTTPS 证书管理 ----------
        def api_cert_status(self):
            conn = get_db()
            cur = conn.cursor()
            cur.execute("SELECT v FROM t_config WHERE k='https_enabled'")
            enabled = cur.fetchone()["v"] == "1"
            cur.execute("SELECT v FROM t_config WHERE k='cert_subject'")
            subject = cur.fetchone()["v"]
            cur.execute("SELECT v FROM t_config WHERE k='cert_not_after'")
            not_after = cur.fetchone()["v"]
            conn.close()
            return self._json(200, {"code": 200, "has_cert": os.path.isfile(CERT_PEM),
                                    "enabled": enabled, "subject": subject,
                                    "not_after": not_after, "manage_port": MANAGE_PORT})

        def api_cert_upload(self):
            data = self._read_json()
            action = data.get("action", "")

            if action == "enable":
                if not os.path.isfile(CERT_PEM):
                    return self._json(400, {"code": 400, "msg": "尚未上传有效证书"})
                conn = get_db()
                cur = conn.cursor()
                cur.execute("UPDATE t_config SET v='1' WHERE k='https_enabled'")
                conn.commit()
                conn.close()
                return self._json(200, {"code": 200, "msg": "已启用 HTTPS，重启服务后生效"})

            if action == "disable":
                conn = get_db()
                cur = conn.cursor()
                cur.execute("UPDATE t_config SET v='0' WHERE k='https_enabled'")
                conn.commit()
                conn.close()
                return self._json(200, {"code": 200, "msg": "已停用 HTTPS，重启服务后生效"})

            # action == upload：上传 PFX 并转换
            raw = data.get("data", "")
            pfx_pass = str(data.get("pass", ""))
            try:
                pfx_data = base64.b64decode(raw)
            except Exception:
                return self._json(400, {"code": 400, "msg": "证书数据解码失败"})
            if not pfx_data:
                return self._json(400, {"code": 400, "msg": "证书内容为空"})
            os.makedirs(CERTS_DIR, exist_ok=True)
            with open(CERT_PFX, "wb") as f:
                f.write(pfx_data)
            # openssl 转换 pfx → pem + key（密码经临时文件传递，避免命令行泄露）
            pass_file = os.path.join(CERTS_DIR, ".pfx_pass")
            with open(pass_file, "w") as f:
                f.write(pfx_pass)
            r1 = subprocess.run(
                ["openssl", "pkcs12", "-in", CERT_PFX, "-clcerts", "-nokeys",
                 "-out", CERT_PEM, "-passin", f"file:{pass_file}"],
                capture_output=True, text=True,
            )
            r2 = subprocess.run(
                ["openssl", "pkcs12", "-in", CERT_PFX, "-nocerts", "-nodes",
                 "-out", CERT_KEY, "-passin", f"file:{pass_file}"],
                capture_output=True, text=True,
            )
            os.remove(pass_file)
            if r1.returncode != 0 or r2.returncode != 0 or not os.path.isfile(CERT_PEM) or not os.path.isfile(CERT_KEY):
                for p in (CERT_PEM, CERT_KEY):
                    if os.path.exists(p):
                        os.remove(p)
                return self._json(400, {"code": 400, "msg": "证书转换失败，请检查 PFX 文件与密码"})
            os.chmod(CERT_KEY, 0o600)
            # 读取证书信息
            subj, not_after = "", ""
            try:
                r3 = subprocess.run(["openssl", "x509", "-in", CERT_PEM, "-noout",
                                     "-subject", "-enddate"], capture_output=True, text=True)
                for line in r3.stdout.splitlines():
                    if line.startswith("subject="):
                        subj = line[len("subject="):]
                    if line.startswith("notAfter="):
                        not_after = line[len("notAfter="):]
            except Exception:
                pass
            conn = get_db()
            cur = conn.cursor()
            cur.execute("UPDATE t_config SET v=%s WHERE k='cert_subject'", (subj,))
            cur.execute("UPDATE t_config SET v=%s WHERE k='cert_not_after'", (not_after,))
            conn.commit()
            conn.close()
            return self._json(200, {"code": 200, "msg": "证书上传成功", "subject": subj, "not_after": not_after})

        # ---------- 客户端管理 ----------
        def api_client_list(self):
            conn = get_db()
            cur = conn.cursor()
            cur.execute("SELECT * FROM t_client ORDER BY id")
            rows = cur.fetchall()
            conn.close()
            return self._json(200, {"code": 200, "data": rows})

        def _validate_client(self, d):
            name = str(d.get("name", "")).strip()
            if not name:
                return None, "客户名称不能为空"
            allowed_ips = str(d.get("allowed_ips", "")).strip()
            for item in allowed_ips.split(","):
                item = item.strip()
                if not item:
                    continue
                try:
                    if "/" in item:
                        ipaddress.ip_network(item, strict=False)
                    else:
                        ipaddress.ip_address(item)
                except ValueError:
                    return None, f"来源 IP 格式错误: {item}"
            window = str(d.get("update_window", "")).strip()
            if window:
                try:
                    time.strptime(window, "%Y-%m-%d")
                except Exception:
                    return None, "更新截止日期格式错误（YYYY-MM-DD）"
            return {
                "name": name,
                "order_no": str(d.get("order_no", "")).strip(),
                "contact": str(d.get("contact", "")).strip(),
                "allowed_ips": allowed_ips,
                "update_window": window,
                "enabled": 1 if d.get("enabled", 1) in (1, True, "1", "true") else 0,
            }, None

        def api_client_add(self):
            d, err = self._validate_client(self._read_json())
            if err:
                return self._json(400, {"code": 400, "msg": err})
            now = int(time.time())
            conn = get_db()
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO t_client (name,order_no,contact,cli_key,cli_token,allowed_ips,update_window,"
                "enabled,update_log,last_update,created,updated) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                (d["name"], d["order_no"], d["contact"], secrets.token_hex(16), secrets.token_hex(24),
                 d["allowed_ips"], d["update_window"], d["enabled"], "", 0, now, now),
            )
            conn.commit()
            conn.close()
            return self._json(200, {"code": 200, "msg": "客户端已创建，请记录其 Key 与 Token"})

        def api_client_update(self, path):
            cid = path.split("/")[-1]
            d, err = self._validate_client(self._read_json())
            if err:
                return self._json(400, {"code": 400, "msg": err})
            conn = get_db()
            cur = conn.cursor()
            cur.execute(
                "UPDATE t_client SET name=%s,order_no=%s,contact=%s,allowed_ips=%s,"
                "update_window=%s,enabled=%s,updated=%s WHERE id=%s",
                (d["name"], d["order_no"], d["contact"], d["allowed_ips"],
                 d["update_window"], d["enabled"], int(time.time()), cid),
            )
            conn.commit()
            affected = cur.rowcount
            conn.close()
            if affected == 0:
                return self._json(404, {"code": 404, "msg": "客户端不存在"})
            return self._json(200, {"code": 200, "msg": "客户端已更新"})

        def api_client_delete(self, path):
            cid = path.split("/")[-1]
            conn = get_db()
            cur = conn.cursor()
            cur.execute("DELETE FROM t_client WHERE id=%s", (cid,))
            conn.commit()
            affected = cur.rowcount
            conn.close()
            if affected == 0:
                return self._json(404, {"code": 404, "msg": "客户端不存在"})
            return self._json(200, {"code": 200, "msg": "客户端已删除"})

        def api_client_regen(self, path):
            cid = path.split("/")[-2]
            data = self._read_json()
            kind = data.get("kind", "")
            conn = get_db()
            cur = conn.cursor()
            if kind == "key":
                new_val = secrets.token_hex(16)
                cur.execute("UPDATE t_client SET cli_key=%s, updated=%s WHERE id=%s",
                            (new_val, int(time.time()), cid))
                msg = "Key 已重新生成"
            elif kind == "token":
                new_val = secrets.token_hex(24)
                cur.execute("UPDATE t_client SET cli_token=%s, updated=%s WHERE id=%s",
                            (new_val, int(time.time()), cid))
                msg = "Token 已重新生成"
            else:
                conn.close()
                return self._json(400, {"code": 400, "msg": "kind 必须为 key 或 token"})
            conn.commit()
            cur.execute("SELECT cli_key, cli_token FROM t_client WHERE id=%s", (cid,))
            row = cur.fetchone()
            conn.close()
            if not row:
                return self._json(404, {"code": 404, "msg": "客户端不存在"})
            return self._json(200, {"code": 200, "msg": msg, "cli_key": row["cli_key"], "cli_token": row["cli_token"]})

        def api_client_log(self, path):
            cid = path.split("/")[-2]
            conn = get_db()
            cur = conn.cursor()
            cur.execute("SELECT update_log, last_update FROM t_client WHERE id=%s", (cid,))
            row = cur.fetchone()
            conn.close()
            if not row:
                return self._json(404, {"code": 404, "msg": "客户端不存在"})
            return self._json(200, {"code": 200, "last_update": row["last_update"], "log": row["update_log"]})

        # ---------- 情报源管理 ----------
        def _validate_source(self, d):
            name = str(d.get("name", "")).strip()
            if not name:
                return None, "情报源名称不能为空"
            stype = str(d.get("type", "")).strip()
            if stype not in SOURCE_TYPES:
                return None, "类型必须为 %s" % "/".join(SOURCE_TYPES)
            try:
                interval_min = max(10, int(d.get("interval_min", 1440) or 1440))
            except Exception:
                interval_min = 1440
            try:
                keep_days = max(0, int(d.get("keep_days", 30) or 0))
            except Exception:
                keep_days = 30
            return {
                "name": name,
                "type": stype,
                "url": str(d.get("url", "")).strip(),
                "api_key": str(d.get("api_key", "")).strip(),
                "interval_min": interval_min,
                "keep_days": keep_days,
                "mapping": str(d.get("mapping", "")).strip(),
                "enabled": 1 if d.get("enabled", 1) in (1, True, "1", "true") else 0,
            }, None

        def api_source_list(self):
            conn = get_db()
            cur = conn.cursor()
            cur.execute("SELECT * FROM t_source ORDER BY id")
            rows = cur.fetchall()
            conn.close()
            return self._json(200, {"code": 200, "data": rows})

        def api_source_add(self):
            d, err = self._validate_source(self._read_json())
            if err:
                return self._json(400, {"code": 400, "msg": err})
            now = int(time.time())
            conn = get_db()
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO t_source (name,type,url,api_key,interval_min,keep_days,mapping,enabled,"
                "last_pull,last_status,last_count,last_error,pull_log,created,updated) "
                "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                (d["name"], d["type"], d["url"], d["api_key"], d["interval_min"], d["keep_days"],
                 d["mapping"], d["enabled"], 0, "", 0, "", "", now, now),
            )
            conn.commit()
            sid = cur.lastrowid
            conn.close()
            return self._json(200, {"code": 200, "msg": "情报源已创建（启用后由调度线程按周期自动拉取）", "id": sid})

        def api_source_update(self, path):
            sid = path.split("/")[-1]
            d, err = self._validate_source(self._read_json())
            if err:
                return self._json(400, {"code": 400, "msg": err})
            conn = get_db()
            cur = conn.cursor()
            cur.execute(
                "UPDATE t_source SET name=%s,type=%s,url=%s,api_key=%s,interval_min=%s,keep_days=%s,"
                "mapping=%s,enabled=%s,updated=%s WHERE id=%s",
                (d["name"], d["type"], d["url"], d["api_key"], d["interval_min"], d["keep_days"],
                 d["mapping"], d["enabled"], int(time.time()), sid),
            )
            conn.commit()
            affected = cur.rowcount
            conn.close()
            if affected == 0:
                return self._json(404, {"code": 404, "msg": "情报源不存在"})
            return self._json(200, {"code": 200, "msg": "情报源已更新"})

        def api_source_delete(self, path):
            sid = path.split("/")[-1]
            conn = get_db()
            cur = conn.cursor()
            cur.execute("DELETE FROM t_source WHERE id=%s", (sid,))
            conn.commit()
            affected = cur.rowcount
            conn.close()
            if affected == 0:
                return self._json(404, {"code": 404, "msg": "情报源不存在"})
            return self._json(200, {"code": 200, "msg": "情报源已删除（已入库的情报保留）"})

        def api_source_pull(self, path):
            sid = path.split("/")[-2]
            res = pull_source_worker(int(sid))
            if res.get("ok"):
                return self._json(200, {"code": 200, "msg": res["msg"],
                                        "new": res.get("new", 0), "update": res.get("update", 0),
                                        "removed": res.get("removed", 0)})
            return self._json(400, {"code": 400, "msg": res.get("msg", "拉取失败")})

        def api_source_log(self, path):
            sid = path.split("/")[-2]
            conn = get_db()
            cur = conn.cursor()
            cur.execute("SELECT pull_log, last_pull, last_status, last_count FROM t_source WHERE id=%s", (sid,))
            row = cur.fetchone()
            conn.close()
            if not row:
                return self._json(404, {"code": 404, "msg": "情报源不存在"})
            return self._json(200, {"code": 200, "last_pull": row["last_pull"],
                                    "last_status": row["last_status"], "last_count": row["last_count"],
                                    "log": row["pull_log"]})

    return Handler


def main():
    parser = argparse.ArgumentParser(description="天鯨威胁情报服务器 v2")
    parser.add_argument("--init", action="store_true", help="初始化数据库")
    parser.add_argument("--manage-port", type=int, default=DEFAULT_MANAGE_PORT, help="管理端口")
    parser.add_argument("--query-port", type=int, default=DEFAULT_QUERY_PORT, help="查询端口")
    parser.add_argument("--host", default="0.0.0.0", help="监听地址")
    parser.add_argument("--db-host", default=os.environ.get("TI_DB_HOST", "127.0.0.1"))
    parser.add_argument("--db-user", default=os.environ.get("TI_DB_USER", "root"))
    parser.add_argument("--db-pass", default=os.environ.get("TI_DB_PASS", ""))
    parser.add_argument("--db-name", default=os.environ.get("TI_DB_NAME", "ti_server"))
    args = parser.parse_args()

    DB_CFG.update(host=args.db_host, user=args.db_user, password=args.db_pass, name=args.db_name)
    global MANAGE_PORT
    MANAGE_PORT = args.manage_port

    if not args.db_pass:
        print("[ERROR] 请通过 --db-pass 或环境变量 TI_DB_PASS 提供 MySQL 密码")
        sys.exit(1)

    if args.init:
        init_db()
        print(f"[ti_server] 数据库初始化完成: {args.db_user}@{args.db_host}/{args.db_name}")
        print(f"[ti_server] 默认管理员: {DEFAULT_ADMIN[0]}/{DEFAULT_ADMIN[1]}")
        return

    # 查询端口服务器（纯 HTTP）
    query_server = http.server.ThreadingHTTPServer((args.host, args.query_port), make_handler("query"))
    print(f"[ti_server] 查询端口: http://{args.host}:{args.query_port}（情报查询协议）")

    # 管理端口服务器（HTTPS 可选）
    manage_server = http.server.ThreadingHTTPServer((args.host, args.manage_port), make_handler("manage"))
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT v FROM t_config WHERE k='https_enabled'")
    https_enabled = cur.fetchone()["v"] == "1"
    conn.close()
    if https_enabled and os.path.isfile(CERT_PEM) and os.path.isfile(CERT_KEY):
        try:
            ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            ctx.load_cert_chain(CERT_PEM, CERT_KEY)
            manage_server.socket = ctx.wrap_socket(manage_server.socket, server_side=True)
            print(f"[ti_server] 管理端口: https://{args.host}:{args.manage_port}（HTTPS 已启用）")
        except Exception as e:
            print(f"[WARN] HTTPS 启动失败({e})，管理端口回退 HTTP: http://{args.host}:{args.manage_port}")
    else:
        print(f"[ti_server] 管理端口: http://{args.host}:{args.manage_port}")

    print(f"[ti_server] 管理界面: http{'s' if https_enabled else ''}://<ip>:{args.manage_port}/   默认账号: {DEFAULT_ADMIN[0]}/{DEFAULT_ADMIN[1]}")
    print(f"[ti_server] 数据库: {args.db_user}@{args.db_host}/{args.db_name} (MySQL)")

    # 情报源定时拉取调度线程
    stop_event = threading.Event()
    threading.Thread(target=source_scheduler, args=(stop_event,), daemon=True).start()
    print("[ti_server] 情报源调度线程已启动（每 60 秒检查一次，到期自动拉取）")

    try:
        threading.Thread(target=manage_server.serve_forever, daemon=True).start()
        query_server.serve_forever()
    except KeyboardInterrupt:
        print("\n[ti_server] 已停止")
        stop_event.set()
        manage_server.server_close()
        query_server.server_close()


if __name__ == "__main__":
    main()
