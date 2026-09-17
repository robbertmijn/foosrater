# Foosrater

## Overview

This repository contains a Flask web application that tracks 2v2 foosball game results and displays a real-time leaderboard. Users can input game outcomes, and player rankings are updated dynamically using an Elo rating system.

---

## Features

- **Game Input:** Easily record the results of 2v2 foosball matches.
- **Leaderboard:** View a live leaderboard with player rankings.
- **Dynamic Ranking System:** Player ratings are updated after every game based on Elo system mechanics.
- **Intuitive UI:** Simple and clean interface for easy navigation and data entry.

---

## Getting Started

### Prerequisites

- Dependencies listed in `requirements.txt` (install with `pip install -r requirements.txt`)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/robbertmijn/foosrater
   cd foosrater
   ```

2. Set up the virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate   # On Windows, use `venv\Scripts\activate`
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set `DATABASE_URL` to a Supabase/Postgres connection string.

5. Run the Flask app:
   ```bash
   flask --app flask_app run
   ```
   The app will be accessible at [http://127.0.0.1:5000](http://127.0.0.1:5000).

---

## Vercel + Supabase setup

The `vercel-supabase` branch stores games in PostgreSQL instead of local CSV files so it can run on Vercel's serverless Python runtime.

### 1. Create the database table

Create a Supabase project, open the SQL editor, and run the contents of:

```text
supabase_schema.sql
```

This creates the `public.games` table and an index used to retrieve each league chronologically.

### 2. Migrate existing CSV files

Each CSV filename becomes its league name. For example, `data/hmt_2025.csv` is imported as league `hmt_2025`.

Generate SQL for one league:

```bash
python scripts/csv_to_sql.py data/hmt_2025.csv > supabase_import.sql
```

Generate one SQL file for all league CSVs:

```bash
python scripts/csv_to_sql.py data/*.csv > supabase_import.sql
```

If you are re-running an import and want to replace the existing rows for those leagues first:

```bash
python scripts/csv_to_sql.py --replace-leagues data/*.csv > supabase_import.sql
```

Inspect `supabase_import.sql`, then paste/run it in the Supabase SQL editor.

### 3. Configure the database connection

Copy a PostgreSQL connection string from Supabase and set it as:

```text
DATABASE_URL=postgresql://...
```

For Vercel, add `DATABASE_URL` as a project environment variable. A pooled Supabase connection string is recommended for serverless deployments.

### 4. Deploy on Vercel

Import this GitHub repository into Vercel and select the `vercel-supabase` branch for a preview deployment, or merge it to your production branch later. The root `app.py` exposes the Flask application to Vercel.

The QR-poster route now derives its URL from the active host, so it works with Vercel preview URLs, the production Vercel URL, or a custom domain without hard-coded PythonAnywhere URLs.

---

## Mechanics of the Elo Rating System

The outcome of each game is predicted based on the ratings of the players. A team with a higher mean rating \(R\) compared to the other team is expected to score a higher proportion of the points in a game. At the end of each game, each players' rating is updated by multiplaying the difference between their expected score \(E\) and their actual score by a constant \(K\) (64)

**Initial Ratings:** All players start with a default rating $R$ of 1000.

**Outcome:**

$$O_{\text{red team}}=\frac{\text{red goals}}{\text{red goals}+\text{blue goals}}$$

**Expected Outcome:**

$$E_{\text{red team}}=\frac{1}{1 + 10^{(R_{\text{blue team}}-R_{\text{red team}}) / 271}}$$

where $R$ is determined by the initial rating and the updating after previous games.

The new rating is updated as:

$$R_{\text{new}} = R_{\text{old}} + K \times (O - E)$$

$K$: A constant determining the magnitude of rating changes.

For example, the expected outcome of a 1100 rated team vs a 900 rated team is $\frac{1}{1 + 10^{200 / 271}} = 0.24$, meaning that the lower rated team is expected to score 24% of the total goals (i.e., about 3.16 goals, given the winning team ends at 10).

---

## Data storage

On the `vercel-supabase` branch, games are stored in the `public.games` PostgreSQL table. Elo ratings and player statistics remain derived data and are recalculated from the game history when a league page is loaded.

---

## GUI

The app retrieves games for the requested league and displays a list of games on the home page. Each time a game is added or edited (or the page is refreshed) ratings are recalculated and displayed.

---

## Contributing

1. Fork the repository.
2. Create a new branch for your feature or bugfix:
   ```bash
   git checkout -b feature-name
   ```
3. Commit your changes:
   ```bash
   git commit -m "Add feature-name"
   ```
4. Push the branch to your fork:
   ```bash
   git push origin feature-name
   ```
5. Open a Pull Request.

---

## License

This project is licensed under the [MIT License](LICENSE). Feel free to use, modify, and distribute as per the license terms.

---
