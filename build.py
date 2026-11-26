#!/usr/bin/env python3
"""
Build the ASEAN AI Governance Tracker.

    python3 build.py

Reads data/*.csv, checks every row, and writes:
  index.html          the self-contained tracker (open it in any browser)
  tracker-data.json   the same data as JSON (for reuse or the atlas)
  data.json           the same dataset under its canonical name
  data/*.json         one JSON file per row type (incidents, responses, ...)
  feed.xml / feed.json  update feeds generated from data/changelog.csv
  pagefind/           full-text search index, if Pagefind is available
The build STOPS if a row is invalid, so mistakes never reach the page.
Python 3.8+ standard library only.
"""
import csv, json, os, re, sys, datetime, pathlib
from xml.sax.saxutils import escape as xml_escape

ROOT = pathlib.Path(__file__).parent
DATA = ROOT / "data"

# ---- settings you may edit -------------------------------------------------
VERSION = "0.5"
CREDIT = "Prepared by Suhaimi Zainal Shah with assistance from Muse and Claude AI (Anthropic)."
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

COUNTRIES = {"ASEAN", "SG", "ID", "MY", "VN", "PH", "TH", "KH", "LA", "MM", "BN", "TL"}
THEMES = {"deepfake-fraud", "sexual-deepfakes", "political-deepfakes", "election-integrity",
          "online-safety", "general-ai", "data-protection"}
RTYPES = {"statement", "advisory", "enforcement", "block_takedown", "engagement", "restriction_lifted", "legislation"}
RT_LABEL = {"statement": "Statement or warning", "advisory": "Formal advisory or guidance",
            "enforcement": "Investigation or enforcement", "block_takedown": "Block or takedown",
            "engagement": "Engagement with a platform", "restriction_lifted": "Restriction lifted",
            "legislation": "New law, regulation or declaration"}
# Public address of the live tracker; used for the feeds and for feed item links.
SITE_URL = "https://suhaimizainalshah.github.io/ASEAN-AI-Governance-Tracker/"
FEED_TITLE = "ASEAN AI Governance Tracker — Updates"
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

# ---------- Compute: chips, data centres and verification (0.5). Optional files: the tracker builds without them.
COUNTRIES = {"SG", "ID", "MY", "VN", "PH", "TH", "KH", "LA", "MM", "BN", "TL", "ASEAN"}
SITE_STATUS = {"operational", "under_construction", "announced", "approved", "paused", "cancelled"}
MEASURE_KIND = {"foreign_rule", "permit", "export_control", "data_centre_rule", "energy_rule", "government_response", "investigation", "prosecution", "seizure", "guidance"}
LANGS = {"en", "ms", "id", "th", "vi", "tl", "km", "lo", "my", "zh", "ta"}
def read_optional(name):
    return read(name) if (DATA / f"{name}.csv").exists() else []
compute_capacity, compute_sites, compute_measures = read_optional("compute_capacity"), read_optional("compute_sites"), read_optional("compute_measures")
compute_profile = read_optional("compute_profile")
PROFILE_Q = {"public_list", "capacity_official", "chip_permit", "enforcement_public", "technical_unit"}
PROFILE_S = {"yes", "partly", "checked_not_found"}        # a cell that was not checked has no row: the page shows "not checked yet"
_seen = set()
for r in compute_profile:
    i = r.get("id", "?")
    if r.get("country") not in COUNTRIES - {"ASEAN"}: err("profile", i, "country must be an ASEAN member code such as MY")
    if r.get("question") not in PROFILE_Q: err("profile", i, f"question must be one of {sorted(PROFILE_Q)}")
    if r.get("status") not in PROFILE_S: err("profile", i, f"status must be one of {sorted(PROFILE_S)} (leave a cell out if it was not checked)")
    if (r.get("country"), r.get("question")) in _seen: err("profile", i, "this country and question already have a row")
    _seen.add((r.get("country"), r.get("question")))
    if not r.get("detail"): err("profile", i, "detail is required: say what was found, or where you looked")
    if not valid_date(r.get("checked_on", ""), "day"): err("profile", i, "checked_on must be YYYY-MM-DD")
    if r.get("confidence") not in CONF: err("profile", i, f"confidence must be one of {sorted(CONF)}")
    check_url("profile", i, "source_url", r.get("source_url", ""), r.get("status") != "checked_not_found")
