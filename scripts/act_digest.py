#!/usr/bin/env python3
"""Дайджест акта из source.pdf: заголовок, дата, резолютивная часть и ключевые фразы со страницами.
    act_digest.py <folder> [keyword ...]"""
import re, subprocess, sys
from pathlib import Path
d = Path(sys.argv[1]); kws = sys.argv[2:] or ["сайт","приложени","согласи","галочк","автоматич","подписк","таймер","скидк","сервисный сбор","Instagram","VPN","erid","маркировк","мелк","лучш","№ 1","штраф","рублей","предписани"]
f = d/"source.pdf"
n = int(re.search(r"Pages:\s+(\d+)", subprocess.run(["pdfinfo", str(f)], capture_output=True, text=True).stdout).group(1))
pages = []
for p in range(1, n+1):
    t = subprocess.run(["pdftotext","-f",str(p),"-l",str(p),str(f),"-"], capture_output=True, text=True).stdout
    pages.append(re.sub(r"\s+"," ",t))
(d/"source.txt").write_text("\n\n".join(f"===== стр. {i+1} =====\n{t}" for i,t in enumerate(pages)), encoding="utf-8")
full = " ".join(pages)
print(f"##### {d.name} | pages={n}")
m = re.search(r"(Решение|Постановление|Определение|Предупреждение)[^|]{0,160}?от (\d{1,2} \w+ \d{4}) г\.", pages[0]); print("header:", m.group(0)[:200] if m else pages[0][600:900])
for i,t in enumerate(pages):
    for kw in kws:
        for mm in list(re.finditer(kw, t))[:1]:
            print(f"  стр.{i+1} [{kw}] …{t[max(0,mm.start()-110):mm.start()+170]}…")
j = max(full.rfind("РЕШИЛА"), full.rfind("ПОСТАНОВИЛ"), full.rfind("О П Р Е Д Е Л И Л"), full.rfind("ОПРЕДЕЛИЛ"))
if j > 0:
    # страница резолютивной части
    acc=0; pg=None
    for i,t in enumerate(pages):
        if acc + len(t) + 1 > j: pg=i+1; break
        acc += len(t)+1
    print(f"  РЕЗОЛЮТИВНАЯ (стр.{pg}): {full[j:j+900]}")
