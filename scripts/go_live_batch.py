#!/usr/bin/env python
"""
go_live_batch.py

Implements the shortest operational sequence for "make everything live at once":

1) Fix snippet collisions (HUF_DIAGNOSTIC + HUF_TODO) -> keep canonical in notes/code_snippets/huf_code/
2) Consolidate staged wiki pages -> notes/wiki_pages/ and remove staged duplicates
3) Flip Advanced Math doc_id to REL + LANE:release (docs/books/advanced_mathematics/index.md)
4) Fix docs/index.md links for MkDocs strict mode
5) Re-run doc_inventory.py --write --merge
6) Optionally git add/commit

Dry-run by default.
"""

from __future__ import annotations

import argparse
import datetime as dt
import os
import re
import shutil
import subprocess
from pathlib import Path
from typing import Iterable, List, Tuple


# ----------------------------
# Config
# ----------------------------

COLLISION_DOC_IDS = [
    "HUF.DRAFT.SOFTWARE.CODE.HUF_DIAGNOSTIC",
    "HUF.DRAFT.SOFTWARE.CODE.HUF_TODO",
]

CANON_SNIPPETS = {
    "HUF.DRAFT.SOFTWARE.CODE.HUF_DIAGNOSTIC": "notes/code_snippets/huf_code/huf_diagnostic.jsx",
    "HUF.DRAFT.SOFTWARE.CODE.HUF_TODO": "notes/code_snippets/huf_code/huf_todo.jsx",
}

WIKI_STAGED_GLOB = "notes/current_documents/staged/**/wiki_*.md"
WIKI_DEST_DIR = "notes/wiki_pages"

ADV_MATH_PATH = "docs/books/advanced_mathematics/index.md"
ADV_MATH_NEW_DOC_ID = "HUF.REL.BOOK.MANUSCRIPT.ADVANCED_MATH"

DOCS_INDEX_PATH = "docs/index.md"
REPO_GH = "https://github.com/PeterHiggins19/huf_core"
REPO_BRANCH = "main"

DOC_INVENTORY = "scripts/doc_inventory.py"

PRIVATE_DUPES_DIR = "notes/_private/dupes"


# ----------------------------
# Helpers
# ----------------------------

def run(cmd: List[str], cwd: Path, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=str(cwd), check=check, text=True, capture_output=False)

def read_text(p: Path) -> str:
    return p.read_text(encoding="utf-8", errors="replace")

def write_text(p: Path, s: str, apply: bool) -> None:
    if apply:
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(s, encoding="utf-8", newline="\n")

def ensure_dir(p: Path, apply: bool) -> None:
    if apply:
        p.mkdir(parents=True, exist_ok=True)

def ts() -> str:
    return dt.datetime.now().strftime("%Y%m%d_%H%M%S")

def scan_for_doc_id(root: Path, doc_id: str, exts: Iterable[str]) -> List[Path]:
    hits: List[Path] = []
    pattern = re.compile(re.escape(doc_id))
    for dirpath, dirnames, filenames in os.walk(root):
        d = Path(dirpath)
        # skip heavy dirs
        dirnames[:] = [n for n in dirnames if n not in {".git", ".venv", "site", "out", "node_modules", "__pycache__"}]
        for fn in filenames:
            p = d / fn
            if p.suffix.lower() not in exts:
                continue
            try:
                head = "\n".join(read_text(p).splitlines()[:160])
            except Exception:
                continue
            if "HUF-DOC:" in head and pattern.search(head):
                hits.append(p)
    return sorted(hits)

def move_to_private(p: Path, private_dir: Path, apply: bool) -> Path:
    private_dir.mkdir(parents=True, exist_ok=True)
    dst = private_dir / f"{p.stem}__dupe__{ts()}{p.suffix}"
    if apply:
        shutil.move(str(p), str(dst))
    return dst

def remove_empty_parents(start: Path, stop: Path, apply: bool) -> None:
    """
    Remove empty directories upward from start until stop (exclusive).
    """
    cur = start
    while cur != stop and cur.exists():
        try:
            if any(cur.iterdir()):
                return
            if apply:
                cur.rmdir()
        except Exception:
            return
        cur = cur.parent

