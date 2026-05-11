# 🚗 Kurd Auto v2 — PythonAnywhere Setup Guide

## ١. ئەکاونتت لە PythonAnywhere درووست بکە
- بچۆ: https://www.pythonanywhere.com/registration/register/beginner/
- ئەکاونتی خۆڕای (Beginner) دروست بکە

---

## ٢. فایلەکان بارکە

لە **Files** تابەوە:
1. دوگمەی **Upload a file** بکە
2. فایلی `kurd-auto-v2.zip` بارکە
3. ئینتەرفەیسەکەی خۆی Unzip بکە لە **Bash console**:

```bash
cd ~
unzip kurd-auto-v3.zip
mv kurd-auto-v3 kurdauto
```

---

## ٣. Virtual Environment و پاکێجەکان

لە **Bash console**:

```bash
cd ~/kurdauto
python3.10 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## ٤. فایلی .env دروست بکە

```bash
cd ~/kurdauto
cp .env.example .env
nano .env
```

پڕیکەرەوە:
```
SECRET_KEY=kurd-auto-very-secret-key-change-this-2025
GMAIL_USER=yourmail@gmail.com
GMAIL_PASS=xxxx-xxxx-xxxx-xxxx
DATABASE_URL=sqlite:///kurdauto.db
```

**Gmail App Password:**
1. بچۆ: https://myaccount.google.com/apppasswords
2. App: **Mail** — Device: **Other (Custom name)**
3. ناوی **KurdAuto** بنووسە و Generate بکە
4. ئەو پاسۆردە 16 ژمارەیەی بۆ `GMAIL_PASS` کاپی بکە

---

## ٥. دەیتابەیس دروست بکە

```bash
cd ~/kurdauto
source venv/bin/activate
python3 -c "from app import create_tables; create_tables()"
```

---

## ٦. Web App دروست بکە

1. بچۆ تابی **Web**
2. دوگمەی **Add a new web app** بکە
3. **Manual Configuration** هەڵبژێرە
4. Python **3.10** هەڵبژێرە

**Source code:**
```
/home/YOURUSERNAME/kurdauto
```

**Virtualenv:**
```
/home/YOURUSERNAME/kurdauto/venv
```

---

## ٧. WSGI فایل دەستکاری بکە

لە تابی Web، **WSGI configuration file** کلیک بکە.
هەموو ناوەڕۆکەکەی بسڕەوە و ئەمەی خوارەوە بنووسە:

```python
import sys
import os
from dotenv import load_dotenv

path = '/home/YOURUSERNAME/kurdauto'
if path not in sys.path:
    sys.path.insert(0, path)

load_dotenv(os.path.join(path, '.env'))

from app import app as application
```

> ⚠️ `YOURUSERNAME` بگۆڕە بۆ ناوی ئەکاونتەکەت

---

## ٨. Static Files

لە تابی Web، بەشی **Static files**:

| URL         | Directory                              |
|-------------|----------------------------------------|
| `/static/`  | `/home/YOURUSERNAME/kurdauto/static/`  |

---

## ٩. Reload بکە ✅

دوگمەی **Reload** بکە — مەڵبەندەکەت ئامادەیە!

---

## 🔧 گرفت هەبوو؟

لە **Error log** تابەوه گرفتەکان ببینە:
```bash
tail -f /var/log/YOURUSERNAME.pythonanywhere.com.error.log
```

---

## 📋 چێک‌لیست

- [ ] zip بارکراوە و extract کراوە
- [ ] venv دروست کراوە و requirements install کراون
- [ ] .env پڕکراوەتەوە (Gmail App Password)
- [ ] دەیتابەیس دروست کراوە
- [ ] WSGI فایل دەستکاری کراوە (YOURUSERNAME گۆڕدراوە)
- [ ] Static files دانراوە
- [ ] Reload کراوە
