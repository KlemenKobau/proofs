#!/usr/bin/env python3
"""Generate docs/index.html listing every documented theorem in the Proofs library.

A theorem is listed when it has a docstring (/-- ... -/) directly above it.
The first paragraph of the docstring becomes the headline statement, the rest
becomes the description. Undocumented theorems are skipped.

Usage: python3 scripts/gen_index.py [--src Proofs] [--out docs/index.html]
"""
import argparse
import html
import os
import re
import sys
from pathlib import Path

REPO_URL = "https://github.com/KlemenKobau/proofs"

DOCSTRING_RE = re.compile(r"/--(.*?)-/", re.S)
MODIFIERS = {"private", "protected", "noncomputable", "nonrec"}


def inline_md(text: str) -> str:
    """Escape HTML and render the small subset of Markdown used in docstrings."""
    out = html.escape(text, quote=False)
    out = re.sub(r"`([^`]+)`", r"<code>\1</code>", out)
    out = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", out)
    out = re.sub(r"(?<![*\w])\*([^*]+)\*(?![*\w])", r"<em>\1</em>", out)
    return out


def namespace_at(text: str, pos: int) -> str:
    """Return the active namespace at character offset pos."""
    stack = []  # entries: ("namespace" | "section", name)
    for m in re.finditer(r"^(namespace|section|end)\b[ \t]*([^\s]*)", text[:pos], re.M):
        kind, name = m.group(1), m.group(2)
        if kind in ("namespace", "section"):
            stack.append((kind, name))
        elif stack:
            stack.pop()
    return ".".join(n for k, n in stack if k == "namespace" and n)


def parse_file(path: Path, root: Path):
    text = path.read_text(encoding="utf-8")
    rel = path.relative_to(root).as_posix()
    module = rel[:-len(".lean")].replace("/", ".")
    doc_page = "docs/" + rel[:-len(".lean")] + ".html"
    results = []
    for m in DOCSTRING_RE.finditer(text):
        rest = text[m.end():]
        offset = m.end()
        # Skip whitespace, attributes like @[simp], and modifiers.
        while True:
            stripped = rest.lstrip()
            offset += len(rest) - len(stripped)
            rest = stripped
            if rest.startswith("@["):
                depth, i = 0, 0
                for i, ch in enumerate(rest):
                    if ch == "[":
                        depth += 1
                    elif ch == "]":
                        depth -= 1
                        if depth == 0:
                            break
                rest, offset = rest[i + 1:], offset + i + 1
                continue
            word = rest.split(None, 1)[0] if rest.split() else ""
            if word in MODIFIERS:
                rest, offset = rest[len(word):], offset + len(word)
                continue
            break
        decl = re.match(r"(theorem|lemma)\s+([^\s(:{\[]+)", rest)
        if not decl:
            continue
        sig_end = rest.find(":=")
        signature = rest[:sig_end].rstrip() if sig_end != -1 else rest.splitlines()[0]
        name = decl.group(2)
        ns = namespace_at(text, offset)
        full_name = f"{ns}.{name}" if ns and not name.startswith("_root_.") else name.removeprefix("_root_.")
        if ns:
            signature = signature.replace(f"{decl.group(1)} {name}", f"{decl.group(1)} {full_name}", 1)
        line = text.count("\n", 0, offset) + 1
        paragraphs = [p.strip() for p in re.split(r"\n\s*\n", m.group(1).strip()) if p.strip()]
        results.append({
            "name": full_name,
            "headline": " ".join(paragraphs[0].split()) if paragraphs else full_name,
            "description": [" ".join(p.split()) for p in paragraphs[1:]],
            "signature": signature,
            "doc_url": f"{doc_page}#{full_name}",
            "src_url": f"{REPO_URL}/blob/HEAD/{rel}#L{line}",
            "module": module,
        })
    return results


