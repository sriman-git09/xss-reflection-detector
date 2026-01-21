#!/usr/bin/env python3
"""
Automated XSS Discovery Scanner (Bug-Bounty Safe)
GITHUB : https://github.com/sriman-git09
Author: Sriman Kundu
Purpose: Automated reflection + context discovery for XSS hunting
WARNING: Use ONLY on websites you own or have permission to test.
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, parse_qs
import uuid
import re
import sys

def banner():
    RED = "\033[91m"
    CYAN = "\033[96m"
    YELLOW = "\033[93m"
    RESET = "\033[0m"

    print(RED + r"""
██╗  ██╗███████╗███████╗
╚██╗██╔╝██╔════╝██╔════╝
 ╚███╔╝ ███████╗███████╗
 ██╔██╗ ╚════██║╚════██║
██╔╝ ██╗███████║███████║
╚═╝  ╚═╝╚══════╝╚══════╝
""" + RESET)


    print(CYAN + "Automatic XSS Reflection Scanner (Bug Bounty Safe)" + RESET)
    print(YELLOW + "Author : Sriman Kundu" + RESET)
    print(YELLOW + "GitHub : https://github.com/sriman-git09" + RESET)
    print(RED + "WARNING: Authorized testing only!" + RESET)
    print("=" * 70)



# ---------------- CONFIG ----------------
HEADERS = {"User-Agent": "BugBounty-XSS-Scanner"}
MAX_DEPTH = 2
TIMEOUT = 10

visited = set()
findings = []

# ---------------- UTIL ----------------
def same_domain(base, target):
    return urlparse(base).netloc == urlparse(target).netloc

def marker():
    return "XSS_" + uuid.uuid4().hex[:6]

# ---------------- PAYLOAD ENGINE (SAFE) ----------------
PAYLOAD_TEMPLATES = {
    "HTML Body": [
        "<x>{marker}</x>",
        "<b>{marker}</b>"
    ],
    "HTML Attribute": [
        "\"{marker}\"",
        "'{marker}'"
    ],
    "JavaScript String": [
        "'{marker}'",
        "\"{marker}\""
    ]
}

def generate_payloads(context, m):
    return [tpl.format(marker=m) for tpl in PAYLOAD_TEMPLATES.get(context, [])]

# ---------------- CONTEXT DETECTION ----------------
def detect_context(resp, m):
    if re.search(rf"<[^>]*>{m}<", resp):
        return "HTML Body"
    if re.search(rf'value="[^"]*{m}[^"]*"', resp):
        return "HTML Attribute"
    if re.search(rf'["\'].*{m}.*["\']', resp):
        return "JavaScript String"
    return "Unknown"

# ---------------- PAYLOAD TEST ----------------
def test_payload(url, method, param, payload, context):
    try:
        if method == "POST":
            r = requests.post(url, data={param: payload}, headers=HEADERS, timeout=TIMEOUT)
        else:
            r = requests.get(url, params={param: payload}, headers=HEADERS, timeout=TIMEOUT)
    except:
        return

    if payload in r.text:
        findings.append({
            "url": url,
            "method": method,
            "parameter": param,
            "context": context,
            "payload": payload
        })

# ---------------- REFLECTION TEST ----------------
def test_reflection(url, method, param):
    m = marker()

    try:
        if method == "POST":
            r = requests.post(url, data={param: m}, headers=HEADERS, timeout=TIMEOUT)
        else:
            r = requests.get(url, params={param: m}, headers=HEADERS, timeout=TIMEOUT)
    except:
        return

    if m in r.text:
        context = detect_context(r.text, m)
        payloads = generate_payloads(context, m)
        for p in payloads:
            test_payload(url, method, param, p, context)

# ---------------- PAGE ANALYSIS ----------------
def analyze_page(url, html):
    soup = BeautifulSoup(html, "html.parser")

    # URL parameters
    parsed = urlparse(url)
    for p in parse_qs(parsed.query):
        test_reflection(url, "GET", p)

    # Forms
    for form in soup.find_all("form"):
        action = form.get("action")
        method = form.get("method", "get").upper()
        target = urljoin(url, action) if action else url

        for inp in form.find_all("input"):
            name = inp.get("name")
            if name:
                test_reflection(target, method, name)

# ---------------- CRAWLER ----------------
def crawl(url, base, depth):
    if depth == 0 or url in visited:
        return
    visited.add(url)

    try:
        r = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
    except:
        return

    analyze_page(url, r.text)

    soup = BeautifulSoup(r.text, "html.parser")
    for a in soup.find_all("a", href=True):
        link = urljoin(url, a["href"])
        if same_domain(base, link):
            crawl(link, base, depth - 1)


# ---------------- REPORT ----------------
def report():
    with open("report.txt", "w") as f:
        f.write("AUTOMATED XSS DISCOVERY REPORT\n")
        f.write("=" * 45 + "\n\n")

        if not findings:
            f.write("No reflected injection points found.\n")
            return

        for i, x in enumerate(findings, 1):
            f.write(f"[{i}] Potential XSS\n")
            f.write(f"URL       : {x['url']}\n")
            f.write(f"Method    : {x['method']}\n")
            f.write(f"Parameter : {x['parameter']}\n")
            f.write(f"Context   : {x['context']}\n")
            f.write(f"Evidence  : {x['payload']}\n")
            f.write("-" * 30 + "\n")

# ---------------- MAIN ----------------
if __name__ == "__main__":
    banner()

    target = input("Enter target URL: ").strip()

    if not target.startswith("http"):
        print("[-] Invalid URL")
        sys.exit(1)

    print("[*] Crawling and testing...")
    crawl(target, target, MAX_DEPTH)

    report()
    print("[+] Done. Report saved as report.txt")
