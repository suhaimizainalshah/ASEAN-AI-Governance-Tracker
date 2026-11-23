# ASEAN AI Governance Tracker

A living record of **what went wrong, who officially responded and when, and which policies were already in place**, for all eleven ASEAN member states — Brunei, Cambodia, Indonesia, Laos, Malaysia, Myanmar, the Philippines, Singapore, Thailand, Timor-Leste and Vietnam — plus ASEAN regional action.

**Status: proof of concept.** Version 0.4 · 55 cases · 79 official responses · 97 policies · every row has a source link. It is a curated sample built to test the method, not a census. It does not claim to hold every incident in the OECD AI Incidents and Hazards Monitor (AIM) for these countries.

The emblem in the page header is the official ASEAN emblem, revised on 15 November 2026 to eleven stalks of padi — one for each member state — after Timor-Leste became ASEAN's eleventh member on 26 October 2025. This tracker is an independent project by Suhaimi Zainal Shah (AI Benar Advisory). It is not affiliated with, endorsed by, or acting on behalf of ASEAN or the ASEAN Secretariat; the emblem is used only to identify the region covered.

## What is in this folder

| File | What it is | Do you edit it? |
|---|---|---|
| `index.html` | The tracker. One file, works offline, no installs. Put it on any website. | No (it is generated) |
| `data/*.csv` | **The data.** Open in Excel or Google Sheets. | **Yes, this is where you work** |
| `build.py` | Checks every row, then rebuilds `index.html`. | No |
| `template.html` | The look and behaviour of the page. | Only to change the design |
| `tracker-data.json` | The same data as JSON, for reuse (for example in the atlas). | No (generated) |
| `data.json` | The same dataset under its canonical name. | No (generated) |
| `data/*.json` | One JSON file per row type (`incidents`, `responses`, `instruments`, `events`, `changelog`, `backlog`), for reuse without the whole set. | No (generated) |
| `feed.xml`, `feed.json` | Update feeds (RSS 2.0 and JSON Feed 1.1), generated from `data/changelog.csv` at build time. | No (generated) |
| `datapackage.json` | The schema for the CSVs: required fields, allowed values, unique IDs, source URLs. Checked by `frictionless validate` and by the validate-data workflow on every pull request. | Yes, when a field or allowed value changes |
| `.lychee.toml` | Link checker exclusions (hosts that block automated requests, and `PRIVACY.html`, which GitHub Pages renders from `PRIVACY.md`). | Yes, when a host needs excluding |
| `.github/workflows/validate-data.yml` | Checks the CSVs against the schema and runs the build on every pull request. | No |
| `.github/workflows/links.yml` | Checks every link in the built page and the docs on pull requests, and once a week. | No |
| `pagefind/` | Full-text search index, built from the finished page by `build.py` (needs Pagefind, installed automatically with `npx` when available). | No (generated) |
| `fetch_stats.py` | Optional. Fetches aggregate visitor numbers from GoatCounter into `data/visitor-stats.json`. | No |
| `.github/workflows/update-visitor-stats.yml` | Optional. Refreshes those numbers daily on GitHub. | No |

## Open it

Double-click `index.html`. To publish, upload that one file to GitHub Pages, Netlify or your own site.

## Add or change something (about 10 minutes per row)

1. Open the right CSV in `data/` (`incidents`, `responses` or `instruments`).
2. Add a row. Copy an existing row as your model. **Every row needs a source URL.**
3. In a terminal, in this folder, run: `python3 build.py`
4. If a row is wrong, the build stops and tells you which row and why. Fix it and run again.
5. Open `index.html` to check. Add a line to `data/changelog.csv` saying what changed.

The build refuses bad data (impossible dates, missing sources, unknown links, a response dated before its incident, duplicate IDs), so mistakes never reach the page. Two further checks run on every pull request: `frictionless validate datapackage.json` checks the CSVs against the schema (required fields, allowed values, unique IDs, well-formed source URLs), and the link checker follows every link in the freshly built page. You can run both by hand: `frictionless validate datapackage.json` (install with `pip install frictionless`) and, after building, `lychee --config .lychee.toml index.html README.md PRIVACY.md`.