def num(t, i, field, v):
    if v and not re.match(r"^\d+(\.\d+)?$", v): err(t, i, f"{field} must be a number of megawatts or empty")
for r in compute_capacity:
    i = r.get("id", "?")
    if r.get("country") not in COUNTRIES: err("capacity", i, "country must be an ASEAN code such as MY")
    if not valid_date(r.get("as_of", ""), "month") and not valid_date(r.get("as_of", ""), "day"): err("capacity", i, "as_of must be YYYY-MM or YYYY-MM-DD")
    for f in ("operational_mw", "under_construction_mw", "planned_mw", "facilities"): num("capacity", i, f, r.get(f, ""))
    if not r.get("measure"): err("capacity", i, "say what the figures measure (measure); firms define capacity differently")
    if not r.get("firm"): err("capacity", i, "say which firm the figures come from (firm): ratios only compare one firm's figures")
    check_url("capacity", i, "source_url", r.get("source_url", ""), True)
for r in compute_sites:
    i = r.get("id", "?")
    if r.get("country") not in COUNTRIES: err("site", i, "country must be an ASEAN code such as MY")
    if r.get("status") not in SITE_STATUS: err("site", i, f"status must be one of {sorted(SITE_STATUS)}")
    num("site", i, "capacity_mw", r.get("capacity_mw", ""))
    if r.get("confidence") not in CONF: err("site", i, f"confidence must be one of {sorted(CONF)}")
    if r.get("source_language", "en") not in LANGS: err("site", i, f"source_language must be one of {sorted(LANGS)}")
    check_url("site", i, "source_url", r.get("source_url", ""), True)
for r in compute_measures:
    i = r.get("id", "?")
    if r.get("jurisdiction") not in COUNTRIES | {"US", "CN", "EU", "INTL"}: err("measure", i, "jurisdiction must be an ASEAN code, or US, CN, EU or INTL")
    if r.get("date_precision") not in PREC or not valid_date(r.get("date", ""), r.get("date_precision", "")): err("measure", i, "date must match its date_precision")
    if r.get("kind") not in MEASURE_KIND: err("measure", i, f"kind must be one of {sorted(MEASURE_KIND)}")
    if r.get("binding") not in {"yes", "no"}: err("measure", i, "binding must be yes or no")
    if r.get("confidence") not in CONF: err("measure", i, f"confidence must be one of {sorted(CONF)}")
    if r.get("kind") in {"investigation", "prosecution"} and not re.search(r"not a finding|until a court|allegation", r.get("summary", ""), re.I):
        err("measure", i, "say in the summary that an investigation or charge is not a finding of wrongdoing")
    if not r.get("title") or not r.get("summary"): err("measure", i, "title and summary are required")
    check_url("measure", i, "source_url", r.get("source_url", ""), True)
print(f"Checked {len(incidents)} cases, {len(responses)} responses, {len(instruments)} policies; compute: {len(compute_capacity)} markets, {len(compute_sites)} sites, {len(compute_measures)} measures, {len(compute_profile)} profile answers.")
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
    changelog=sorted(changelog, key=lambda c: c["date"], reverse=True), backlog=backlog, visitors=stats,
    compute=dict(capacity=compute_capacity, sites=compute_sites, measures=sorted(compute_measures, key=lambda m: m["date"], reverse=True), profile=compute_profile))

public = json.loads(json.dumps(payload)); public.pop("visitors", None); public["meta"].pop("analytics", None)   # the reusable dataset carries no visitor data
(ROOT / "tracker-data.json").write_text(json.dumps(public, ensure_ascii=False, indent=1), encoding="utf-8")

