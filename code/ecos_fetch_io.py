"""
Download the Bank of Korea input-output tables (producer prices, medium and small classification)
for 2015-2024 from the public ECOS file service, with a provenance record (source, time, SHA-256).

Usage: python -I ecos_fetch_io.py <target dir>
Existing files are never overwritten. Files are untrusted downloads: only size and zip magic are checked here.
"""
import hashlib
import os
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))   # sibling helper by the same author
import ecos_client as e

NODES = {"271Y005": "2015 실측표", "271Y004": "2016 연장표", "271Y003": "2017 연장표", "271Y002": "2018 연장표",
         "271Y001": "2019 연장표", "271Y105": "2020 실측표", "271Y104": "2021 연장표", "271Y103": "2022 연장표",
         "271Y102": "2023 연장표", "271Y101": "2024 연장표"}
WANT_LEVELS = ("통합중분류", "통합소분류")
MAX_BYTES = 80 * 1024 * 1024        # [SECURE] Size cap for a downloaded file (Category 1)
BASE = "https://ecos.bok.or.kr/serviceEndpoint/fileDownload?"


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def main(argv):
    if len(argv) != 2 or not os.path.isdir(argv[1]):
        print("usage: ecos_fetch_io.py <existing target dir>")
        return 2
    out = argv[1]
    lines, bad = [], 0
    for ds, label in NODES.items():
        items = e.call("OSUUA01R02", {"dsId": ds, "fileOfrYn": "Y"})["data"]["statClfItmList"]
        for it in items:
            codes = e.call("OSUUA01R03", dict(it, dsId=ds, fileOfrYn="Y"))["data"]["statClfItmCdList"]
            name = {c["cd"]: c["cdNm"] for c in codes}
            up = {c["cd"]: c["uppCd"] for c in codes}
            for c in codes:
                parent = name.get(c["uppCd"], "")
                grand = name.get(up.get(c["uppCd"], ""), "")
                if c["cdNm"] not in WANT_LEVELS or parent != "생산자가격" or grand != "투입산출표":
                    continue
                res = e.call("OSDFA01R03", dict(c, dsId=ds, statItmId=it["statItmId"], langCd="KO")).get("data") or {}
                fp, fn = res.get("attFilePath"), res.get("attFileNm")
                if not fp or not fn:
                    print(f"NO FILE: {label} {c['cdNm']}")
                    bad += 1
                    continue
                # [SECURE] File name from the server is reduced to its base name - no path traversal (Category 1)
                safe = os.path.basename(fn.replace("\\", "/"))
                dst = os.path.join(out, safe)
                if os.path.exists(dst):
                    print(f"exists, kept: {safe}")
                    continue
                url = BASE + urllib.parse.urlencode({"filePath": fp, "fileName": fn})
                req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0", "Referer": "https://ecos.bok.or.kr/"})
                with urllib.request.urlopen(req, timeout=120) as r:
                    data = r.read(MAX_BYTES + 1)
                if len(data) > MAX_BYTES or data[:4] != b"PK\x03\x04" or len(data) < 20000:
                    print(f"REJECTED (size {len(data)} or not an xlsx container): {safe}")
                    bad += 1
                    continue
                tmp = dst + ".part"
                with open(tmp, "wb") as f:
                    f.write(data)
                os.replace(tmp, dst)        # [SECURE] Atomic placement of the finished file (Category 3)
                digest = sha256_of(dst)
                now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
                print(f"OK {len(data):>9} bytes  {safe}")
                lines.append(f"- file: {safe}\n  size_bytes: {len(data)}\n  sha256: {digest}\n  downloaded_at_utc: {now}\n"
                             f"  ecos_node: {ds} ({label}) > 투입산출표 > 생산자가격 > {c['cdNm']}\n  ecos_item_code: {c['cd']}\n")
                time.sleep(1.0)             # be polite to the public service
    if lines:
        p = os.path.join(out, "PROVENANCE_ecos_panel.txt")
        new = not os.path.exists(p)
        with open(p, "a", encoding="utf-8", newline="\n") as f:
            if new:
                f.write("# 한국은행 ECOS 산업연관표(2015~2024, 생산자가격, 통합중분류·통합소분류) - 출처 기록\n"
                        "# source: https://ecos.bok.or.kr 통계검색 > 2.2 산업연관표 > 파일 다운로드 (사이트의 파일 서비스가 내려 준 원본)\n"
                        "# note: 파일은 받은 그대로이며 수정하지 않았다.\n\n")
            f.write("\n".join(lines) + "\n")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

# --------------------------------------------------
# Security Checklist
# Applied:
#   - Untrusted download handling: size cap, zip magic check, server file name reduced to base name,
#     nothing in the files is opened or executed here (Category 1)
#   - Integrity: SHA-256 and time recorded per file; existing files never overwritten (Category 2, 3)
#   - Network: fixed HTTPS host, timeouts, bounded reads, one-second pause between files (Category 3)
# Not Applied:
#   - [WARN] Code Download Without Integrity Check: the publisher provides no checksum; authenticity rests on HTTPS
#   - [WARN] Undocumented web endpoint: request format may change without notice
# --------------------------------------------------