def replace_header_doc_id_and_lane(text: str, new_doc_id: str) -> str:
    """
    Rewrites the HUF-DOC line doc_id and enforces LANE:release for Advanced Math.
    """
    lines = text.splitlines()
    out = lines[:]

    # Find HUF-DOC line in first ~80 lines
    idx = None
    for i, ln in enumerate(out[:120]):
        if "HUF-DOC:" in ln:
            idx = i
            break
    if idx is None:
        return text

    ln = out[idx]

    # Replace doc_id immediately after "HUF-DOC:"
    # Example: "HUF-DOC: HUF.DRAFT.... | HUF:... | ..."
    ln2 = re.sub(r"(HUF-DOC:\s*)([^|]+)", r"\1" + new_doc_id + " ", ln)

    # Force LANE:release (keep status as-is)
    if "LANE:" in ln2:
        ln2 = re.sub(r"LANE:\s*[^|]+", "LANE:release", ln2)
    else:
        ln2 = ln2.rstrip() + " | LANE:release"

    out[idx] = ln2
    return "\n".join(out) + ("\n" if text.endswith("\n") else "")

def fix_docs_index_links(text: str) -> str:
    """
    Fixes strict-mode link targets in docs/index.md:
    - Removes 'docs/' prefix inside markdown link targets
    - Rewrites repo-root non-doc links to external GitHub URLs
    - Rewrites docs/cases.md -> partners/case_studies/index.md
    """
    # 1) Remove docs/ prefix in markdown links: (docs/foo.md) -> (foo.md)
    text = re.sub(r"\((?:\./)?docs/([^)]+)\)", r"(\1)", text)

    # 2) docs/cases.md is obsolete -> partners/case_studies/index.md
    text = text.replace("(cases.md)", "(partners/case_studies/index.md)")
    text = text.replace("(docs/cases.md)", "(partners/case_studies/index.md)")

    # 3) START_HERE_* scripts: convert to GitHub URLs
    start_map = {
        "START_HERE_WINDOWS.bat": f"{REPO_GH}/blob/{REPO_BRANCH}/START_HERE_WINDOWS.bat",
        "START_HERE_MAC.command": f"{REPO_GH}/blob/{REPO_BRANCH}/START_HERE_MAC.command",
        "start_here_linux.sh": f"{REPO_GH}/blob/{REPO_BRANCH}/start_here_linux.sh",
        "scripts/fetch_data.py": f"{REPO_GH}/blob/{REPO_BRANCH}/scripts/fetch_data.py",
        "scripts/bootstrap.py": f"{REPO_GH}/blob/{REPO_BRANCH}/scripts/bootstrap.py",
    }

    # Replace markdown link targets that point to those files
    for local, url in start_map.items():
        text = text.replace(f"({local})", f"({url})")

    return text

def ensure_private_gitignore(repo: Path, apply: bool) -> None:
    """
    Ensures notes/_private is gitignored. (Safe append)
    """
    gi = repo / ".gitignore"
    if not gi.exists():
        return
    s = read_text(gi)
    needed = ["notes/_private/", "notes/_private/**"]
    if all(x in s for x in needed):
        return
    add = "\n# --- HUF local-only management (do not commit) ---\nnotes/_private/\nnotes/_private/**\n"
    if apply:
        write_text(gi, s.rstrip() + add + "\n", apply=True)


