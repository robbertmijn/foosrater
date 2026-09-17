import os

import psycopg
from psycopg.rows import dict_row


class PostgresStorage:
    """Small persistence layer for the games table in Supabase/Postgres."""

    def __init__(self, database_url=None):
        self.database_url = database_url or os.environ.get("DATABASE_URL")

    def _connect(self):
        if not self.database_url:
            raise RuntimeError(
                "DATABASE_URL is not set. Use the Supabase Postgres connection "
                "string (preferably the transaction pooler URL on Vercel)."
            )

        # Disable automatic prepared statements for compatibility with
        # transaction-pooling setups such as Supabase's pooler.
        return psycopg.connect(
            self.database_url,
            autocommit=True,
            row_factory=dict_row,
            prepare_threshold=None,
        )

    def list_games(self, league_name):
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, league_name, r1, r2, b1, b2,
                           red_score, blue_score, date_time
                    FROM public.games
                    WHERE league_name = %s
                    ORDER BY date_time, id
                    """,
                    (league_name,),
                )
                return cur.fetchall()

    def add_game(
        self,
        league_name,
        r1,
        r2,
        b1,
        b2,
        red_score,
        blue_score,
        date_time,
    ):
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO public.games
                        (league_name, r1, r2, b1, b2,
                         red_score, blue_score, date_time)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                    """,
                    (
                        league_name,
                        r1,
                        r2,
                        b1,
                        b2,
                        int(red_score),
                        int(blue_score),
                        date_time,
                    ),
                )
                return cur.fetchone()["id"]

    def update_game(
        self,
        game_id,
        league_name,
        r1,
        r2,
        b1,
        b2,
        red_score,
        blue_score,
        date_time,
    ):
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE public.games
                    SET r1 = %s,
                        r2 = %s,
                        b1 = %s,
                        b2 = %s,
                        red_score = %s,
                        blue_score = %s,
                        date_time = %s
                    WHERE id = %s AND league_name = %s
                    """,
                    (
                        r1,
                        r2,
                        b1,
                        b2,
                        int(red_score),
                        int(blue_score),
                        date_time,
                        game_id,
                        league_name,
                    ),
                )
                if cur.rowcount != 1:
                    raise LookupError(
                        f"Game {game_id} was not found in league {league_name!r}."
                    )

    def delete_game(self, game_id, league_name):
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    DELETE FROM public.games
                    WHERE id = %s AND league_name = %s
                    """,
                    (game_id, league_name),
                )
                if cur.rowcount != 1:
                    raise LookupError(
                        f"Game {game_id} was not found in league {league_name!r}."
                    )
