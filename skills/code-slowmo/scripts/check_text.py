#!/usr/bin/env python3
"""Check every piece of reader-facing text in a code-slowmo page file for plain writing.

Usage:
    python3 check_text.py page.json

Exit code 0 = no errors (warnings may remain), 1 = errors found, 2 = bad input.
build.py runs this automatically and refuses to build while errors remain.

What it checks (see references/writing.md for the reasons):
  ERROR  a step explanation over 45 words
  ERROR  a sentence over 32 words
  ERROR  a code name in <code>...</code> that has no plain explanation in "terms"
  ERROR  filler or inflated words (utilize, leverage, seamless, delve, ...)
  WARN   a step explanation over 40 words, or a sentence over 24 words
  WARN   tech words a newcomer may not know, used without an explanation
  WARN   passive voice ("is created", "was called")
  WARN   em dashes, which usually hide a second sentence
  WARN   vague openers like "It", "This" or "That" with no clear subject
  WARN   arrow and map labels longer than 6 words
"""
import json
import re
import sys

STEP_FIELDS = {"say"}
LABEL_FIELDS = {"label", "tick", "name", "word", "title"}
PROSE_FIELDS = {"say", "about", "intro", "meaning", "example", "question", "takeaway", "body", "q", "why", "text", "start"}

BANNED = [
    "utilize", "utilise", "utilizes", "utilizing", "leverage", "leverages", "leveraging", "facilitate", "facilitates",
    "seamless", "seamlessly", "robust", "delve", "delves", "orchestrate", "orchestrates", "paradigm", "synergy",
    "holistic", "plethora", "myriad", "underscores", "it's worth noting", "it is worth noting", "worth noting",
    "needless to say", "at the end of the day", "in essence", "a testament to", "plays a crucial role",
    "plays a key role", "plays a vital role", "under the hood", "magic", "magically", "elegant", "elegantly",
    "powerful", "cutting-edge", "state-of-the-art", "game-changer", "in order to", "whilst", "thereby", "henceforth",
]
SOFT = ["simply", "just", "basically", "essentially", "obviously", "clearly", "of course", "actually"]
JARGON = [
    "reducer", "dispatch", "dispatches", "dispatched", "hydrate", "hydration", "reconcile", "reconciliation", "mount",
    "mounts", "unmount", "payload", "schema", "middleware", "callback", "callbacks", "closure", "promise", "promises",
    "idempotent", "mutation", "mutate", "mutates", "immutable", "immutably", "serialize", "serialized", "deserialize",
    "ast", "dom", "iframe", "portal", "hook", "hooks", "props", "memoize", "memoized", "memo", "selector", "subscribe",
    "subscribes", "subscriber", "subscribers", "thunk", "saga", "observable", "debounce", "debounced", "throttle",
    "throttled", "polyfill", "transpile", "bundler", "runtime", "middleware", "endpoint", "handler", "instantiate",
    "singleton", "invariant", "heuristic", "abstraction", "orm", "mutex", "semaphore", "coroutine", "goroutine",
    "api", "apis", "headless", "sdk", "daemon", "rpc", "ipc", "websocket", "stdin", "stdout", "uds", "jsonl",
]
PASSIVE = re.compile(r"\b(is|are|was|were|be|been|being|gets|got)\s+(\w+ed|built|made|done|sent|run|set|kept|held|thrown|written|drawn|shown|given|taken|found|read)\b", re.I)
NOTE_THAT = re.compile(r"(^|[.!?]\s+)(please\s+)?note that\b", re.I)
VAGUE = re.compile(r"(^|[.!?]\s+)(It|This|That|These|Those)\s+(is|does|ends|handles|takes care|deals|works|happens|means)\b")