# ----------------------------
# Main sequence
# ----------------------------

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=".", help="Repo root")
    ap.add_argument("--apply", action="store_true", help="Apply changes (default dry-run)")
    ap.add_argument("--commit", action="store_true", help="Commit changes as one go-live batch")
    ap.add_argument("--message", default="Go-live: resolve collisions + consolidate wiki + books/learning live", help="Commit message")
    args = ap.parse_args()

    repo = Path(args.repo).resolve()
    apply = args.apply

    print(f"[go_live_batch] repo={repo}")
    print(f"[go_live_batch] mode={'APPLY' if apply else 'DRY-RUN'}")

    # 0) Ensure notes/_private is gitignored (recommended)
    ensure_private_gitignore(repo, apply)

    # 1) Fix snippet collisions
    print("\n[1/5] Fix snippet collisions...")
    private_dupes = repo / PRIVATE_DUPES_DIR
    ensure_dir(private_dupes, apply)

    for doc_id in COLLISION_DOC_IDS:
        canon_rel = CANON_SNIPPETS.get(doc_id)
        if not canon_rel:
            print(f"  - skip {doc_id}: no canonical mapping")
            continue

        canon = repo / canon_rel
        if not canon.exists():
            print(f"  - WARNING: canonical missing for {doc_id}: {canon_rel}")
            continue

        hits = scan_for_doc_id(repo, doc_id, exts={".jsx", ".js", ".ts", ".tsx", ".md", ".txt"})
        # Keep canonical, move others to _private
        for h in hits:
            if h.resolve() == canon.resolve():
                continue
            dst = move_to_private(h, private_dupes, apply)
            print(f"  - moved duplicate -> {dst.relative_to(repo)} (from {h.relative_to(repo)})")
            # remove empty staged parent dirs if applicable
            if "notes/current_documents/staged" in h.as_posix():
                remove_empty_parents(h.parent, repo, apply)

    # 2) Consolidate staged wiki pages into notes/wiki_pages
    print("\n[2/5] Consolidate staged wiki pages...")
    dest_dir = repo / WIKI_DEST_DIR
    ensure_dir(dest_dir, apply)

    staged_wiki = sorted(repo.glob(WIKI_STAGED_GLOB))
    if not staged_wiki:
        print("  - no staged wiki pages found (ok)")
    for p in staged_wiki:
        target = dest_dir / p.name
        print(f"  - promote {p.relative_to(repo)} -> {target.relative_to(repo)}")
        if apply:
            shutil.copy2(p, target)
            # then move original staged file to _private (trail) and remove staged dir
            _ = move_to_private(p, private_dupes, apply=True)
            remove_empty_parents(p.parent, repo, apply=True)

    # 3) Flip Advanced Math doc_id to REL and lane release
    print("\n[3/5] Flip Advanced Math doc_id to REL...")
    adv_path = repo / ADV_MATH_PATH
    if adv_path.exists():
        adv_text = read_text(adv_path)
        adv_new = replace_header_doc_id_and_lane(adv_text, ADV_MATH_NEW_DOC_ID)
        if adv_new != adv_text:
            print(f"  - updated header in {ADV_MATH_PATH}")
            write_text(adv_path, adv_new, apply)
        else:
            print("  - no change needed (already REL?)")
    else:
        print(f"  - WARNING: missing {ADV_MATH_PATH}")

    # 4) Fix docs/index.md links for strict mode
    print("\n[4/5] Fix docs/index.md links for strict mode...")
    idx_path = repo / DOCS_INDEX_PATH
    if idx_path.exists():
        idx_text = read_text(idx_path)
        idx_new = fix_docs_index_links(idx_text)
        if idx_new != idx_text:
            print(f"  - updated links in {DOCS_INDEX_PATH}")
            write_text(idx_path, idx_new, apply)
        else:
            print("  - no link changes needed")
    else:
        print(f"  - WARNING: missing {DOCS_INDEX_PATH}")

    # 5) Re-run inventory (doc_inventory.py --write --merge)
    print("\n[5/5] Re-run doc inventory...")
    inv = repo / DOC_INVENTORY
    if inv.exists():
        cmd = [str((repo / ".venv" / "Scripts" / "python.exe").as_posix())] if (repo / ".venv" / "Scripts" / "python.exe").exists() else [os.sys.executable]
        cmd += [str(inv), "--root", ".", "--write", "--merge"]
        print("  - running:", " ".join(cmd))
        if apply:
            run(cmd, cwd=repo, check=True)
    else:
        print(f"  - WARNING: {DOC_INVENTORY} not found; skip inventory run")

    # Optional commit
    if args.commit:
        print("\n[commit] git add/commit...")
        if apply:
            run(["git", "add", "-A"], cwd=repo, check=True)
            # show status
            run(["git", "status"], cwd=repo, check=True)
            run(["git", "commit", "-m", args.message], cwd=repo, check=True)
            print("[commit] done. Next: git push")
        else:
            print("  - dry-run: would run git add -A && git commit")
    else:
        print("\n[commit] skipped (pass --commit to commit as one batch)")

    print("\nDone.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())