#!/usr/bin/env python3
"""
Build the ASEAN AI Governance Tracker.

    python3 build.py

Reads data/*.csv, checks every row, and writes:
  index.html          the self-contained tracker (open it in any browser)
  tracker-data.json   the same data as JSON (for reuse or the atlas)

The build STOPS if a row is invalid, so mistakes never reach the page.
Python 3.8+ standard library only.
"""
import csv, json, os, re, sys, datetime, pathlib

ROOT = pathlib.Path(__file__).parent
DATA = ROOT / "data"

# ---- settings you may edit -------------------------------------------------
VERSION = "0.3"
CREDIT = "Prepared by Suhaimi Zainal Shah with assistance from Claude AI (Anthropic)."
CORRECTIONS_URL = "mailto:suhaimizainalshah@gmail.com"     # readers can report errors by email; or use a GitHub issues link
# Optional visitor counting with GoatCounter (no cookies). Empty means OFF: no tracking code is added.
# You can also set it without editing this file:  python3 build.py --goatcounter your-code   (or "off")
GOATCOUNTER_CODE = "suhaimizs"   # your GoatCounter site code (the part before .goatcounter.com). It is public: it is visible in the page source.
STATS_URL = ""           # optional: an https address of the latest visitor-stats.json, so a copy elsewhere (for example itch.io) stays fresh
STATS_MIN_VISITS = 30    # the country table appears only once there are at least this many visits
# ---------------------------------------------------------------------------

def _arg(name):
    if name in sys.argv:
        i = sys.argv.index(name)
        if i + 1 >= len(sys.argv): sys.exit(f"{name} needs a value")
        return sys.argv[i + 1]
    return None

_gc = _arg("--goatcounter")
GOATCOUNTER_CODE = (_gc if _gc is not None else (os.environ.get("GOATCOUNTER_CODE") or GOATCOUNTER_CODE)).strip().lower()   # an empty variable falls back to the setting above
if GOATCOUNTER_CODE in {"off", "none"}: GOATCOUNTER_CODE = ""
STATS_URL = (_arg("--stats-url") or os.environ.get("STATS_URL") or STATS_URL).strip()
if GOATCOUNTER_CODE and not re.match(r"^[a-z0-9][a-z0-9-]{1,40}$", GOATCOUNTER_CODE):
    sys.exit(f"GOATCOUNTER_CODE {GOATCOUNTER_CODE!r} is not valid: use lower-case letters, digits and hyphens (the part before .goatcounter.com).")
if STATS_URL and not re.match(r"^https://\S+$", STATS_URL): sys.exit("STATS_URL must be an https:// address.")

COUNTRIES = {"ASEAN", "SG", "ID", "MY", "VN", "PH", "TH"}
THEMES = {"deepfake-fraud", "sexual-deepfakes", "political-deepfakes", "election-integrity",
          "online-safety", "general-ai", "data-protection"}
RTYPES = {"statement", "advisory", "enforcement", "block_takedown", "engagement", "restriction_lifted", "legislation"}
STATUS = {"in_force", "adopted", "draft", "proposed", "superseded"}
LEGAL = {"existing_law", "new_law", "none_stated", "not_applicable"}
PREC = {"day", "month", "year"}
CONF = {"high", "medium", "low"}
CERT = {"documented", "approximate", "unknown"}
DATE_RE = {"day": r"^\d{4}-\d{2}-\d{2}$", "month": r"^\d{4}-\d{2}$", "year": r"^\d{4}$"}

errors, warnings = [], []

def demo_stats():
    """Invented numbers, for previewing the layout only. Never publish a build made with this."""
    c = [("SG","Singapore",96),("MY","Malaysia",58),("PH","Philippines",41),("ID","Indonesia",37),("GB","United Kingdom",33),("US","United States",31),
         ("TH","Thailand",22),("VN","Vietnam",19),("IN","India",12),("AU","Australia",9),("JP","Japan",6),("DE","Germany",5),("FR","France",4),("HK","Hong Kong",4),("KR","South Korea",3)]
    rows = [dict(code=a, name=n, count=k) for a, n, k in c] + [dict(code="", name="Other countries (fewer than 3 visits each)", count=21, other=True)]
    return dict(generated=datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), source="SAMPLE", sample=True,
        period=dict(start="2026-08-15", end="2026-11-15"), min_group=3, total_visits=401, total_events=120, countries=rows,
        referrers=[dict(name="techforgoodinstitute.org", count=88), dict(name="LinkedIn", count=61), dict(name="Google", count=24), dict(name="(direct or unknown)", count=17), dict(name="Other sites (fewer than 3 visits each)", count=9, other=True)],
        tabs=[dict(name="cases", count=312), dict(name="policies", count=96), dict(name="compare", count=61), dict(name="method", count=44), dict(name="updates", count=23)],
        events=[dict(name="csv-download-cases", count=14), dict(name="csv-download-policies", count=6), dict(name="copy-link", count=9)])