# ---- reusable JSON exports ---------------------------------------------------
# data.json is the same public dataset as tracker-data.json (kept under both
# names: tracker-data.json for existing links, data.json as the canonical
# name). One JSON file per row type lives next to the CSVs in data/, so
# researchers and other tools can fetch a single table without the whole set.
(ROOT / "data.json").write_text(json.dumps(public, ensure_ascii=False, indent=1), encoding="utf-8")
for _name, _rows in [("incidents", incidents), ("responses", responses), ("instruments", instruments),
                     ("events", events), ("changelog", changelog), ("backlog", backlog)]:
    (DATA / f"{_name}.json").write_text(json.dumps(_rows, ensure_ascii=False, indent=1), encoding="utf-8")

# ---- feeds -------------------------------------------------------------------
# feed.xml (RSS 2.0) and feed.json (JSON Feed 1.1) are generated from the
# changelog at build time, so followers are notified of each weekly update.
# Both are listed in template.html with autodiscovery <link> tags.
def _rfc2822(d):
    dt = datetime.datetime.strptime(d, "%Y-%m-%d").replace(tzinfo=datetime.timezone.utc)
    return dt.strftime("%a, %d %b %Y %H:%M:%S +0000")

def write_feeds():
    items = sorted(changelog, key=lambda c: c["date"], reverse=True)
    last = items[0]["date"] if items else datetime.date.today().isoformat()
    rss = ['<?xml version="1.0" encoding="UTF-8"?>',
           '<rss version="2.0"><channel>',
           f"<title>{xml_escape(FEED_TITLE)}</title>",
           f"<link>{xml_escape(SITE_URL)}</link>",
           f"<description>{xml_escape('What changed in the ASEAN AI Governance Tracker: new cases, official responses and policies, and what is still queued for verification.')}</description>",
           "<language>en</language>",
           f"<lastBuildDate>{_rfc2822(last)}</lastBuildDate>"]
    for n, c in enumerate(items):
        rss.append("<item>"
                   f"<title>{xml_escape('Tracker update — ' + c['date'])}</title>"
                   f"<link>{xml_escape(SITE_URL + '#updates')}</link>"
                   f"<guid isPermaLink=\"false\">{xml_escape(SITE_URL + '#updates-' + c['date'] + '-' + str(n))}</guid>"
                   f"<pubDate>{_rfc2822(c['date'])}</pubDate>"
                   f"<description>{xml_escape(c['change'])}</description>"
                   "</item>")
    rss.append("</channel></rss>")
    (ROOT / "feed.xml").write_text("\n".join(rss) + "\n", encoding="utf-8")
    feed = {"version": "https://jsonfeed.org/version/1.1",
            "title": FEED_TITLE, "home_page_url": SITE_URL, "feed_url": SITE_URL + "feed.json",
            "items": [{"id": SITE_URL + "#updates-" + c["date"] + "-" + str(n),
                       "url": SITE_URL + "#updates",
                       "title": "Tracker update — " + c["date"],
                       "content_text": c["change"],
                       "date_published": c["date"] + "T00:00:00Z"} for n, c in enumerate(items)]}
    (ROOT / "feed.json").write_text(json.dumps(feed, ensure_ascii=False, indent=1), encoding="utf-8")

write_feeds()

