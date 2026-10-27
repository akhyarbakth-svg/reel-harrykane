import json, sys, time, urllib.request, urllib.parse, urllib.error
UA = {"User-Agent": "GameStateReel/1.0 (https://www.youtube.com/@GameState365) python-urllib"}
API = "https://commons.wikimedia.org/w/api.php"
def get(params):
    params["format"] = "json"
    req = urllib.request.Request(API + "?" + urllib.parse.urlencode(params), headers=UA)
    for attempt in range(6):
        time.sleep(1.0)
        try:
            return json.load(urllib.request.urlopen(req))
        except urllib.error.HTTPError as e:
            if e.code != 429: raise
            time.sleep(5 * (attempt + 1))
    raise RuntimeError("rate limited")
def members(cat):
    out, cont = [], {}
    while True:
        d = get({"action": "query", "list": "categorymembers", "cmtitle": cat, "cmlimit": 500, **cont})
        out += d["query"]["categorymembers"]
        if "continue" not in d: return out
        cont = d["continue"]
seen, files = set(), []
def walk(cat, depth):
    if cat in seen or depth < 0: return
    seen.add(cat)
    for m in members(cat):
        if m["ns"] == 14: walk(m["title"], depth - 1)
        elif m["ns"] == 6: files.append((cat, m["title"]))
walk(sys.argv[1], int(sys.argv[2]))
titles = list(dict.fromkeys(t for _, t in files))
info = {}
for i in range(0, len(titles), 40):
    d = get({"action": "query", "titles": "|".join(titles[i:i+40]), "prop": "imageinfo",
             "iiprop": "size|url|extmetadata", "iiurlwidth": 400})
    for p in d["query"]["pages"].values():
        ii = p.get("imageinfo", [{}])[0]
        md = ii.get("extmetadata", {})
        info[p["title"]] = (ii.get("width"), ii.get("height"), md.get("LicenseShortName", {}).get("value"),
                            md.get("Artist", {}).get("value", "")[:80], ii.get("thumburl"), ii.get("url"))
json.dump(info, open(sys.argv[3], "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for t in titles:
    w, h, lic, art, th, u = info.get(t, (None,)*6)
    print(f"{w}x{h}\t{lic}\t{t}")