def plain(html):
    """Strip tags and entities so we count only the words a reader sees."""
    t = re.sub(r"<code>(.*?)</code>", lambda m: " CODE ", html or "", flags=re.S)
    t = re.sub(r"<[^>]+>", " ", t)
    t = re.sub(r"&\w+;", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def words(text):
    return re.findall(r"[A-Za-z0-9][\w'’-]*", text)


def sentences(text):
    return [s for s in re.split(r"(?<=[.!?])\s+(?=[A-Z0-9\"“(])", text) if s.strip()]


def walk(node, path="$"):
    """Yield (path, field, value) for every string in the page data."""
    if isinstance(node, dict):
        for k, v in node.items():
            if isinstance(v, str):
                yield f"{path}.{k}", k, v
            elif isinstance(v, list) and all(isinstance(x, str) for x in v) and k in PROSE_FIELDS | {"options"}:
                for i, x in enumerate(v):
                    yield f"{path}.{k}[{i}]", k, x
            else:
                yield from walk(v, f"{path}.{k}")
    elif isinstance(node, list):
        for i, v in enumerate(node):
            yield from walk(v, f"{path}[{i}]")


SKIP_KEYS = {"code", "file", "path", "html", "script", "id", "from", "to", "role", "area", "screen", "lanes", "rows",
             "eyebrow", "subject", "note", "alt", "footer", "sub", "stateLabel", "screenLabel", "phase"}


def check(page):
    errors, warns = [], []
    terms = {k.strip() for k in (page.get("terms") or {})}
    explained_lower = {t.lower() for t in terms}
    for r in page.get("roles") or []:
        explained_lower.add(str(r.get("name", "")).lower())
    for sec in page.get("sections") or []:
        if sec.get("type") == "glossary":
            for it in sec.get("items") or []:
                explained_lower.add(str(it.get("word", "")).lower())
                if it.get("code"):
                    explained_lower.add(str(it["code"]).lower())
        # names of map parts and flow lanes come with their own explanations
        for p in (sec.get("parts") or []) + (sec.get("lanes") or []) + (sec.get("areas") or []):
            explained_lower.add(str(p.get("name", "")).lower())

    def explained(word, text_low):
        if word in explained_lower or any(re.search(r"(?<![\w-])" + re.escape(word) + r"(?![\w-])", e) for e in explained_lower):
            return True
        # explained right where it is used: "iframe (a page inside the page)" or "iframe, a page inside the page"
        return bool(re.search(re.escape(word) + r"\s*(\(|,\s+(a|an|the|which|meaning)\b|:\s)", text_low))

    # skip code-ish containers entirely: trace files, variable values, state values
    def is_skipped(path):
        return bool(re.search(r"\.(files|vars|state|frames|terms)(\.|\[|$)", path)) or bool(re.search(r"\.(screen|html|script|code)$", path))

    for path, key, value in walk(page):
        if key in SKIP_KEYS or is_skipped(path):
            continue
        text = plain(value)
        if not text:
            continue
        low = " " + text.lower() + " "

        # unexplained code names
        for m in re.finditer(r"<code>(.*?)</code>", value, flags=re.S):
            raw = re.sub(r"<[^>]+>", "", m.group(1))
            raw = raw.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&")
            if raw not in terms:
                errors.append(f"{path}: <code>{raw}</code> has no plain explanation. Add it to \"terms\", or say it in plain words instead.")

        if key in LABEL_FIELDS:
            limit = 9 if key == "title" else 6
            if len(words(text)) > limit:
                warns.append(f"{path}: label is {len(words(text))} words. Keep labels to a few words: \"{text[:60]}\"")
            continue

        n = len(words(text))
        if key in ("about", "meaning", "why", "start") and n > 60:
            warns.append(f"{path}: {n} words. Keep explanations under about 60 words, or split them.")
        if key in STEP_FIELDS:
            if n > 45:
                errors.append(f"{path}: {n} words. Split this step in two (aim for 40 or fewer).")
            elif n > 40:
                warns.append(f"{path}: {n} words. Aim for 40 or fewer.")
        for s in sentences(text):
            sn = len(words(s))
            if sn > 32:
                errors.append(f"{path}: a {sn}-word sentence. Split it: \"{s[:70]}...\"")
            elif sn > 24:
                warns.append(f"{path}: a {sn}-word sentence. Shorter reads easier: \"{s[:70]}...\"")
        for w in BANNED:
            if re.search(r"(?<![\w-])" + re.escape(w) + r"(?![\w-])", low):
                errors.append(f"{path}: \"{w}\" is filler or inflated. Say the plain thing.")
        for w in SOFT:
            if re.search(r"(?<![\w-])" + re.escape(w) + r"(?![\w-])", low):
                warns.append(f"{path}: \"{w}\" usually adds nothing. Cut it if you can.")
        for w in JARGON:
            if re.search(r"(?<![\w-])" + re.escape(w) + r"(?![\w-])", low) and not explained(w, low):
                warns.append(f"{path}: \"{w}\" may be new to the reader. Explain it the first time (glossary or terms), or use a plain word.")
        if NOTE_THAT.search(text):
            errors.append(f"{path}: \"Note that\" is filler. Say the thing directly.")
        if PASSIVE.search(text):
            warns.append(f"{path}: passive voice (\"{PASSIVE.search(text).group(0)}\"). Say who does it.")
        if "—" in value:
            warns.append(f"{path}: em dash. Use two sentences instead.")
        if VAGUE.search(text):
            warns.append(f"{path}: starts a sentence with \"{VAGUE.search(text).group(2)} {VAGUE.search(text).group(3)}\". Name the thing so the reader knows who does what.")

    # dedupe jargon warnings: report each word once
    seen, uniq = set(), []
    for w in warns:
        k = re.sub(r"^\S+: ", "", w) if "may be new" in w else w
        if k in seen:
            continue
        seen.add(k)
        uniq.append(w)
    return errors, uniq


def main(argv):
    if len(argv) != 2:
        print(__doc__)
        return 2
    try:
        with open(argv[1], encoding="utf-8") as f:
            page = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        print(f"Could not read {argv[1]}: {e}")
        return 2
    errors, warns = check(page)
    for e in errors:
        print("ERROR ", e)
    for w in warns:
        print("WARN  ", w)
    print(f"\n{len(errors)} errors, {len(warns)} warnings.")
    if errors:
        print("Fix every ERROR. Then read each WARN and fix it unless you have a clear reason not to.")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
