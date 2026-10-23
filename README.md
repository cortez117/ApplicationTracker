# Job Application Hunt Tracker

A small full-stack app for tracking job applications: FastAPI backend, SQLite storage (`job_tracker.db`, created automatically on first run), and a single-page Tailwind UI.

## Install

Requires Python 3.9+.

```bash
pip install -r requirements.txt
```

## Run

```bash
uvicorn main:app --reload
```

Then open http://127.0.0.1:8000. Interactive API docs are at http://127.0.0.1:8000/docs.

## API

| Method | Path | Description |
| --- | --- | --- |
| GET | `/api/applications` | All applications, most recently applied first |
| POST | `/api/applications` | Create an application |
| PUT | `/api/applications/{id}` | Update any subset of fields (e.g. just `status`) |
| DELETE | `/api/applications/{id}` | Delete an application |

Fields: `company_name`, `position_title`, `status` (`Applied`, `Interviewing`, `Offer`, `Rejected`), `date_applied` (`YYYY-MM-DD`), `salary_range`, `notes`.

## Files

- `main.py` – API and database setup
- `index.html` – dashboard UI (Tailwind via CDN, vanilla JS)
- `job_tracker.db` – created on first start; delete it to reset your data
