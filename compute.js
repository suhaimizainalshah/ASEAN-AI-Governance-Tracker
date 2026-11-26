/* ASEAN AI Governance and Safety Tracker: the Compute tab. Chips, data centres and verification in Southeast Asia.
   Draws from DATA.compute (data/compute_capacity.csv, compute_sites.csv and compute_measures.csv, checked by build.py).
   Everything shown is published and sourced. Signals are questions to check, never accusations. */
(() => {
  const esc = s => String(s ?? "").replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const CT = { SG: "Singapore", ID: "Indonesia", MY: "Malaysia", VN: "Vietnam", PH: "Philippines", TH: "Thailand", KH: "Cambodia", LA: "Laos", MM: "Myanmar", BN: "Brunei", TL: "Timor-Leste",
               ASEAN: "ASEAN (regional)", US: "United States", CN: "China", EU: "European Union", INTL: "International" };
  const LANG = { en: "English", ms: "Malay", id: "Indonesian", th: "Thai", vi: "Vietnamese", tl: "Filipino", km: "Khmer", lo: "Lao", my: "Burmese", zh: "Chinese", ta: "Tamil" };
  const STATUS = { operational: "Operational", under_construction: "Under construction", announced: "Announced", approved: "Approved", paused: "Paused", cancelled: "Cancelled" };
  const KIND = { foreign_rule: "Rule from outside ASEAN", permit: "Permit or licence", export_control: "Export control", data_centre_rule: "Data centre rule", energy_rule: "Energy rule",
                 government_response: "Government response", investigation: "Investigation", prosecution: "Charge or prosecution", seizure: "Seizure", guidance: "Guidance" };
  const fmt = n => n === "" || n == null ? "" : Number(n).toLocaleString("en-GB");
  const isNation = r => /whole country/i.test(r.market) || r.market === CT[r.country];      // "Singapore" is a city and a country
  const short = r => isNation(r) ? r.market : `${r.market} (${r.country})`;             // charts: "Johor (MY)"
  const full = r => isNation(r) ? r.market : `${r.market}, ${CT[r.country] || r.country}`; // text: "Johor, Malaysia"
  const when = (d, p) => { if (!d) return ""; const [y, m, dd] = d.split("-"); const M = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
    return p === "year" ? y : p === "month" ? `${M[+m - 1]} ${y}` : `${+dd} ${M[+m - 1]} ${y}`; };
  const src = r => `<a href="${esc(r.source_url)}" target="_blank" rel="noopener">${esc(r.source_title)}</a>`;
  const csvCell = v => { const s = String(v ?? ""); const t = /^[=+\-@\t\r]/.test(s) ? "'" + s : s; return /[",\n\r]/.test(t) ? `"${t.replace(/"/g, '""')}"` : t; };
  const download = (name, rows) => { if (!rows.length) return; const keys = Object.keys(rows[0]);
    const blob = new Blob(["\ufeff" + [keys, ...rows.map(r => keys.map(k => r[k]))].map(r => r.map(csvCell).join(",")).join("\r\n")], { type: "text/csv" });
    const a = document.createElement("a"), u = URL.createObjectURL(blob); a.href = u; a.download = name; a.hidden = true; document.body.append(a); a.click(); a.remove(); setTimeout(() => URL.revokeObjectURL(u), 4000); };

  /* ---------- 1. capacity: one bar per market ---------- */
  function capacityChart(rows) {     // bars made of page elements, so they reflow and stay readable on any screen
    const markets = rows.filter(r => !/whole country/i.test(r.market));
    const tot = r => (+r.operational_mw || 0) + (+r.under_construction_mw || 0) + (+r.planned_mw || 0), max = Math.max(1, ...markets.map(tot));
    const parts = [["operational_mw", "Operational", "cp-op"], ["under_construction_mw", "Under construction", "cp-uc"], ["planned_mw", "Planned", "cp-pl"]];
    const desc = markets.map(r => `${full(r)}: ${parts.map(([k, n]) => r[k] ? `${n.toLowerCase()} ${fmt(r[k])} MW` : "").filter(Boolean).join(", ")}`).join("; ");
    const rowsHtml = markets.map(r => { const missing = parts.filter(([k]) => r[k] === "").map(([, n]) => n.toLowerCase());
      return `<div class="cp-row"><div class="cp-rl"><span class="cp-name" title="${esc(full(r))}">${esc(short(r))}</span><span class="cp-num">${fmt(tot(r))} MW${missing.length ? `<small> · ${esc(missing.join(", "))} not published</small>` : ""}</span></div>
        <div class="cp-bar">${parts.map(([k, n, c]) => +r[k] ? `<span class="${c}" style="width:${(+r[k] / max * 100).toFixed(2)}%" title="${esc(full(r))}: ${n} ${fmt(r[k])} MW"></span>` : "").join("")}</div></div>`; }).join("");
    return `<figure class="cp-fig"><div class="cp-legend" aria-hidden="true">${parts.map(([, n, c]) => `<span><i class="${c}"></i>${n}</span>`).join("")}</div>
      <div class="cp-bars" role="img" aria-label="Data centre capacity by market, in megawatts. ${esc(desc)}">${rowsHtml}</div>
      <figcaption>Megawatts (MW) of data centre IT capacity by market, mid-2026. Each bar comes from one published report: see the table for its source and what it measures.
      <strong>Do not add figures from different firms together:</strong> they count capacity differently.</figcaption></figure>`;
  }
  function capacityTable(rows) {
    return `<div class="tablewrap"><table class="cp-t"><caption class="sr">Capacity figures, with what each measures and its source</caption>
      <thead><tr><th scope="col">Market</th><th scope="col">Operational</th><th scope="col">Under construction</th><th scope="col">Planned</th><th scope="col">What it measures</th><th scope="col">Source</th></tr></thead><tbody>
      ${rows.map(r => `<tr><th scope="row">${esc(r.market)}${isNation(r) ? "" : `<br><small>${esc(CT[r.country] || r.country)}</small>`}<br><small class="muted">${esc(when(r.as_of, r.as_of.length > 7 ? "day" : "month"))}</small></th>
        ${["operational_mw", "under_construction_mw", "planned_mw"].map(k => `<td>${r[k] ? fmt(r[k]) + " MW" : '<span class="muted">not published</span>'}</td>`).join("")}
        <td>${esc(r.measure)}${r.notes ? `<details><summary>Note</summary><p>${esc(r.notes)}</p></details>` : ""}</td><td>${src(r)}</td></tr>`).join("")}</tbody></table></div>`;
  }
  /* ---------- 2. named projects ---------- */
  function sitesTable(rows) {
    return `<div class="tablewrap"><table class="cp-t"><caption class="sr">Named data centre projects</caption>
      <thead><tr><th scope="col">Project</th><th scope="col">Where</th><th scope="col">Status</th><th scope="col">Capacity</th><th scope="col">AI-focused</th><th scope="col">Source</th></tr></thead><tbody>
      ${rows.map(r => `<tr><th scope="row">${esc(r.name)}<br><small class="muted">${esc(r.operator)}</small></th><td>${esc(r.place)}, ${esc(CT[r.country] || r.country)}</td>
        <td><span class="cp-st s-${esc(r.status)}">${esc(STATUS[r.status] || r.status)}</span>${r.announced ? `<br><small class="muted">${esc(r.announced)}</small>` : ""}</td>
        <td>${r.capacity_mw ? fmt(r.capacity_mw) + " MW" : '<span class="muted">not published</span>'}${r.capacity_basis ? `<br><small class="muted">${esc(r.capacity_basis)}</small>` : ""}</td>
        <td>${r.ai_focus === "yes" ? "Yes" : r.ai_focus === "no" ? "No" : '<span class="muted">unknown</span>'}</td>
        <td>${src(r)} <span class="cp-conf c-${esc(r.confidence)}" title="How sure we are">${esc(r.confidence)}</span>${r.notes ? `<details><summary>Note</summary><p>${esc(r.notes)}</p></details>` : ""}</td></tr>`).join("")}</tbody></table></div>`;
  }
  /* ---------- 3. chips: rules, responses and cases ---------- */
  function measuresList(rows, filter) {
    const list = rows.filter(r => !filter || r.kind === filter);
    return list.map(r => `<li class="cp-m"><div class="cp-mh"><time>${esc(when(r.date, r.date_precision))}</time><span class="cp-k k-${esc(r.kind)}">${esc(KIND[r.kind] || r.kind)}</span>
        <span class="muted">${esc(CT[r.jurisdiction] || r.jurisdiction)} · ${esc(r.actor)}</span></div>
      <h4>${esc(r.title)}</h4><p>${esc(r.summary)}</p>
      <p class="small">${src(r)}${r.more_sources ? ` · <a href="${esc(r.more_sources)}" target="_blank" rel="noopener">another report</a>` : ""} · <span class="cp-conf c-${esc(r.confidence)}">${esc(r.confidence)} confidence</span> · ${r.binding === "yes" ? "binding" : "not binding"}</p></li>`).join("")
      || '<li class="muted">Nothing of this kind yet.</li>';
  }
  /* ---------- 4. when it isn't in the news ---------- */
  const SIGNALS = [
    ["Trade statistics", "Imports and exports of computers and servers (HS 8471), their parts (8473) and chips (8542), by month and partner country.", "UN Comtrade; national statistics offices", "Broad product codes, months of delay, and no company names. A jump is a question, not evidence."],
    ["Electricity", "Grid connections, utility statements and electricity demand from data centres show capacity actually being switched on.", "Utilities, energy regulators, national energy plans", "Rarely names the tenant, or what the power is used for."],
    ["Approvals and land", "Investment approvals, calls for new capacity, planning permissions and land sales for data centres.", "Investment boards, planning authorities, consultancy market reports", "Shows intention and scale, not what is installed."],
    ["Company filings", "Spending plans, leases, GPU purchases and customers, in listed companies' reports.", "Stock exchange announcements (Bursa, SGX, SET, IDX, HOSE)", "Only listed companies, and only what they must disclose."],
    ["Enforcement records", "Customs statements, court listings and charges, and police or regulator press releases.", "Customs, courts, regulators", "A charge is an allegation until a court decides. Report it as such."],
    ["Export control lists", "Changes to foreign lists of restricted companies that name entities in the region.", "Government lists, such as the US Entity List", "A foreign government's listing, not a local finding."],
    ["Gaps between figures", "Capacity that grows faster than the power or the chips that would need to reach it, or pre-leased capacity with no named tenant.", "The figures on this tab, compared", "Firms define capacity differently: compare like with like."],
  ];
  const QUESTIONS = ["Is there a public register of data centres, and does it name the operator?", "Are numbers of export, transit or transshipment permits for AI chips published?",
    "Do grid connection approvals or energy plans name data centre projects?", "Are customs seizures and court charges for chip smuggling announced, and in which language?",
    "Which agency would answer a question about who uses a data centre, and is there a way to ask it?"];
  /* ---------- 5. verification ---------- */
  const LAYERS = [
    ["Trade and customs", "Which chips cross the border, under which permit, to which declared user.", "Customs and trade ministries", "Importers and exporters", "Already possible: permits such as Malaysia's for US-origin AI chips."],
    ["The data centre site", "Declared capacity, power drawn, cooling, owner and tenants.", "Planning and energy regulators, utilities", "The operator", "Largely possible: power and planning approvals already exist. Knowing the tenants needs a legal duty to say."],
    ["The chips and servers", "How many, where, and whether built-in security features are switched on.", "Chip makers, operators, inspectors", "Chip makers and operators", "Only partly: built-in features depend on chip makers; host states can require inventories and spot checks."],
    ["The network", "How much data flows in and out of a cluster.", "Operators, network providers, inspectors", "The operator, within data protection law", "Intrusive. Network monitoring raises data protection questions, and operators may refuse."],
    ["The workload", "Whether training or inference is running, and how much computing it uses.", "The AI developer, auditors", "The AI developer", "Needs the developer's agreement: verification software, attestation, or confidential computing."],
    ["The model and its tests", "Which model ran, and its safety evaluation results.", "AI developers, AI safety institutes", "The AI developer", "Through testing bodies, such as Singapore's AI Verify and its safety institute."],
  ];
  const READING = [
    ["Verification of frontier AI", "UN Scientific Advisory Board, 2025", "https://www.un.org/scientific-advisory-board/sites/default/files/2025-06/verification_of_frontier_ai.pdf"],
    ["Verification for International AI Governance", "Oxford Martin AI Governance Initiative, 2025", "https://aigi.ox.ac.uk/wp-content/uploads/2025/07/Verification_for_International_AI_Governance.pdf"],
    ["Verifying international agreements on large-scale AI compute", "arXiv:2507.15916, 2025", "https://arxiv.org/html/2507.15916v1"],
    ["A system overview for near-term, low-trust AI compute verification", "Machine Intelligence Research Institute, working paper", "https://intelligence.org/wp-content/uploads/A-system-overview-for-near-term-low-trust-AI-compute-verification.pdf"],
    ["Can power draw constrain covert compute? Limits of analogue verification", "Kimpson, Baker and Graham, arXiv:2610.07476, October 2026", "https://arxiv.org/pdf/2610.07476"],
    ["AI data centers directory", "Epoch AI", "https://epoch.ai/data/ai-data-centers/directory/ytl-johor"],
  ];

  /* ---------- planned versus running: one firm's figures only ---------- */
  function ratioRows(rows) {
    return rows.filter(r => r.firm === "Cushman & Wakefield" && +r.operational_mw > 0 && !/whole country/i.test(r.market))
      .map(r => ({ market: r.market, label: short(r), name: full(r), op: +r.operational_mw, ahead: (+r.under_construction_mw || 0) + (+r.planned_mw || 0), as_of: r.as_of, r }))
      .map(x => ({ ...x, ratio: x.ahead / x.op })).sort((a, b) => b.ratio - a.ratio);
  }
  function ratioChart(rows) {
    const R = ratioRows(rows); if (!R.length) return '<p class="muted">Not enough figures from one firm yet.</p>';
    const max = Math.max(...R.map(x => x.ratio));
    const bars = R.map(d => `<div class="cp-row"><div class="cp-rl"><span class="cp-name" title="${esc(d.name)}">${esc(d.label)}</span><span class="cp-num cp-big">${d.ratio.toFixed(1)} ×</span></div>
      <div class="cp-bar"><span class="cp-uc" style="width:${(d.ratio / max * 100).toFixed(2)}%" title="${esc(d.name)}: ${d.ratio.toFixed(1)} times"></span></div></div>`).join("");
    const desc = R.map(d => `${d.name} ${d.ratio.toFixed(1)} times`).join(", ");
    const excluded = rows.filter(r => !R.some(d => d.r === r)).map(r => `${full(r)} (${r.firm !== "Cushman & Wakefield" ? "figures from " + r.firm : "no operational figure published"})`);
    return `<div class="cp-two"><figure class="cp-fig"><div class="cp-bars" role="img" aria-label="Capacity being built or planned, as a multiple of capacity running now: ${esc(desc)}">${bars}</div>
        <figcaption>Capacity under construction or planned, divided by capacity running now. All from one firm, Cushman &amp; Wakefield (mid-2026), so the markets compare like with like.</figcaption></figure>
      <ul class="cp-story">${R.map(d => `<li><strong>${esc(d.name)}:</strong> ${fmt(d.ahead)} MW being built or planned, <strong>${d.ratio.toFixed(1)} times</strong> the ${fmt(d.op)} MW running. ${d.ratio >= 5 ? "Most of it is still a plan, and depends on power, permits and financing arriving." : d.op >= 500 ? "A large pipeline on an already large base." : "An early market: still small in megawatts."}</li>`).join("")}</ul></div>
      ${excluded.length ? `<p class="small muted">Left out of this comparison: ${esc(excluded.join("; "))}.</p>` : ""}`;
  }
  /* ---------- can it be checked? A profile, with no total ---------- */
  const PQ = [["public_list", "Public list", "Is there a public list of data centres that names their operators?"],
              ["capacity_official", "Official capacity", "Does a government body publish data centre capacity?"],
              ["chip_permit", "Chip permit", "Is there a permit or licence for moving AI chips?"],
              ["enforcement_public", "Enforcement made public", "Are chip seizures, charges or investigations announced?"],
              ["technical_unit", "Technical unit", "Is there a public body with the skills to audit a site or test a model?"]];
  const PS = { yes: ["Yes", "✓"], partly: ["Partly", "½"], checked_not_found: ["Not found", "○"], none: ["Not checked yet", "–"] };
  const MEMBERS = ["SG", "ID", "MY", "VN", "PH", "TH", "KH", "LA", "MM", "BN", "TL"];
  function profile(rows) {
    const at = (c, q) => rows.find(r => r.country === c && r.question === q);
    const done = rows.length, all = MEMBERS.length * PQ.length;
    const cell = (c, q) => { const r = at(c, q), st = r ? r.status : "none", [l, ic] = PS[st];
      const chip = st === "none" ? `<span class="pf-dash" aria-hidden="true">–</span><span class="sr">Not checked yet</span>` : `<span class="pf-chip pf-${st}"><span aria-hidden="true">${ic}</span> ${l}</span>`;
      return `<td>${r ? `<a class="pf-link" href="#pf-${esc(r.id)}" aria-label="${esc(CT[c])}, ${esc(PQ.find(x => x[0] === q)[1])}: ${l}. See the evidence">${chip}</a>` : chip}</td>`; };
    const notes = MEMBERS.filter(c => rows.some(r => r.country === c)).map(c => `<li><h4>${esc(CT[c])}</h4><ul>${PQ.filter(([q]) => at(c, q)).map(([q, short]) => { const r = at(c, q);
      return `<li id="pf-${esc(r.id)}" class="pf-note" tabindex="-1"><span class="pf-chip pf-${esc(r.status)}"><span aria-hidden="true">${PS[r.status][1]}</span> ${PS[r.status][0]}</span> <strong>${esc(short)}.</strong> ${esc(r.detail)}
        <span class="small muted">${r.source_url ? `<a href="${esc(r.source_url)}" target="_blank" rel="noopener">${esc(r.source_title)}</a> · ` : ""}checked ${esc(when(r.checked_on, "day"))} · ${esc(r.confidence)} confidence</span></li>`; }).join("")}</ul></li>`).join("");
    return `<p>Five questions about whether what happens with compute <strong>could be checked</strong> in each country. There is <strong>no total and no ranking</strong>: the gaps are the story.</p>
      <div class="pf-legend" aria-label="What the marks mean">${Object.entries(PS).map(([k, [l, ic]]) => `<span class="pf-chip pf-${k}"><span aria-hidden="true">${ic}</span> ${l}</span>`).join("")}</div>
      <p class="pf-swipe small muted" aria-hidden="true">Scroll sideways to see all five questions →</p>
      <div class="tablewrap pf-wrap"><table class="pf"><caption class="sr">Can it be checked? Five questions for each ASEAN member</caption>
        <thead><tr><th scope="col">Country</th>${PQ.map(([, short, full]) => `<th scope="col"><span title="${esc(full)}">${esc(short)}</span></th>`).join("")}</tr></thead>
        <tbody>${MEMBERS.map(c => `<tr><th scope="row">${esc(CT[c])}</th>${PQ.map(([q]) => cell(c, q)).join("")}</tr>`).join("")}</tbody></table></div>
      <ol class="pf-q small">${PQ.map(([, short, full]) => `<li><strong>${esc(short)}:</strong> ${esc(full)}</li>`).join("")}</ol>
      <p class="pf-cover"><strong>Checked so far: ${done} of ${all}.</strong> "Not checked yet" is a gap in this tracker, not a judgement about the country.</p>
      ${notes ? `<h4 class="pf-h">What was found</h4><ul class="pf-notes">${notes}</ul>` : ""}`;
  }
  function glance(C) {
    const R = ratioRows(C.capacity), top = R[0], big = [...C.capacity].filter(r => r.firm === "Cushman & Wakefield").sort((a, b) => ((+b.operational_mw || 0) + (+b.under_construction_mw || 0) + (+b.planned_mw || 0)) - ((+a.operational_mw || 0) + (+a.under_construction_mw || 0) + (+a.planned_mw || 0)))[0];
    const tot = r => (+r.operational_mw || 0) + (+r.under_construction_mw || 0) + (+r.planned_mw || 0);
    const card = (n, l, href) => `<a class="cp-card" href="${href}"><span class="cp-n">${n}</span><span class="cp-l">${l}</span></a>`;
    return `<div class="cp-glance" aria-label="At a glance">
      ${big ? card(fmt(tot(big)) + " MW", `${esc(full(big))}: running, being built and planned`, "#cp-capacity") : ""}
      ${top ? card(top.ratio.toFixed(1) + " ×", `${esc(top.name)}: planned capacity compared with what runs now`, "#cp-ratio") : ""}
      ${card(String(C.measures.length), "Rules, responses and cases about chips", "#cp-chips")}
      ${card(`${(C.profile || []).length} of ${MEMBERS.length * PQ.length}`, "Questions checked in the profile", "#cp-profile")}</div>`;
  }
  function render(panel, D) {
    const C = (D && D.compute) || { capacity: [], sites: [], measures: [], profile: [] };
    const langs = {}; [...C.sites, ...C.measures].forEach(r => { const l = r.source_language || "en"; langs[l] = (langs[l] || 0) + 1; });
    const total = Object.values(langs).reduce((a, b) => a + b, 0) || 1;
    panel.innerHTML = `<div class="cp">
      <header class="cp-head"><h2>Compute: chips, data centres and verification</h2>
        <p>AI governance and safety depend on <strong>compute</strong>: the chips and data centres that train and run AI. Southeast Asia is now one of the world's fastest-growing places for them,
        so rules about where chips go, and how anyone could check what runs on them, increasingly concern this region. This tab records what is <strong>published</strong>, says what is <strong>not</strong>, and explains what could be checked.</p>
        ${glance(C)}
        <nav class="cp-toc" aria-label="On this tab">${[["cp-capacity", "Capacity"], ["cp-ratio", "Planned versus running"], ["cp-profile", "Can it be checked?"], ["cp-sites", "Projects"], ["cp-chips", "Chips"],
          ["cp-signals", "When it isn't in the news"], ["cp-verify", "Verification"], ["cp-langs", "Languages"], ["cp-data", "Data"]].map(([h, l]) => `<a href="#${h}">${l}</a>`).join("")}</nav></header>

      <section id="cp-capacity" aria-labelledby="cp-h1"><h3 id="cp-h1">Where the capacity is</h3>${C.capacity.length ? capacityChart(C.capacity) + capacityTable(C.capacity) : '<p class="muted">No capacity figures yet.</p>'}</section>

      <section id="cp-ratio" aria-labelledby="cp-h1b"><h3 id="cp-h1b">Planned versus running</h3>${ratioChart(C.capacity)}</section>

      <section id="cp-profile" aria-labelledby="cp-h1c"><h3 id="cp-h1c">Can it be checked?</h3>${profile(C.profile || [])}</section>

      <section id="cp-sites" aria-labelledby="cp-h2"><h3 id="cp-h2">Named projects</h3>
        <p class="small muted">Projects named in published sources. "Not published" means the source did not say; it does not mean there is nothing to say. An announcement is not a building.</p>${sitesTable(C.sites)}</section>

      <section id="cp-chips" aria-labelledby="cp-h3"><h3 id="cp-h3">Chips: rules, responses and cases</h3>
        <p class="cp-caution">Investigations and charges are recorded as reported. <strong>An investigation is not a finding, and a charge is an allegation until a court decides.</strong> This tracker does not name people.</p>
        <div class="cp-filter" role="group" aria-label="Show"><button type="button" aria-pressed="true" data-k="">All</button>${[...new Set(C.measures.map(m => m.kind))].map(k => `<button type="button" aria-pressed="false" data-k="${esc(k)}">${esc(KIND[k] || k)}</button>`).join("")}</div>
        <ol class="cp-ml">${measuresList(C.measures, "")}</ol></section>

      <section id="cp-signals" aria-labelledby="cp-h4"><h3 id="cp-h4">When it isn't in the news</h3>
        <p>Most movement of chips and capacity is never reported. These <strong>public signals</strong> can show where to look. Each one is a <strong>question to check</strong>, never evidence on its own, and never a reason to name anyone.</p>
        <div class="tablewrap"><table class="cp-t"><caption class="sr">Public signals, what each shows, where to find it and its limits</caption>
          <thead><tr><th scope="col">Signal</th><th scope="col">What it can show</th><th scope="col">Where to find it</th><th scope="col">Limits</th></tr></thead>
          <tbody>${SIGNALS.map(s => `<tr><th scope="row">${esc(s[0])}</th><td>${esc(s[1])}</td><td>${esc(s[2])}</td><td>${esc(s[3])}</td></tr>`).join("")}</tbody></table></div>
        <h4>Questions to check for each country</h4><ul>${QUESTIONS.map(q => `<li>${esc(q)}</li>`).join("")}</ul></section>

      <section id="cp-verify" aria-labelledby="cp-h5"><h3 id="cp-h5">Verification: what could be checked, by whom, with whose cooperation</h3>
        <p>Verification is not one technology. It is a set of checks at different <strong>layers</strong>, from the border to the model itself. The outer layers need little from AI developers,
        but say little about what is running. The inner layers say the most, but need the developer's agreement. <strong>Software methods</strong> are quicker to deploy than new hardware,
        but there is no guarantee that frontier developers will accept verification software, or monitoring of their networks. That is why it matters what <strong>host countries</strong> can check without them.</p>
        <div class="tablewrap"><table class="cp-t cp-layers"><caption class="sr">Layers of verification</caption>
          <thead><tr><th scope="col">Layer</th><th scope="col">What could be checked</th><th scope="col">Who could check</th><th scope="col">Whose cooperation it needs</th><th scope="col">What a host country can do</th></tr></thead>
          <tbody>${LAYERS.map(l => `<tr><th scope="row">${esc(l[0])}</th>${l.slice(1).map(c => `<td>${esc(c)}</td>`).join("")}</tr>`).join("")}</tbody></table></div>
        <p class="small">No single layer is enough on its own. Researchers describe combining several, so that each covers another's weak points; hardware approaches are described as tractable but not solved.</p>
        <h4>Reading</h4><ul class="cp-read">${READING.map(r => `<li><a href="${esc(r[2])}" target="_blank" rel="noopener">${esc(r[0])}</a> <span class="muted">${esc(r[1])}</span></li>`).join("")}</ul></section>

      <section id="cp-langs" aria-labelledby="cp-h6"><h3 id="cp-h6">Reading the region</h3>
        <p>Much of what matters here is first published in <strong>Malay, Indonesian, Thai, Vietnamese, Filipino, Khmer, Lao or Burmese</strong>: customs notices, court listings, local news and ministry statements.
        Every row on this tab records its source language, so gaps show.</p>
        <p class="small">Sources so far: ${Object.entries(langs).map(([l, n]) => `${esc(LANG[l] || l)} ${Math.round(n / total * 100)}%`).join(", ") || "none"}.
        ${Object.keys(langs).length === 1 && langs.en ? "<strong>All are in English: that is a gap this tracker aims to close.</strong>" : ""}</p>
        <p class="small">Regional language models such as AI Singapore's <strong>SEA-LION</strong> can give a first reading of these sources. A person who reads the language checks every summary
        before it is published here, and the original wording is kept for anything quoted.</p></section>

      <section id="cp-data" aria-labelledby="cp-h7"><h3 id="cp-h7">Data</h3>
        <div class="cp-dl"><button type="button" class="btn" data-dl="capacity">Capacity (CSV)</button><button type="button" class="btn" data-dl="sites">Projects (CSV)</button>
        <button type="button" class="btn" data-dl="measures">Chips measures (CSV)</button><button type="button" class="btn" data-dl="profile">Profile (CSV)</button><a class="btn" href="tracker-data.json">All data (JSON)</a></div>
        <p class="small muted">Free to reuse with credit (see the data licence). Corrections and new sources are welcome, in any of the region's languages.</p></section>
    </div>`;
    panel.querySelectorAll('a[href^="#cp-"], a[href^="#pf-"]').forEach(a => a.addEventListener("click", e => {
      const t = panel.querySelector(a.getAttribute("href")); if (!t) return; e.preventDefault();
      t.scrollIntoView({ behavior: matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth", block: "start" }); if (t.tabIndex === -1) t.focus({ preventScroll: true }); }));
    panel.querySelectorAll(".cp-filter button").forEach(b => b.addEventListener("click", () => {
      panel.querySelectorAll(".cp-filter button").forEach(x => x.setAttribute("aria-pressed", String(x === b)));
      panel.querySelector(".cp-ml").innerHTML = measuresList(C.measures, b.dataset.k); }));
    panel.querySelectorAll("[data-dl]").forEach(b => b.addEventListener("click", () => {
      const k = b.dataset.dl; download(`asean-compute-${k}.csv`, C[k] || []); }));
  }
  window.ComputeTab = { render };
})();