def load_stats():
    if "--demo-stats" in sys.argv: return demo_stats()
    p = DATA / "visitor-stats.json"
    if not p.exists(): return None
    try: s = json.loads(p.read_text(encoding="utf-8"))
    except ValueError as e: sys.exit(f"data/visitor-stats.json is not valid JSON: {e}")
    bad = []
    if not isinstance(s, dict) or not isinstance(s.get("generated"), str): bad.append("missing 'generated'")
    elif not isinstance(s.get("total_visits"), int) or s["total_visits"] < 0: bad.append("'total_visits' must be a whole number")
    elif not isinstance(s.get("countries"), list): bad.append("'countries' must be a list")
    else:
        floor = s.get("min_group", 3)
        for r in s["countries"] + s.get("referrers", []):
            if not isinstance(r, dict) or not isinstance(r.get("count"), int) or not r.get("name"): bad.append(f"bad row {r!r}"); break
            if not r.get("other") and r["count"] < floor: bad.append(f"{r['name']!r} has only {r['count']} visits, below the privacy floor of {floor}; rerun fetch_stats.py"); break
    if bad: sys.exit("data/visitor-stats.json is not usable: " + "; ".join(bad))
    return s

def err(t, i, m): errors.append(f"{t} {i}: {m}")
def warn(t, i, m): warnings.append(f"{t} {i}: {m}")

def read(name):
    p = DATA / f"{name}.csv"
    with open(p, newline="", encoding="utf-8-sig") as f:
        rows = [{k: (v or "").strip() for k, v in r.items()} for r in csv.DictReader(f)]
    return rows

def valid_date(s, prec):
    if prec not in PREC or not re.match(DATE_RE[prec], s or ""): return False
    try:
        y, m, d = (list(map(int, s.split("-"))) + [1, 1])[:3]
        datetime.date(y, m, d); return True
    except ValueError: return False

def check_url(t, i, field, u, required):
    if not u:
        if required: err(t, i, f"{field} is required (every row needs a source)")
        return
    if not re.match(r"^https?://\S+$", u): err(t, i, f"{field} is not a valid http(s) URL: {u!r}")

def check_common(t, r, ids):
    i = r.get("id", "?")
    if not i: err(t, "?", "missing id"); return
    if i in ids: err(t, i, "duplicate id")
    ids.add(i)
    if r.get("confidence") not in CONF: err(t, i, f"confidence must be one of {sorted(CONF)}")
    if not valid_date(r.get("verified_on", ""), "day"): err(t, i, "verified_on must be YYYY-MM-DD")
    check_url(t, i, "source_url", r.get("source_url"), True)
    for u in filter(None, (r.get("more_sources") or "").split(";")):
        check_url(t, i, "more_sources", u.strip(), False)
    if not r.get("source_title"): err(t, i, "source_title is required")

incidents, responses, instruments = read("incidents"), read("responses"), read("instruments")
events, changelog, backlog = read("events"), read("changelog"), read("backlog")

iid, rid, pid = set(), set(), set()
for r in incidents:
    check_common("incident", r, iid); i = r["id"]
    if r["country"] not in COUNTRIES - {"ASEAN"}: err("incident", i, f"country must be one of {sorted(COUNTRIES - {'ASEAN'})}")
    if not i.startswith(r["country"] + "-I-"): warn("incident", i, "id prefix should match country, e.g. SG-I-01")
    if not valid_date(r["date"], r["date_precision"]): err("incident", i, f"date {r['date']!r} does not match precision {r['date_precision']!r}")
    if r["onset_certainty"] not in CERT: err("incident", i, f"onset_certainty must be one of {sorted(CERT)}")
    th = [t for t in r["themes"].split(";") if t]
    if not th or any(t not in THEMES for t in th): err("incident", i, f"themes must come from {sorted(THEMES)}")
    if not r["title"] or not r["summary"]: err("incident", i, "title and summary are required")
    if r.get("aim_url") and not re.match(r"^https://oecd\.ai/en/incidents/\S+$", r["aim_url"]): err("incident", i, "aim_url must be an https://oecd.ai/en/incidents/... link or empty")

evids = {e["id"] for e in events}
for r in incidents:
    if r["event_id"] and r["event_id"] not in evids: err("incident", r["id"], f"unknown event_id {r['event_id']}")

