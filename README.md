# ASEAN AI Governance Tracker

A living record of **what went wrong, who officially responded and when, and which policies were already in place**, for Singapore, Indonesia, Malaysia, Vietnam, the Philippines, Thailand and ASEAN.

**Status: proof of concept.** Version 0.3 · 40 cases · 62 official responses · 60 policies · every row has a source link. It is a curated sample built to test the method, not a census. It does not claim to hold every incident in the OECD AI Incidents and Hazards Monitor (AIM) for these countries.

## What is in this folder

| File | What it is | Do you edit it? |
|---|---|---|
| `index.html` | The tracker. One file, works offline, no installs. Put it on any website. | No (it is generated) |
| `data/*.csv` | **The data.** Open in Excel or Google Sheets. | **Yes, this is where you work** |
| `build.py` | Checks every row, then rebuilds `index.html`. | No |
| `template.html` | The look and behaviour of the page. | Only to change the design |
| `tracker-data.json` | The same data as JSON, for reuse (for example in the atlas). | No (generated) |
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

The build refuses bad data (impossible dates, missing sources, unknown links, a response dated before its incident, duplicate IDs), so mistakes never reach the page.

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

Covered now: `SG`, `ID`, `MY`, `VN`, `PH`, `TH`, plus `ASEAN` for regional policies. To add another (for example `KH`, `LA`, `MM`, `BN`, `TL`), do three things: add its code to `COUNTRIES` in `build.py`; add its name to `CT`, `ORDER` and `NATIONAL` near the top of the script in `template.html`; then add rows. A suggested rule is to add a country only once it has at least two verified cases.

## Where cases come from

Cases come from public reporting, the OECD AI Incidents and Hazards Monitor (AIM) and the AI Incident Database. AIM collects incidents automatically from news; this tracker keeps the subset where a person can check an official response or a relevant policy. Link the AIM record in `aim_url` when you find one. Sweeping AIM is a manual search, so say in `data/changelog.csv` what you searched each time.

## Speed, and whether a policy came first

The page already calculates both, so nothing needs adding to the CSVs:

- **Speed.** Days from the earliest public record to the first official response, and to the first binding one, plus how long an access restriction lasted. Medians by country are on the Compare tab.
- **Policy before incident.** Each policy is compared with the first incident on the same theme in the same place, and is labelled pre-emptive only if it also names the risk.

Both depend on honest dates. A case whose start is unknown (`onset_certainty` = `unknown`) or dated only to a month or year gets no day count, and most cases added in 0.2 are of that kind, so the speed medians still rest on a small number of cases. Treat them as indicative.

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

Each weekly update is comprehensive: it covers all six countries plus ASEAN, all themes, every watch-list item due for checking, and the backlog queue — and the pull request says explicitly what was checked and what could not be verified.

For a one-off row, paste a source (an article or a ministry page) with this prompt:

> Using only the text I pasted, draft one row each for `incidents.csv` and `responses.csv` following the field list below. Use only facts stated in the text. If a date or detail is missing, leave the cell empty and say so; do not guess. Quote the sentence that supports each date and each actor. Classify the response type and whether it is binding, and explain why. Do not add anything that is not in the text.

Then **you** open the source, confirm each field, and only then add the row. Treat any detail you cannot find on the source page as wrong until proven otherwise.

## Known limits (also on the Method tab)

- A seed, not a census: many incidents and policies are still queued.
- "No official response recorded" means none was found, not that none exists.
- A dash in the policy stack means "none recorded here".
- Day counts depend on the earliest public record found, so a response on "day 0" may simply be the first record.
- Themes and the "pre-emptive" label are researcher judgements and can be challenged.

*Prepared by Suhaimi Zainal Shah with assistance from Muse and Claude AI (Anthropic). Version 0.3, data verified 20 November 2026.*
