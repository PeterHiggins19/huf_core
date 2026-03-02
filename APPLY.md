# Auto-generated current documents catalog

Adds:
- scripts/generate_current_documents_catalog.py
- notes/_org/current_documents_catalog_README.md

Run (dry-run):
```powershell
.\.venv\Scripts\python scripts\generate_current_documents_catalog.py
```

Write outputs:
```powershell
.\.venv\Scripts\python scripts\generate_current_documents_catalog.py --write
```

Fail non-zero if any orphans (optional gate):
```powershell
.\.venv\Scripts\python scripts\generate_current_documents_catalog.py --write --fail-on-orphans
```

Then:
```powershell
.\.venv\Scripts\python -m mkdocs build --strict
```

Add to mkdocs.yml nav (suggested under Books or Documentation):
- Current documents (authoritative): current_documents.md
