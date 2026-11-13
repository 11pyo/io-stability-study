"""
Minimal client for the public ECOS web service (Bank of Korea) used to list and download the
input-output table files without a browser. Read-only; no account, no credentials.

Usage: python -I ecos_client.py tree            # list statistic nodes that offer files (I-O section)
       python -I ecos_client.py items <dsId>    # list file items of one node
"""
import json
import sys
import urllib.request

URL = "https://ecos.bok.or.kr/serviceEndpoint/httpService/request.json"
TIMEOUT = 40          # [SECURE] Every network call has a timeout (Category 3)


def call(trx, data):
    body = {"header": {"guidSeq": 1, "trxCd": trx, "scrId": "IECOSPC", "sysCd": "03", "fstChnCd": "WEB",
                       "langDvsnCd": "KO", "envDvsnCd": "D", "sndRspnDvsnCd": "S", "sndDtm": "20261113",
                       "ipAddr": "0.0.0.0", "usrId": "IECOSPC", "pageNum": 1, "pageCnt": 1000}, "data": data}
    # [SECURE] Fixed HTTPS endpoint, certificate verification left on (Category 2)
    req = urllib.request.Request(URL, data=json.dumps(body).encode("utf-8"),
                                 headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0",
                                          "Referer": "https://ecos.bok.or.kr/"})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
        return json.loads(r.read().decode("utf-8"))


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    if argv[1] == "tree":
        res = call("OSUUA01R01", {})
        rows = res.get("data", {}).get("statClfList", [])
        print("nodes:", len(rows), "| keys:", sorted(rows[0].keys()) if rows else None)
        for r in rows:
            name = str(r.get("dsNm") or r.get("statClfNm") or "")
            if r.get("fileOfrYn") == "Y" or "산업연관" in name or name.startswith("2.2"):
                print({k: r.get(k) for k in ("dsId", "uppDsId", "dsNm", "statClfNm", "fileOfrYn", "lvl", "statClfId", "uppStatClfId") if k in r})
    elif argv[1] == "items" and len(argv) >= 3:
        row = json.loads(argv[2])
        res = call("OSUUA01R02", row)
        d = res.get("data", {})
        print(json.dumps(res.get("message"), ensure_ascii=False)[:300])
        for k, v in d.items():
            print(k, len(v) if isinstance(v, list) else v)
            if isinstance(v, list):
                for x in v[:60]:
                    print("  ", json.dumps(x, ensure_ascii=False)[:300])
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

# --------------------------------------------------
# Security Checklist
# Applied:
#   - Network: fixed HTTPS endpoint, timeouts, certificate verification on (Category 2, 3)
#   - No credentials or personal data are sent; a generic client name is used
# Not Applied:
#   - [WARN] Input validation: the JSON row argument is passed through as given (operator-supplied, local script)
#   - [WARN] Undocumented web endpoint: the request format may change without notice
# --------------------------------------------------