## The rules that keep it trustworthy

**What counts as a response.** Any action by a government body or a person with official authority in that country: a statement or warning, a formal advisory, an investigation or arrest, a block or takedown order, engagement with a platform, lifting a restriction, or a new law. Statements by companies, parties, researchers or news outlets do not count.

**Dates.**
- An incident's `date` is the *earliest public record you can find*. Set `date_precision` to `day`, `month` or `year` honestly.
- `onset_certainty` is `documented` (you know the start), `approximate` (the start is near this date) or `unknown`. If `unknown`, no day count is shown.
- A response with only a month or year gets no day count either. That is correct, not a bug.

**Confidence.**
- `high` = an official or primary source, or several independent sources that agree.
- `medium` = one secondary source, or sources that disagree. Explain the disagreement in `notes`.
- If you only saw a headline or a search listing, say so in `notes` and use `medium`.

**Never add** a row you have not checked against its source. Put unverified ideas in `data/backlog.csv`; they appear on the Updates tab as "queued", asserting nothing.

## Fields you will use most

**incidents.csv**: `id` (`SG-I-06`), `country`, `date`, `date_precision`, `onset_certainty`, `title`, `themes` (separate several with `;`), `event_id` (only if part of a group such as `grok-2026`), `summary`, `source_title`, `source_url`, `confidence`, `verified_on`, and optionally `aim_url` (the case's record in the OECD AI Incidents and Hazards Monitor, in the form `https://oecd.ai/en/incidents/2026-09-17-3946`).

**responses.csv**: `id` (`SG-R-06`), `incident_id` (the case it belongs to), `date`, `date_precision`, `actor`, `type`, `binding` (`yes` = creates legal obligations or restrictions, `no` = statement, advice or request), `legal_basis` (`existing_law`, `new_law`, `none_stated`, `not_applicable`), `instrument_id` (only if the source names the law used), `summary`, `source_url`, `confidence`, `verified_on`.

**instruments.csv** (policies): `id` (`MY-P-06`), `jurisdiction`, `date`, `effective_date` (when it took effect, if different), `title`, `short_title`, `layer`, `binding`, `status` (`in_force`, `adopted`, `draft`, `proposed`, `superseded`), `themes`, `names_risk` (`yes` only if the text explicitly names the risk, for example deepfakes), `next_milestone` and `next_check` (for anything pending, so it lands on the watch list).

Allowed themes: `deepfake-fraud`, `sexual-deepfakes`, `political-deepfakes`, `election-integrity`, `online-safety`, `general-ai`, `data-protection`. Allowed response types: `statement`, `advisory`, `enforcement`, `block_takedown`, `engagement`, `restriction_lifted`, `legislation`.

## Countries covered, and adding one

Covered now: all eleven member states — `SG`, `ID`, `MY`, `VN`, `PH`, `TH`, `KH`, `LA`, `MM`, `BN`, `TL` — plus `ASEAN` for regional policies. The six **SEA-6** countries (`SG`, `ID`, `MY`, `VN`, `PH`, `TH`) have the deepest verified coverage so far; the other five joined the scope on 20 November 2026 and their coverage is still being built. (An earlier rule — add a country only once it has two verified cases — was retired on 20 November 2026: all eleven are in scope from that date, and the gaps are shown rather than hidden.) The page has an **All 11 countries** / **SEA-6 only** switch in the filter rail: SEA-6 is the mature dataset, the 11-country view is the full scope. To add rows for a country, its code goes in `COUNTRIES` in `build.py` and its name in `CT`, `ORDER` and `NATIONAL` in `template.html` — all eleven are already there.

## Where cases come from

Cases come from public reporting, the OECD AI Incidents and Hazards Monitor (AIM) and the AI Incident Database. AIM collects incidents automatically from news; this tracker keeps the subset where a person can check an official response or a relevant policy. Link the AIM record in `aim_url` when you find one. Sweeping AIM is a manual search, so say in `data/changelog.csv` what you searched each time.

## Speed, and whether a policy came first

The page already calculates both, so nothing needs adding to the CSVs:

- **Speed.** Days from the earliest public record to the first official response, and to the first binding one, plus how long an access restriction lasted. Medians by country are on the Compare tab.
- **Policy before incident.** Each policy is compared with the first incident on the same theme in the same place, and is labelled pre-emptive only if it also names the risk.

Both depend on honest dates. A case whose start is unknown (`onset_certainty` = `unknown`) or dated only to a month or year gets no day count, and most cases added in 0.2 are of that kind, so the speed medians still rest on a small number of cases. Treat them as indicative.

## Search, feeds and reuse

**Search.** The search box in the header is powered by [Pagefind](https://pagefind.app/) (MIT), a static full-text index built from the finished page — no server, no third party. It runs entirely in the browser and is self-hosted in `pagefind/`. The page renders its rows with JavaScript, so the built HTML on its own contains no row text; that is why `build.py` also writes a plain list of every row into a hidden `<div id="static-rows">` (readers without JavaScript get the list, shown by a `<noscript>` style rule, and Pagefind can find the rows). Each row in that list carries its own id and title, so a search hit links straight to that row — the list's ids carry an `s-` prefix to avoid clashing with the live cards, and the search box strips it before showing a result. `build.py` rebuilds the index automatically when Pagefind is available (it uses `npx`, which downloads it on first use); if it is not available the build still succeeds and says how to build the index by hand (`npx pagefind --site . --glob index.html`). Commit `pagefind/` with the page, or the search box hides itself.

**Link to a row.** Every case, response and policy has its own link: `#SG-I-01`, `#VN-R-10`, `#ASEAN-P-01`. Use the ⧉ Link button on a row to copy it, or quote the row ID when citing. Opening such a link opens the right tab and scrolls to the row.

**Feeds.** `feed.xml` (RSS 2.0) and `feed.json` (JSON Feed 1.1) are generated from `data/changelog.csv` at build time, one item per changelog entry, and are listed in the page header so feed readers can discover them. Nothing is maintained by hand.

**Reuse the data.** `data.json` (the whole public dataset) and `data/*.json` (one file per row type) are generated at build time alongside the CSV downloads on the page. All data is CC BY 4.0; cite the tracker and the version.

## Publishing

**What is live and what is not.** A GitHub repository on its own only shows the files. To get a live page from the same repository, switch on GitHub Pages (below). An itch.io upload is live as soon as you publish it.

**GitHub Pages (recommended as the main address).**
1. Create a **public** repository (Pages on private repositories needs a paid plan) and upload the contents of this folder, with `index.html` at the top level.
2. In the repository: Settings, Pages, Deploy from a branch, branch `main`, folder `/ (root)`. The address will be `https://YOUR-NAME.github.io/REPOSITORY/` within a few minutes.
3. Save that address to the Internet Archive (web.archive.org/save). A plain page like this archives well.

**itch.io (as a showcase).** Use `asean-ai-tracker-v0.2-itch.zip`, which has `index.html` at the top of the zip. On the project page set Kind of project to HTML, tick "This file will be played in the browser", and choose a viewport of at least 1280 by 900 or the fullscreen option. Say in the description that it is a proof of concept and link to the GitHub page for the data. itch.io shows the page inside a frame and archives poorly, so use the GitHub address when citing.

**Before going public.** The licences are chosen: CC BY 4.0 for the data (`DATA-LICENSE.md`) and MIT for the code (`LICENSE`). Corrections go to suhaimizainalshah@gmail.com (set as `CORRECTIONS_URL` in `build.py`, so the link appears on the page). The privacy page is `PRIVACY.md`. Check that nothing implies endorsement by LSE or LSE IDEAS.

## Visitor counts and the Visitors tab (optional, no cookies)

Off by default in the generic version: nothing is added to the page, and the Visitors tab stays hidden, until a counter code is set. **In your copy the code `suhaimizs` is already set in `build.py`, so counting is on.** To turn it off, run `python3 build.py --goatcounter off`. Do not also paste GoatCounter's own script snippet into the page: this page loads it for you, with the privacy checks built in, and a second copy would count every visit twice. Turn it on if you want to know who reads the tracker, in numbers and places, without a login or a separate dashboard.

| What the tab shows | How fresh | What it needs |
|---|---|---|
| Visits to this copy of the page | Live, up to 30 minutes behind | A GoatCounter site with "Allow adding visitor counts" ticked |
| Region view (ASEAN, rest of Asia, Europe and so on), country table, referring sites, tabs opened, CSV downloads | A snapshot, refreshed by you or daily on GitHub | A read-only API key, kept secret |

It never shows individuals. Countries and sites with fewer than 3 visits are merged into "Other", and the tables appear only once there are 30 visits.

**Set it up (about 20 minutes)**
1. Go to goatcounter.com, sign up (free for non-commercial use), choose a site code such as `asean-ai-tracker`, and confirm your email.
2. In GoatCounter, open the site settings. Tick "Allow adding visitor counts on your website", and check that location and referrer are being collected.
3. Put the code into the page. Run `python3 build.py --goatcounter asean-ai-tracker`, then upload the new `index.html`. With no Python: open `index.html` in a text editor, search for `"goatcounter": ""`, and type your code between the second pair of quotes.
4. Open the live page, then your GoatCounter dashboard. Your first visit should appear within a minute. Your own visits count too; add your IP address under Ignore IPs if you want to exclude them.
5. For the country table, create an API key (your username in the top menu, then API) that can read statistics. Then run:
   ```
   export GOATCOUNTER_CODE=asean-ai-tracker
   export GOATCOUNTER_TOKEN=your-key
   python3 fetch_stats.py
   python3 build.py
   ```
   Upload the new `index.html`. **Keep the key secret.** The script reads it only from the environment; never paste it into a file or into `index.html`.

**Daily refresh on GitHub (optional).** In the repository go to Settings, Secrets and variables, Actions. Add a *variable* `GOATCOUNTER_CODE` and a *secret* `GOATCOUNTER_TOKEN`. The included workflow runs every day, fetches the numbers, rebuilds and commits, and GitHub Pages republishes. GitHub pauses scheduled workflows in public repositories after 60 days without activity; switch it back on from the Actions tab. If you also edit the CSVs on your own computer, pull before you push.

**On itch.io.** The page runs inside a frame, which the counting script normally ignores; this build allows it, so itch.io visits are counted under their own address. To keep the itch.io copy's tables fresh, build it with `--stats-url https://YOUR-NAME.github.io/REPOSITORY/data/visitor-stats.json`. The itch.io copy then reads the latest snapshot from your GitHub Pages site.

**Honest limits.** Counts are visits, not people. Ad blockers and privacy browsers hide a share of visits, so treat the numbers as a floor. Locations come from the visitor's address at the moment of the visit and are shown only by country. The live figure counts one copy of the page; the snapshot counts all copies. Nothing is counted if the browser sends Do Not Track or Global Privacy Control, or if the page is opened from a local file.

**Preview the layout first.** `python3 build.py --demo-stats` makes a page with invented numbers, clearly labelled as sample data. It is for looking only; never publish it, and rebuild normally afterwards.

## Weekly routine (about 90 minutes, every Wednesday midday)

1. **Watch list.** On the Updates tab, open every item marked "Check due". Update its status, `next_milestone` and `next_check`.
2. **Scan** for new incidents and official actions (news alerts, the OECD AI Incidents Monitor, ministry press pages).
3. **Verify** each candidate against a primary source, add the rows, and run `python3 build.py`.
4. **Work the queue.** Take two or three items from `data/backlog.csv`, verify them, and move them into the data.
5. **Log it** in `data/changelog.csv`, then propose the changes as a pull request for review (see below). Nothing goes live until the pull request is reviewed and merged.

## Using an AI assistant (Muse) — human in the loop

Weekly updates are drafted by **Muse**, an AI assistant, and reviewed by a human before anything goes live. Muse works on a branch and opens a pull request; it never pushes to `main` or publishes by itself. The human reviews the pull request, checks anything that looks unsure, and merges it — or asks for changes first.

Anything Muse cannot verify against a source stays in `data/backlog.csv` as a draft: it appears on the Updates tab as "queued", asserting nothing, until a human checks it.

Each weekly update is comprehensive: it covers all eleven member states plus ASEAN regional action, all themes, every watch-list item due for checking, and the backlog queue — and the pull request says explicitly what was checked and what could not be verified.

For a one-off row, paste a source (an article or a ministry page) with this prompt:

> Using only the text I pasted, draft one row each for `incidents.csv` and `responses.csv` following the field list below. Use only facts stated in the text. If a date or detail is missing, leave the cell empty and say so; do not guess. Quote the sentence that supports each date and each actor. Classify the response type and whether it is binding, and explain why. Do not add anything that is not in the text.

Then **you** open the source, confirm each field, and only then add the row. Treat any detail you cannot find on the source page as wrong until proven otherwise.

## Checking a weekly update (the Review tab)

There is no admin backend: the tracker is a static page, and checking happens on the pull request before anything is merged. Open the **Review tab** on the page — or add `#review` to the page address — for the checklist: every row added or changed in the latest update, with its source link, confidence and check date. For each row, open the source and confirm the date is the earliest public record, the actor is a government body or official, and the summary says only what the source says, then tick the row (ticks are saved in your browser only). The pull request also carries a review file quoting the exact source sentence behind each date and actor. When every new row is ticked, merge the pull request; anything that cannot be confirmed stays in `data/backlog.csv` instead.

## Privacy and security

**Privacy.** The page sets no cookies and does no fingerprinting. The full
notice is [`PRIVACY.md`](PRIVACY.md) (rendered on the live site as
`PRIVACY.html`, linked from the footer on every tab). Visitor counting is
GoatCounter only, no cookies, aggregates only, and respects Do Not Track and
Global Privacy Control. The only third parties a browser contacts to load or
use the page are the host, GitHub Pages, and GoatCounter (`gc.zgo.at` for the
counting script, `suhaimizs.goatcounter.com` for the counts). No other
third-party script, font, tracker or advertisement is loaded. Followed items,
theme choice, Review-tab ticks and last-visit date are kept in the reader's
own browser (local storage) and never sent anywhere.

**Security headers.** The site is hosted on GitHub Pages, which does not let
a site set its own HTTP response headers — so `X-Content-Type-Options`,
`X-Frame-Options` and the CSP `frame-ancestors` rule, which can only be set
as headers, are not set here, and no claim is made that they are.
Permissions-Policy has no `<meta>` equivalent at all (browsers ignore a
Permissions-Policy `<meta>` tag), so it cannot be set either while the site
is hosted on GitHub Pages. What can be done in the page itself is done:
`template.html` sets Content-Security-Policy and Referrer-Policy
(`strict-origin-when-cross-origin`) through `<meta>` tags. The policy allows
only the page's own inline scripts and styles plus GoatCounter (`gc.zgo.at`
for the script, `*.goatcounter.com` for counts, including its image-pixel
fallback); there are no other external resources to allow. The CSP needs
`'unsafe-inline'` because all page JavaScript and CSS is inline, so it is a
partial mitigation. It also allows `'wasm-unsafe-eval'` in `script-src`,
because the Pagefind search index runs on WebAssembly: that keyword permits
compiling WebAssembly and nothing else, so JavaScript `eval` stays blocked.
If `STATS_URL` in `build.py` is ever set to another host,
add that host to `connect-src` in `template.html` first, or the snapshot
fetch will be blocked.

## Known limits (also on the Method tab)

- A seed, not a census: many incidents and policies are still queued.
- "No official response recorded" means none was found, not that none exists.
- A dash in the policy stack means "none recorded here".
- Day counts depend on the earliest public record found, so a response on "day 0" may simply be the first record.
- Themes and the "pre-emptive" label are researcher judgements and can be challenged.

*Prepared by Suhaimi Zainal Shah with assistance from Muse and Claude AI (Anthropic). Version 0.4, data verified 23 November 2026.*
*Built and maintained by Suhaimi Zainal Shah · [AI Benar Advisory](https://suhaimizainalshah.github.io/AI-Benar-Advisory/) — independent AI compliance and governance.*