def render(theorems) -> str:
    sections = []
    for t in theorems:
        desc = "".join(f'    <p class="gloss">{inline_md(p)}</p>\n' for p in t["description"])
        sections.append(f"""  <section class="theorem" id="{html.escape(t['name'])}">
    <p class="statement">{inline_md(t['headline'])}</p>
{desc}    <pre><code>{html.escape(t['signature'], quote=False)}</code></pre>
    <p class="links"><a href="{html.escape(t['doc_url'])}">Read in docs</a><a href="{html.escape(t['src_url'])}">View source</a></p>
  </section>
""")
    body = "\n".join(sections) if sections else '  <p class="intro">No documented theorems yet. Add a <code>/-- … -/</code> docstring above a theorem to list it here.</p>\n'
    return TEMPLATE.replace("{{THEOREMS}}", body).replace("{{COUNT}}", str(len(theorems)))


TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Proofs · Lean 4 formalizations by Klemen Kobau</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,600;1,6..72,400&family=JetBrains+Mono:wght@400&display=swap" rel="stylesheet">
<style>
  :root {
    --paper: #f3f5f8; --ink: #18202c; --muted: #5a6577;
    --rule: #d5dbe4; --accent: #2b5c8a; --code-bg: #e8ecf2;
    color-scheme: light;
  }
  @media (prefers-color-scheme: dark) {
    :root {
      --paper: #141a23; --ink: #e6ebf2; --muted: #97a3b5;
      --rule: #2c3644; --accent: #8db8e3; --code-bg: #1d2531;
      color-scheme: dark;
    }
  }
  * { box-sizing: border-box; }
  body { margin: 0; background: var(--paper); color: var(--ink);
    font-family: "Newsreader", Georgia, "Times New Roman", serif; font-size: 1.125rem; line-height: 1.6; }
  main { max-width: 46rem; margin: 0 auto; padding: 4rem 1.5rem 3rem; }
  header { margin-bottom: 3.5rem; }
  h1 { font-size: 3.5rem; font-weight: 600; line-height: 1.05; margin: 0 0 1rem; letter-spacing: -0.01em; }
  .intro { color: var(--muted); max-width: 34rem; margin: 0; }
  a { color: var(--accent); text-underline-offset: 0.18em; }
  a:focus-visible { outline: 2px solid var(--accent); outline-offset: 3px; border-radius: 2px; }
  .theorem { border-top: 1px solid var(--rule); padding: 2rem 0; }
  .statement { font-size: 1.75rem; line-height: 1.35; margin: 0 0 0.35rem; font-style: italic; overflow-wrap: anywhere; }
  .gloss { color: var(--muted); margin: 0 0 1rem; }
  code { font-family: "JetBrains Mono", ui-monospace, Menlo, Consolas, monospace; font-size: 0.85em; }
  pre { margin: 0 0 1rem; padding: 0.85rem 1rem; background: var(--code-bg); border-radius: 6px;
    overflow-x: auto; line-height: 1.5; }
  pre code { font-size: 0.85rem; }
  .links { display: flex; gap: 1.5rem; flex-wrap: wrap; margin: 0; font-size: 1rem; }
  footer { border-top: 1px solid var(--rule); padding-top: 2rem; color: var(--muted); font-size: 1rem; }
  @media (max-width: 30rem) { h1 { font-size: 2.6rem; } .statement { font-size: 1.4rem; } }
</style>
</head>
<body>
<main>
  <header>
    <h1>Proofs</h1>
    <p class="intro">Elementary theorems I've formalized while learning the Lean 4 proof assistant.</p>
  </header>

{{THEOREMS}}
  <footer>
    <p>Built with <a href="https://lean-lang.org">Lean 4</a> and <a href="https://github.com/leanprover-community/mathlib4">Mathlib</a>. <a href="docs/">Browse the full API documentation</a>, including Mathlib, or see the <a href="https://github.com/KlemenKobau/proofs">repository on GitHub</a>.</p>
  </footer>
</main>
</body>
</html>
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default="Proofs", help="library folder to scan")
    ap.add_argument("--out", default="docs/index.html")
    args = ap.parse_args()
    src = Path(args.src)
    if not src.is_dir():
        sys.exit(f"error: source folder '{src}' not found (run from the repository root)")
    root = src.parent
    theorems = []
    for path in sorted(src.rglob("*.lean")):
        theorems.extend(parse_file(path, root))
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render(theorems), encoding="utf-8")
    print(f"Wrote {out} with {len(theorems)} theorem(s):")
    for t in theorems:
        print(f"  {t['name']}  ->  {t['doc_url']}")


if __name__ == "__main__":
    main()
