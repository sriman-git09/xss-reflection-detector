

# 🛡️ XSS Reflection Detector
# xss-reflection-detector
Detects reflected user input in HTML responses to assist in identifying potential XSS vulnerabilities.
**Automated XSS Discovery Scanner (Bug-Bounty Safe)**  
Detects reflected user input and basic injection contexts in HTML responses to assist in identifying **potential XSS vulnerabilities**.

> ⚠️ This tool identifies *reflection and context*, not guaranteed XSS execution.  
> Manual verification is always required.

---

## 📌 Features

- ✔ Detects reflected parameters (GET & POST)
- ✔ Identifies basic reflection contexts:
  - HTML Body
  - HTML Attributes
  - JavaScript Strings
- ✔ Crawls same-domain links (depth-limited)
- ✔ Tests safe context-aware payloads
- ✔ Generates a clean text report
- ✔ ANSI colored ASCII banner
- ✔ Bug-bounty & learning friendly
- ✔ MIT Licensed

---

## 🧠 What This Tool Is (and Is Not)

### ✅ This tool **DOES**
- Help find **potential XSS injection points**
- Show **where** input is reflected
- Identify **context** of reflection
- Assist in manual bug-bounty testing

### ❌ This tool **DOES NOT**
- Confirm exploitability
- Bypass WAF / CSP
- Detect DOM-based XSS
- Auto-exploit vulnerabilities

---

## ⚙️ Requirements

- Python **3.8+**
- Internet connection
- Permission to test the target

### Python Libraries
```bash
pip3 install requests beautifulsoup4
git clone https://github.com/sriman-git09/xss-reflection-detector.git
cd xss-reflection-detector
chmod +x xss-reflection-detector.py
▶️ Usage
