# Application check — 16 October 2026

Preserved the interface, local model endpoints, port 8053 and 500 MB upload setting.

## Corrections

- Extract Word table cells in document order instead of omitting tables.
- Extract scanned pages in mixed text/scanned PDFs; close PDF rendering handles.
- Explain password-protected PDFs instead of showing an uncaught reader exception.
- Show file-specific upload errors and skip unreadable or empty files.
- Keep model errors visible instead of immediately clearing them on rerun.
- Preserve empty Word export table cells and avoid duplicating the final row.
- Reset temporary conversation history when starting a chat with newly selected documents.
- Validate the bcrypt password length rather than crashing on long passwords.
- Align the fallback database port with the configured port 5543.
- Exclude PostgreSQL runtime data and logs from Docker builds.

## Validation

- 10 automated regression tests passed: `python -m unittest discover -s tests -v`.
- Python compilation and `pip check` passed.
- Both theme pages and permanent/temporary Vault navigation passed Streamlit AppTest checks.
- Live LAN models passed embedding, retrieval, chat, and vision OCR checks.
- Database document/chat create, read, ownership, and delete checks passed in a rolled-back transaction.
- Admin data queries passed; local database readiness script passed.
- Live app health endpoint returned HTTP 200.

## Limits of the check

No actual 500 MB upload/load test or Docker build was run. Page tests are programmatic,
not a browser visual audit. The hidden OCR export functions were tested; the hidden
admin controls remain demo controls. Retrieval still selects up to 10 passages, so a
whole-report overview can omit details. Large temporary-chat contexts remain subject
to the model's context limit. A 500 MB upload setting does not guarantee that every
500 MB document can be processed within available RAM or model limits.

The source archive excludes the virtual environment, private .env, uploaded documents,
database contents and vector indexes. Use .env.example for configuration on a fresh
installation. This Windows installation uses its existing initialized PostgreSQL data
directory; the Docker Compose option initializes its own database.
