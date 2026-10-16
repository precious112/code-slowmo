#!/usr/bin/env python3
"""Build a code-slowmo page: page data (JSON) -> one self-contained HTML file.

Usage:
    python3 build.py page.json [out.html] [--force]

Steps:
  1. Checks the page data for structural mistakes (unknown ids, missing fields).
  2. Runs check_text.py on every reader-facing sentence. Errors stop the build,
     because plain writing is the point of these pages. --force skips this (avoid it).
  3. Injects the data into assets/template.html and writes the HTML file.

Needs only Python 3.8+. The output opens in any browser, with no server.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import check_text  # noqa: E402

TEMPLATE = os.path.join(HERE, "..", "assets", "template.html")
SECTION_TYPES = {"glossary", "text", "map", "flow", "trace", "compare", "custom"}


def structure_errors(page):
    errs = []
    if not page.get("title"):
        errs.append("$.title is missing. Name the page.")
    if not page.get("question"):
        errs.append("$.question is missing. Every page answers one question; state it.")
    if not page.get("takeaway"):
        errs.append("$.takeaway is missing. End with the one thing the reader should remember.")
    roles = page.get("roles") or []
    if len(roles) > 5:
        errs.append(f"$.roles has {len(roles)} entries. Use at most 5 colors, or the colors stop meaning anything.")
    role_ids = {r.get("id") for r in roles}

    def role_ok(r, where):
        if r is not None and r not in role_ids:
            errs.append(f"{where}: role \"{r}\" is not in $.roles.")

    secs = page.get("sections")
    if not secs:
        errs.append("$.sections is empty. Add at least one section.")
        return errs
    ids = set()
    for i, s in enumerate(secs):
        w = f"$.sections[{i}]"
        t = s.get("type")
        if t not in SECTION_TYPES:
            errs.append(f"{w}.type \"{t}\" is not one of {sorted(SECTION_TYPES)}.")
            continue
        sid = s.get("id") or f"{t}{i+1}"
        if sid in ids:
            errs.append(f"{w}.id \"{sid}\" is used twice.")
        ids.add(sid)
        if t == "map":
            areas = {a.get("id") for a in s.get("areas") or []}
            parts = {p.get("id") for p in s.get("parts") or []}
            for j, p in enumerate(s.get("parts") or []):
                if p.get("area") not in areas:
                    errs.append(f"{w}.parts[{j}] ({p.get('id')}): area \"{p.get('area')}\" does not exist.")
                role_ok(p.get("role"), f"{w}.parts[{j}]")
                if not p.get("about"):
                    errs.append(f"{w}.parts[{j}] ({p.get('id')}): add \"about\", a plain explanation of what it does.")
            for j, l in enumerate(s.get("links") or []):
                for end in ("from", "to"):
                    if l.get(end) not in parts:
                        errs.append(f"{w}.links[{j}].{end} \"{l.get(end)}\" is not a part id.")
                role_ok(l.get("role"), f"{w}.links[{j}]")
            for j, row in enumerate(s.get("rows") or []):
                for a in row:
                    if a not in areas:
                        errs.append(f"{w}.rows[{j}] names area \"{a}\", which does not exist.")
            if s.get("rows"):
                placed = {a for row in s["rows"] for a in row}
                for a in areas - placed:
                    errs.append(f"{w}: area \"{a}\" is not placed in any row.")
            link_ids = {l.get("id") for l in s.get("links") or [] if l.get("id")}
            for j, st in enumerate(s.get("tour") or []):
                for p in st.get("parts") or []:
                    if p not in parts:
                        errs.append(f"{w}.tour[{j}].parts: \"{p}\" is not a part id.")
                for l in st.get("links") or []:
                    if l not in link_ids:
                        errs.append(f"{w}.tour[{j}].links: \"{l}\" is not a link id (give the link an \"id\").")
                if not st.get("say"):
                    errs.append(f"{w}.tour[{j}]: missing \"say\".")
        elif t == "flow":
            lanes = {l.get("id") for l in s.get("lanes") or []}
            for j, l in enumerate(s.get("lanes") or []):
                role_ok(l.get("role"), f"{w}.lanes[{j}]")
            for j, m in enumerate(s.get("steps") or []):
                for end in ("from", "to"):
                    if m.get(end) not in lanes:
                        errs.append(f"{w}.steps[{j}].{end} \"{m.get(end)}\" is not a lane id.")
                if not m.get("say"):
                    errs.append(f"{w}.steps[{j}]: missing \"say\".")
                if not m.get("label"):
                    errs.append(f"{w}.steps[{j}]: missing \"label\" (the few words on the arrow).")
        elif t == "trace":
            files = s.get("files") or {}
            frames = s.get("frames") or {}
            for k, f in files.items():
                if "code" not in f:
                    errs.append(f"{w}.files.{k}: missing \"code\".")
                if not f.get("path"):
                    errs.append(f"{w}.files.{k}: missing \"path\" (the real file path).")
            for k, fr in frames.items():
                role_ok(fr.get("role"), f"{w}.frames.{k}")
            for j, st in enumerate(s.get("steps") or []):
                f = files.get(st.get("file"))
                if not f:
                    errs.append(f"{w}.steps[{j}].file \"{st.get('file')}\" is not in files.")
                    continue
                start = f.get("start", 1)
                n = len(str(f.get("code", "")).rstrip("\n").split("\n"))
                for fld in ("line", "to"):
                    v = st.get(fld)
                    if v is not None and not (start <= v < start + n):
                        errs.append(f"{w}.steps[{j}].{fld} = {v} is outside {f.get('path')} lines {start}-{start+n-1}.")
                for fr in st.get("stack") or []:
                    if isinstance(fr, str) and fr not in frames:
                        errs.append(f"{w}.steps[{j}].stack: \"{fr}\" is not in frames.")
                if not st.get("say"):
                    errs.append(f"{w}.steps[{j}]: missing \"say\".")
                ask = st.get("ask")
                if ask and not (isinstance(ask.get("options"), list) and isinstance(ask.get("answer"), int) and ask.get("why")):
                    errs.append(f"{w}.steps[{j}].ask needs q, options (list), answer (index) and why.")
                for k2, lg in enumerate(st.get("log") or []):
                    if not isinstance(lg, dict) or "text" not in lg:
                        errs.append(f"{w}.steps[{j}].log[{k2}] must be {{\"role\": ..., \"text\": ...}}.")
                    else:
                        role_ok(lg.get("role"), f"{w}.steps[{j}].log[{k2}]")
            if not any(st.get("ask") for st in s.get("steps") or []):
                errs.append(f"{w}: add at least one \"ask\" (a guess-first question) at a key step.")
        elif t == "compare":
            for side in ("left", "right"):
                if not (s.get(side) or {}).get("title"):
                    errs.append(f"{w}.{side}.title is missing.")
        elif t == "glossary":
            for j, it in enumerate(s.get("items") or []):
                if not it.get("word") or not it.get("meaning"):
                    errs.append(f"{w}.items[{j}] needs \"word\" and \"meaning\".")
    return errs


NUMBER_WORDS = {"two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
                "eleven": 11, "twelve": 12}
COUNTED = {"glossary": [("items", r"words?|cards?|terms?")],
           "map": [("areas", r"areas?|regions?"), ("parts", r"parts?|pieces?"), ("tour", r"(?:tour )?steps?|stops?")],
           "flow": [("steps", r"steps?|messages?|arrows?"), ("lanes", r"lanes?|columns?")],
           "trace": [("steps", r"steps?")], "compare": [("steps", r"steps?")]}


def count_warnings(page):
    """Warn when an intro states a count ("Six areas") that doesn't match what the section holds."""
    import re
    warns = []
    for i, s in enumerate(page.get("sections") or []):
        text = " ".join(x if isinstance(x, str) else "" for x in ([s.get("intro")] if isinstance(s.get("intro"), str) else (s.get("intro") or [])))
        for field, noun in COUNTED.get(s.get("type"), []):
            n = len(s.get(field) or [])
            for m in re.finditer(r"\b(\d+|" + "|".join(NUMBER_WORDS) + r")\s+(?:[a-z-]+\s+)?(" + noun + r")\b", text, re.I):
                said = m.group(1).lower()
                said = int(said) if said.isdigit() else NUMBER_WORDS[said]
                if said != n:
                    warns.append(f"$.sections[{i}].intro says \"{m.group(0)}\" but the section has {n} {field}.")
    return warns


