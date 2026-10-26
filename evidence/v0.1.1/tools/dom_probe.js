// DOM fact extraction for one rendered report page (runs in the page with
// page JavaScript disabled; Playwright evaluates this function directly).
// It only collects facts; all pass/fail decisions are made in evaluate.py.
(params) => {
  const OTHER_BLOCKS = new Set([
    "PRE", "TABLE", "HR", "DIV", "DETAILS", "SUMMARY", "DL", "DT", "DD",
    "SECTION", "ARTICLE", "ASIDE", "NAV", "HEADER", "FOOTER", "MAIN", "FORM",
    "FIELDSET", "FIGURE", "IFRAME", "OBJECT", "EMBED", "IMG", "VIDEO", "AUDIO",
    "CANVAS", "SVG", "MATH", "TEXTAREA", "SELECT", "BUTTON", "INPUT", "SCRIPT",
    "STYLE", "TEMPLATE", "NOSCRIPT", "LINK", "META", "BASE", "CENTER", "MARQUEE",
    "FRAMESET", "FRAME", "DIALOG", "MENU", "ADDRESS", "PICTURE", "SOURCE",
  ]);
  const HEADINGS = new Set(["H1", "H2", "H3", "H4", "H5", "H6"]);
  const CONTROL_RE = /[\p{Cc}\p{Cf}\p{Zl}\p{Zp}\p{Cs}]/gu;
  const body = document.body;

  const visibility = (el) => {
    const reasons = [];
    if (!el.checkVisibility({ contentVisibilityAuto: true, opacityProperty: true,
                              visibilityProperty: true })) {
      reasons.push("checkVisibility=false");
    }
    for (let e = el; e && e.nodeType === 1; e = e.parentElement) {
      if (e.hasAttribute("hidden")) reasons.push("hidden-attr:" + e.tagName);
      const cs = getComputedStyle(e);
      if (cs.display === "none") reasons.push("display-none:" + e.tagName);
      if (parseFloat(cs.opacity) === 0) reasons.push("opacity-0:" + e.tagName);
      if (e.tagName === "DETAILS" && !e.open && !el.closest("summary")) {
        reasons.push("closed-details");
      }
    }
    const cs = getComputedStyle(el);
    if (cs.visibility !== "visible") reasons.push("visibility:" + cs.visibility);
    if (parseFloat(cs.fontSize) < 1) reasons.push("font-size<1px");
    if (cs.color === "rgba(0, 0, 0, 0)") reasons.push("transparent-color");
    const rect = el.getBoundingClientRect();
    if (!(rect.width > 0 && rect.height > 0)) reasons.push("zero-box");
    return reasons;
  };

  // Units: headings, list items, top-level paragraphs, block quotes, other blocks.
  const unitOf = new Map();
  const units = [];
  const all = Array.from(body.querySelectorAll("*"));
  for (const el of all) {
    const tag = el.tagName;
    let kind = null;
    if (HEADINGS.has(tag)) kind = "heading";
    else if (tag === "LI") kind = "li";
    else if (tag === "BLOCKQUOTE") kind = "blockquote";
    else if (tag === "P") kind = el.parentElement.closest("li, blockquote") ? null : "p";
    else if (OTHER_BLOCKS.has(tag)) kind = "other";
    if (kind === null) continue;
    unitOf.set(el, units.length);
    units.push({ index: units.length, tag: tag.toLowerCase(), kind, text: "",
                 visible_reasons: visibility(el) });
  }
  const nearestUnit = (node) => {
    for (let e = node.parentElement; e && e !== body; e = e.parentElement) {
      if (unitOf.has(e)) return unitOf.get(e);
    }
    return -1;
  };

  const textWalker = document.createTreeWalker(body, NodeFilter.SHOW_TEXT);
  const orphanText = [];
  const textNodes = [];
  for (let n = textWalker.nextNode(); n; n = textWalker.nextNode()) {
    const u = nearestUnit(n);
    textNodes.push([n, u]);
    if (u >= 0) units[u].text += n.data;
    else if (n.data.trim() !== "") orphanText.push(n.data.slice(0, 200));
  }

  // Raw control code points per unit (Cc except TAB/LF/CR, Cf, Zl, Zp, Cs).
  const controls = [];
  for (const [n, u] of textNodes) {
    for (const m of n.data.matchAll(CONTROL_RE)) {
      const cp = m[0].codePointAt(0);
      if (cp === 9 || cp === 10 || cp === 13) continue;
      controls.push({ unit: u, cp: "U+" + cp.toString(16).toUpperCase().padStart(4, "0") });
    }
  }

  // Comments anywhere in the document; element tags and attributes in body.
  const comments = [];
  const commentWalker = document.createTreeWalker(document, NodeFilter.SHOW_COMMENT);
  for (let c = commentWalker.nextNode(); c; c = commentWalker.nextNode()) {
    comments.push(c.data.slice(0, 120));
  }
  const tagCounts = {};
  const attributes = [];
  for (const el of all) {
    const t = el.tagName.toLowerCase();
    tagCounts[t] = (tagCounts[t] || 0) + 1;
    for (const a of el.attributes) {
      attributes.push({ tag: t, name: a.name, value: a.value.slice(0, 120) });
    }
  }

  // Sentinel occurrences (visible text only) and hidden copies elsewhere.
  const locate = (token) => {
    const hits = [];
    for (const [n, u] of textNodes) {
      let from = 0;
      for (;;) {
        const at = n.data.indexOf(token, from);
        if (at < 0) break;
        const range = document.createRange();
        range.setStart(n, at);
        range.setEnd(n, at + token.length);
        const rects = Array.from(range.getClientRects()).filter(
          (r) => r.width > 0 && r.height > 0);
        const parentReasons = visibility(n.parentElement);
        hits.push({ unit: u, visible: rects.length > 0 && parentReasons.length === 0,
                    reasons: parentReasons });
        from = at + token.length;
      }
    }
    const inComments = comments.filter((c) => c.includes(token)).length;
    const inAttributes = attributes.filter((a) => a.value.includes(token)).length;
    const inHead = document.head ? document.head.textContent.includes(token) : false;
    return { token, hits, in_comments: inComments, in_attributes: inAttributes,
             in_head: inHead };
  };
  const sentinels = (params.tokens || []).map(locate);

  // Elements inside each payload range [begin token start, end token end].
  const findNode = (token) => {
    for (const [n, u] of textNodes) {
      const at = n.data.indexOf(token);
      if (at >= 0) return [n, at, u];
    }
    return null;
  };
  const ranges = (params.fields || []).map((f) => {
    const b = findNode(f.begin);
    const e = findNode(f.end);
    if (!b || !e || b[2] !== e[2] || b[2] < 0) return { field: f.field, tags: null };
    const range = document.createRange();
    range.setStart(b[0], b[1]);
    range.setEnd(e[0], e[1] + f.end.length);
    const unitEl = all.find((el) => unitOf.get(el) === b[2]);
    const tags = [];
    for (const el of unitEl.querySelectorAll("*")) {
      if (range.intersectsNode(el)) tags.push(el.tagName.toLowerCase());
    }
    return { field: f.field, unit: b[2], tags };
  });

  return {
    units,
    orphan_text: orphanText,
    controls,
    comments,
    tag_counts: tagCounts,
    attributes,
    sentinels,
    ranges,
    body_text_length: body.textContent.length,
  };
}
