# DEYE Operational Forms App

This repository is a minimal Next.js + Tailwind application that consolidates three operational forms (Repairing, Inward Tracking, Outward Tracking) into a single interface with a small Node.js backend that stores submissions in PostgreSQL and can export CSVs.

Features
- Single-page interface with tabs for each form
- Client-side validation on required fields
- Backend API to save submissions into PostgreSQL
- Duplicate submission prevention (SHA256 hash of payload)
- Admin API and UI protected by `ADMIN_TOKEN` to view records and export CSVs

Getting started

1) Install dependencies

```powershell
cd "c:\Users\Yashraj\Desktop\Deye Web App Project"
npm install
```

2) Configure environment

Create a `.env.local` file in the project root with the following:

```
DATABASE_URL=postgresql://user:password@localhost:5432/deye_forms
ADMIN_TOKEN=some-strong-token
```

3) Prepare the database

Run the SQL in `db/schema.sql` against your PostgreSQL instance, or let the server initialize the table on first write (the app attempts to create the table automatically).

4) Run the app

```powershell
npm run dev
```

Open `http://localhost:3000` to use the forms. Admin UI is at `http://localhost:3000/admin` — supply the `ADMIN_TOKEN` to load records and export CSV.

Notes & next steps
- This scaffold focuses on the requested feature set and is intentionally minimal. For production use:
  - Add proper authentication for the admin UI (OAuth / sessions)
  - Add server-side validation and stricter schema mapping
  - Add paginated listing and richer filters for admin
  - Add file uploads and signature capture (canvas) implementation

If you want, I can:
- Wire up Docker Compose with Postgres
- Add Prisma for schema migrations and type-safe DB access
- Implement signature capture and file uploads