def main(argv):
    args = [a for a in argv[1:] if not a.startswith("--")]
    force = "--force" in argv
    if not args:
        print(__doc__)
        return 2
    src = args[0]
    out = args[1] if len(args) > 1 else os.path.splitext(src)[0] + ".html"
    try:
        with open(src, encoding="utf-8") as f:
            page = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        print(f"Could not read {src}: {e}")
        return 2

    serr = structure_errors(page)
    terr, twarn = check_text.check(page)
    twarn = count_warnings(page) + twarn
    for e in serr:
        print("ERROR ", e)
    for e in terr:
        print("ERROR ", e)
    for w in twarn:
        print("WARN  ", w)
    print(f"\n{len(serr) + len(terr)} errors, {len(twarn)} warnings.")
    if serr:
        print("Fix the structure errors above; the page would not draw correctly.")
        return 1
    if terr and not force:
        print("Not built. Plain writing is the point of these pages: fix every ERROR, then build again.")
        return 1

    with open(TEMPLATE, encoding="utf-8") as f:
        html = f.read()
    data = json.dumps(page, ensure_ascii=False).replace("</", "<\\/").replace("<!--", "\\u003c!--")
    title = str(page.get("title", "Code explainer")).replace("&", "&amp;").replace("<", "&lt;")
    html = html.replace("__TITLE__", title, 1).replace("__PAGE_JSON__", data, 1)
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Built {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