# ---- plain static list, for readers without JavaScript and for search -------
# The page renders its rows with JavaScript, so the built HTML on its own
# contains no row text. build.py therefore also writes a plain list of every
# row (template placeholder <!--__STATIC_ROWS__-->): readers without
# JavaScript get a usable list, and the Pagefind search index (built after
# this step) can find the rows. The list is hidden while JavaScript runs
# (the <noscript> style below shows it again when scripting is off).
# Each row carries its own id and data-pagefind-title, so a search hit links
# straight to that row. The ids here are prefixed with "s-" because the
# JavaScript viewer puts the same row IDs on the live cards, and an id must
# not appear twice in one page; the search box rewrites the "s-" prefix
# away (see initSearch in template.html), so a hit links to #SG-I-01, the
# same link the ⧉ Link button on the row copies.
def static_rows():
    import html as _html
    def esc(s): return _html.escape(s or "", quote=True)
    parts = ['<div id="static-rows" hidden>',
             '<h2>All rows (plain list)</h2>',
             '<p class="small muted">This plain list is shown when JavaScript is off. With JavaScript on, use the Cases and Policies tabs above; every row there also has its own link, for example #SG-I-01.</p>']
    for i in incidents:
        parts.append(f'<article id="s-{esc(i["id"])}" data-pagefind-title="{esc(i["title"])}">'
                     f'<h3>{esc(i["title"])}</h3>'
                     f'<p>{esc(i["summary"])}</p>'
                     f'<p class="src">Case {esc(i["id"])} · {esc(i["country"])} · {esc(i["date"])} · '
                     f'<a href="{esc(i["source_url"])}">{esc(i["source_title"])}</a></p></article>')
    for r in responses:
        title = f"{r['actor']} — {RT_LABEL.get(r['type'], r['type'])} on {r['incident_id']}"
        parts.append(f'<article id="s-{esc(r["id"])}" data-pagefind-title="{esc(title)}">'
                     f'<h3>{esc(title)}</h3>'
                     f'<p>{esc(r["summary"])}</p>'
                     f'<p class="src">Response {esc(r["id"])} · {esc(r["date"])} · '
                     f'<a href="{esc(r["source_url"])}">{esc(r["source_title"])}</a></p></article>')
    for p in instruments:
        parts.append(f'<article id="s-{esc(p["id"])}" data-pagefind-title="{esc(p["title"])}">'
                     f'<h3>{esc(p["title"])}</h3>'
                     f'<p>{esc(p["summary"])}</p>'
                     f'<p class="src">Policy {esc(p["id"])} · {esc(p["jurisdiction"])} · {esc(p["date"])} · '
                     f'<a href="{esc(p["source_url"])}">{esc(p["source_title"])}</a></p></article>')
    parts.append('</div>')
    parts.append('<noscript><style>#static-rows{display:block}</style></noscript>')
    return "\n".join(parts)

tpl = (ROOT / "template.html").read_text(encoding="utf-8")
if "<!--__STATIC_ROWS__-->" not in tpl:
    sys.exit("template.html is missing the <!--__STATIC_ROWS__--> placeholder")
tpl = tpl.replace("<!--__STATIC_ROWS__-->", static_rows())
PREVIEW = "--preview" in sys.argv or os.environ.get("PREVIEW") == "1"     # pull-request preview: shows the Review tab and a banner
page = {**payload, "meta": {**payload["meta"], "preview": True}} if PREVIEW else payload
blob = json.dumps(page, ensure_ascii=False).replace("</", "<\\/")      # keep </script> out of the data
if PREVIEW:
    print("PREVIEW build: the Review tab and a preview banner are shown. Do not commit this index.html.")
(ROOT / "index.html").write_text(tpl.replace("/*__DATA__*/null", blob), encoding="utf-8")
print(f"Built index.html and tracker-data.json (version {VERSION}, verified {verified}).")
print(f"Also wrote data.json, data/*.json (one per row type), feed.xml and feed.json ({len(changelog)} changelog entries).")
print("Visitor counting:", f"ON ({GOATCOUNTER_CODE}.goatcounter.com)" if GOATCOUNTER_CODE else "OFF (no tracking code in the page)")
print("Visitor snapshot:", ("SAMPLE DATA, for layout preview only, do not publish" if stats.get("sample") else f"embedded, generated {stats['generated']}") if stats else "none")

# ---- search index (Pagefind) -------------------------------------------------
# The search box on the page is powered by Pagefind, a static search index
# built from the finished index.html (it reads the plain list above, because
# the tabs themselves are rendered by JavaScript). Runs only if Pagefind is
# available; otherwise the build still succeeds and says how to build the
# index by hand. The index lives in pagefind/ and is committed with the page.
def run_pagefind():
    import shutil, subprocess
    if shutil.which("pagefind"):
        cmd = ["pagefind", "--site", ".", "--glob", "index.html"]
    elif shutil.which("npx"):
        cmd = ["npx", "-y", "pagefind", "--site", ".", "--glob", "index.html"]
    else:
        print("Pagefind not found (no `pagefind` or `npx` on PATH): search index not rebuilt. Install it, or run: npx pagefind --site . --glob index.html")
        return False
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print("Pagefind failed; search index not rebuilt:")
        print((r.stdout or "") + (r.stderr or ""))
        return False
    print("Pagefind index rebuilt in pagefind/.")
    return True

run_pagefind()
