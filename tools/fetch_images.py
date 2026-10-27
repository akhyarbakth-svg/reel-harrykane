import json, sys, time, urllib.request, urllib.parse, re, html
sys.stdout.reconfigure(encoding="utf-8")
UA = {"User-Agent": "GameStateReel/1.0 (https://www.youtube.com/@GameState365) python-urllib"}
API = "https://commons.wikimedia.org/w/api.php"
picks = {
 "hook":     "File:FC Red Bull Salzburg gegen Bayern München (2025-01-06 Testspiel) 29.jpg",
 "scan":     "File:Harry Kane 9 England v Ghana at 2026 Fifa World Cup by YantsImages 04.jpg",
 "origins":  "File:Harry Kane mural.jpg",
 "young":    "File:Harry Kane.jpg",
 "spurs18":  "File:Chelsea 2 Spurs 0 Capital One Cup winners 2015 (16505807198).jpg",
 "spurs10":  "File:Manchester United v Tottenham Hotspur, 12 March 2022 (24).jpg",
 "eng2018":  "File:Harry Kane 2018-07-03 1.jpg",
 "england":  "File:Harry Kane England v Panama 27 June 26-184.jpg",
 "locker":   "File:Allianz Arena (25-11-2023) 08.jpg",
 "bayern":   "File:FC Red Bull Salzburg gegen Bayern München (2025-01-06 Testspiel) 17.jpg",
 "bayern2":  "File:FC Red Bull Salzburg gegen Bayern München (2025-01-06 Testspiel) 86.jpg",
 "action":   "File:Harry Kane England v Panama 27 June 26-141.jpg",
 "final":    "File:Harry Kane England v Ghana 23 June 2026-219.jpg",
}
def api(params):
    params["format"] = "json"
    for a in range(6):
        time.sleep(1)
        try:
            return json.load(urllib.request.urlopen(urllib.request.Request(API + "?" + urllib.parse.urlencode(params), headers=UA)))
        except urllib.error.HTTPError as e:
            if e.code != 429: raise
            time.sleep(5 * (a + 1))
def clean(s): return html.unescape(re.sub("<[^>]+>", "", s or "")).strip()
out = sys.argv[1]
credits = []
for key, title in picks.items():
    d = api({"action": "query", "titles": title, "prop": "imageinfo", "iiprop": "url|size|extmetadata", "iiurlwidth": 2000})
    ii = list(d["query"]["pages"].values())[0]["imageinfo"][0]
    md = ii["extmetadata"]
    url = ii["thumburl"] if ii["width"] > 2000 else ii["url"]
    for a in range(6):
        try:
            time.sleep(1)
            data = urllib.request.urlopen(urllib.request.Request(url, headers=UA)).read(); break
        except Exception as e:
            print("retry", key, e); time.sleep(5 * (a + 1))
    ext = ".png" if url.lower().endswith(".png") else ".jpg"
    open(f"{out}/{key}{ext}", "wb").write(data)
    artist = clean(md.get("Artist", {}).get("value"))
    lic = clean(md.get("LicenseShortName", {}).get("value"))
    credits.append(f"{key}: \"{title[5:]}\" by {artist}, {lic}, via Wikimedia Commons — {ii['descriptionurl']}")
    print(key, len(data) // 1024, "KB", artist, lic)
open(f"{out}/CREDITS.txt", "w", encoding="utf-8").write("\n".join(credits) + "\n")
