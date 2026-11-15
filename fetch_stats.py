#!/usr/bin/env python3
"""
Fetch aggregate visitor statistics from GoatCounter and write data/visitor-stats.json.

    GOATCOUNTER_CODE=your-code GOATCOUNTER_TOKEN=your-token python3 fetch_stats.py
    python3 build.py        # embeds the snapshot in index.html

What it needs
  GOATCOUNTER_CODE   your site code (the part before .goatcounter.com)
  GOATCOUNTER_TOKEN  an API key with permission to read statistics
                     (GoatCounter: your username in the top menu, then API).
                     The token is read ONLY from the environment. It is never
                     written to a file, and it must never be put in index.html.

What it writes
  Totals, countries, referring sites, tab and download counts. Aggregates only:
  any country or referrer with fewer than --min visits is merged into "Other",
  so a lone reader can never be picked out of the public file.

Python 3.8+ standard library only.
"""
import argparse, datetime, json, os, pathlib, re, sys, time, urllib.error, urllib.parse, urllib.request

ROOT = pathlib.Path(__file__).parent
OUT = ROOT / "data" / "visitor-stats.json"
CODE_RE = re.compile(r"^[a-z0-9][a-z0-9-]{1,40}$")


def die(msg, code=1):
    print("fetch_stats:", msg, file=sys.stderr)
    sys.exit(code)


def call(base, token, path, params, retries=3):
    url = f"{base}{path}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}", "Accept": "application/json",
                                               "User-Agent": "asean-ai-tracker-stats/1.0"})
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                time.sleep(0.3)                      # the documented limit is 4 requests a second
                return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < retries - 1:
                wait = int(e.headers.get("X-Rate-Limit-Reset", "2") or 2)
                time.sleep(min(max(wait, 1), 30)); continue
            if e.code == 401: die("GoatCounter rejected the token (401). Check GOATCOUNTER_TOKEN.", 2)
            if e.code == 403: die("The token lacks permission (403). Create a key that can read statistics.", 2)
            die(f"GoatCounter returned HTTP {e.code} for {path}.", 2)
        except urllib.error.URLError as e:
            if attempt == retries - 1: die(f"Could not reach GoatCounter: {e.reason}", 2)
            time.sleep(2)
    die(f"No usable answer for {path}.", 2)


def expect(data, key, path):
    if not isinstance(data, dict) or key not in data:
        shape = sorted(data) if isinstance(data, dict) else type(data).__name__
        die(f"Unexpected answer from {path}: wanted a '{key}' field, got {shape}. GoatCounter may have changed its API; "
            "see https://www.goatcounter.com/api", 2)
    return data[key]


def paged(base, token, path, key, start, end, cap_pages=5):
    out, offset = [], 0
    for _ in range(cap_pages):
        d = call(base, token, path, {"start": start, "end": end, "limit": 100, "offset": offset})
        rows = expect(d, key, path)
        out += rows
        if not d.get("more"): break
        offset += 100
    return out


def roll_up(rows, name_key, minimum, other_label):
    keep, other = [], 0
    for r in sorted(rows, key=lambda x: -int(x.get("count", 0))):
        n = int(r.get("count", 0))
        if n >= minimum: keep.append((r, n))
        else: other += n
    return keep, other


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--days", type=int, default=365, help="how far back to count (default 365)")
    ap.add_argument("--min", type=int, default=3, help="merge countries and referrers with fewer visits than this into 'Other' (default 3)")
    ap.add_argument("--api-base", default="", help="override the API address (for testing)")
    ap.add_argument("--skip-if-unconfigured", action="store_true", help="exit quietly if the code or token is missing (for scheduled jobs)")
    a = ap.parse_args()

    code = os.environ.get("GOATCOUNTER_CODE", "").strip().lower()
    token = os.environ.get("GOATCOUNTER_TOKEN", "").strip()
    if not code or not token:
        msg = "set GOATCOUNTER_CODE and GOATCOUNTER_TOKEN (see the README, 'Visitor counts')."
        if a.skip_if_unconfigured: print("fetch_stats: skipped,", msg); return
        die(msg)
    if not a.api_base and not CODE_RE.match(code): die(f"GOATCOUNTER_CODE {code!r} is not a valid site code.")
    base = (a.api_base or f"https://{code}.goatcounter.com/api/v0").rstrip("/")

    now = datetime.datetime.now(datetime.timezone.utc).replace(minute=0, second=0, microsecond=0)
    start = (now - datetime.timedelta(days=a.days)).strftime("%Y-%m-%dT%H:%M:%SZ")
    end = now.strftime("%Y-%m-%dT%H:%M:%SZ")

    total = call(base, token, "/stats/total", {"start": start, "end": end})
    total_all, total_events = int(expect(total, "total", "/stats/total")), int(total.get("total_events", 0))
    locations = paged(base, token, "/stats/locations", "stats", start, end)
    refs = paged(base, token, "/stats/toprefs", "stats", start, end)
    hits = paged(base, token, "/stats/hits", "hits", start, end)

    keep, other = roll_up(locations, "name", a.min, "Other")
    countries = [{"code": str(r.get("id", ""))[:2].upper() if len(str(r.get("id", ""))) == 2 else "", "name": r.get("name", "Unknown"), "count": n} for r, n in keep]
    if other: countries.append({"code": "", "name": f"Other countries (fewer than {a.min} visits each)", "count": other, "other": True})

    rkeep, rother = roll_up(refs, "name", a.min, "Other")
    referrers = [{"name": r.get("name") or "(direct or unknown)", "count": n} for r, n in rkeep]
    if rother: referrers.append({"name": f"Other sites (fewer than {a.min} visits each)", "count": rother, "other": True})

    events = [{"name": h["path"], "count": int(h.get("count", 0))} for h in hits if h.get("event")]
    tabs = [{"name": e["name"][4:], "count": e["count"]} for e in events if e["name"].startswith("tab-")]
    other_events = [e for e in events if not e["name"].startswith("tab-")]

    snap = {"generated": now.strftime("%Y-%m-%dT%H:%M:%SZ"), "source": "GoatCounter", "period": {"start": start[:10], "end": end[:10]},
            "min_group": a.min, "total_visits": max(total_all - total_events, 0), "total_events": total_events,
            "countries": countries, "referrers": referrers, "tabs": tabs, "events": other_events}
    OUT.parent.mkdir(exist_ok=True)
    tmp = OUT.with_suffix(".tmp"); tmp.write_text(json.dumps(snap, ensure_ascii=False, indent=1), encoding="utf-8"); tmp.replace(OUT)
    print(f"Wrote {OUT.relative_to(ROOT)}: {snap['total_visits']} visits, {len(countries)} country rows, {len(referrers)} referrer rows, {len(tabs)} tabs.")
    print("Now run: python3 build.py")


if __name__ == "__main__":
    main()