inc_by_id = {r["id"]: r for r in incidents}
for r in responses:
    check_common("response", r, rid); i = r["id"]
    inc = inc_by_id.get(r["incident_id"])
    if not inc: err("response", i, f"unknown incident_id {r['incident_id']!r}"); continue
    if not valid_date(r["date"], r["date_precision"]): err("response", i, f"date {r['date']!r} does not match precision {r['date_precision']!r}")
    if r["type"] not in RTYPES: err("response", i, f"type must be one of {sorted(RTYPES)}")
    if r["binding"] not in {"yes", "no"}: err("response", i, "binding must be yes or no")
    if r["legal_basis"] not in LEGAL: err("response", i, f"legal_basis must be one of {sorted(LEGAL)}")
    if not r["actor"] or not r["summary"]: err("response", i, "actor and summary are required")
    if r["instrument_id"] and r["instrument_id"] not in {p["id"] for p in instruments}: err("response", i, f"unknown instrument_id {r['instrument_id']}")
    # response should not precede its incident (compare at the coarser precision)
    pr = min(["day", "month", "year"].index(r["date_precision"]), 2)
    pi = min(["day", "month", "year"].index(inc["date_precision"]), 2)
    cut = {0: 10, 1: 7, 2: 4}[max(pr, pi)]
    if valid_date(r["date"], r["date_precision"]) and valid_date(inc["date"], inc["date_precision"]):
        if r["date"][:cut] < inc["date"][:cut]: err("response", i, f"date {r['date']} is before its incident ({inc['date']})")

for r in incidents:
    if not any(x["incident_id"] == r["id"] for x in responses):
        warn("incident", r["id"], "has no recorded official response (that is allowed, but check it is true)")

for r in instruments:
    check_common("policy", r, pid); i = r["id"]
    if r["jurisdiction"] not in COUNTRIES: err("policy", i, f"jurisdiction must be one of {sorted(COUNTRIES)}")
    if not valid_date(r["date"], r["date_precision"]): err("policy", i, f"date {r['date']!r} does not match precision {r['date_precision']!r}")
    if r["effective_date"] and not valid_date(r["effective_date"], "day"): err("policy", i, "effective_date must be YYYY-MM-DD or empty")
    if r["status"] not in STATUS: err("policy", i, f"status must be one of {sorted(STATUS)}")
    if r["binding"] not in {"yes", "no"}: err("policy", i, "binding must be yes or no")
    if r["names_risk"] not in {"yes", "no"}: err("policy", i, "names_risk must be yes or no")
    th = [t for t in r["themes"].split(";") if t]
    if not th or any(t not in THEMES for t in th): err("policy", i, f"themes must come from {sorted(THEMES)}")
    if r["next_check"] and not valid_date(r["next_check"], "day"): err("policy", i, "next_check must be YYYY-MM-DD or empty")
    if r["status"] in {"draft", "proposed", "adopted"} and not r["next_check"]: warn("policy", i, "pending item has no next_check date; add one so it appears on the watch list")
    if not r["title"] or not r["summary"]: err("policy", i, "title and summary are required")

for e in events:
    if not valid_date(e["onset"], e["onset_precision"]): err("event", e["id"], "bad onset date")
for c in changelog:
    if not valid_date(c["date"], "day"): err("changelog", c.get("date", "?"), "date must be YYYY-MM-DD")

print(f"Checked {len(incidents)} cases, {len(responses)} responses, {len(instruments)} policies.")
for w in warnings: print("  note:", w)
if errors:
    print("\nBUILD STOPPED. Fix these rows in data/*.csv:")
    for e in errors: print("  ERROR", e)
    sys.exit(1)

verified = max(r["verified_on"] for r in incidents + responses + instruments)
stats = load_stats()
payload = dict(
    meta=dict(version=VERSION, verified=verified, built=datetime.date.today().isoformat(), credit=CREDIT, corrections_url=CORRECTIONS_URL,
              analytics=dict(goatcounter=GOATCOUNTER_CODE, stats_url=STATS_URL, min_visits=STATS_MIN_VISITS, sample=bool(stats and stats.get("sample")))),
    incidents=incidents, responses=responses, instruments=instruments, events=events,
    changelog=sorted(changelog, key=lambda c: c["date"], reverse=True), backlog=backlog, visitors=stats)

public = json.loads(json.dumps(payload)); public.pop("visitors", None); public["meta"].pop("analytics", None)   # the reusable dataset carries no visitor data
(ROOT / "tracker-data.json").write_text(json.dumps(public, ensure_ascii=False, indent=1), encoding="utf-8")
tpl = (ROOT / "template.html").read_text(encoding="utf-8")
blob = json.dumps(payload, ensure_ascii=False).replace("</", "<\\/")      # keep </script> out of the data
(ROOT / "index.html").write_text(tpl.replace("/*__DATA__*/null", blob), encoding="utf-8")
print(f"Built index.html and tracker-data.json (version {VERSION}, verified {verified}).")
print("Visitor counting:", f"ON ({GOATCOUNTER_CODE}.goatcounter.com)" if GOATCOUNTER_CODE else "OFF (no tracking code in the page)")
print("Visitor snapshot:", ("SAMPLE DATA, for layout preview only, do not publish" if stats.get("sample") else f"embedded, generated {stats['generated']}") if stats else "none")
