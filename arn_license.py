# ARN Konsumenttvist MCP
# Copyright (c) 2026 Kim Andreas Hawaleska
# All rights reserved.
# Proprietary software. Unauthorized copying, modification,
# redistribution, or commercial use is prohibited without permission.
# Contact: hawaleska@gmail.com

from pathlib import Path
import sqlite3
import hashlib
import secrets
from datetime import datetime, timezone


DB_PATH = Path(__file__).with_name("arn_license.db")

FREE_SEARCHES = 10


class LicenseManager:
    def __init__(self, db_path=DB_PATH):
        self.db_path = Path(db_path)
        self._init_db()

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    user_id TEXT PRIMARY KEY,
                    api_key_hash TEXT UNIQUE,
                    searches_used INTEGER NOT NULL DEFAULT 0,
                    paid INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS subscriptions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    paypal_subscription_id TEXT UNIQUE,
                    plan TEXT NOT NULL,
                    status TEXT NOT NULL,
                    amount_sek INTEGER NOT NULL,
                    started_at TEXT,
                    expires_at TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
                """
            )

            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_subscriptions_user_id "
                "ON subscriptions(user_id)"
            )

            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_subscriptions_paypal_id "
                "ON subscriptions(paypal_subscription_id)"
            )

            conn.commit()

    @staticmethod
    def _hash_api_key(api_key: str) -> str:
        return hashlib.sha256(
            api_key.encode("utf-8")
        ).hexdigest()


    def create_api_key(self, user_id: str) -> str:
        user_id = user_id.strip()

        if not user_id:
            raise ValueError("user_id krävs.")

        api_key = "arn_" + secrets.token_urlsafe(32)
        api_key_hash = self._hash_api_key(api_key)
        now = datetime.now(timezone.utc).isoformat()

        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO users
                (user_id, api_key_hash, searches_used, paid, created_at, updated_at)
                VALUES (?, ?, 0, 0, ?, ?)
                ON CONFLICT(user_id)
                DO UPDATE SET
                    api_key_hash = excluded.api_key_hash,
                    updated_at = excluded.updated_at
                """,
                (user_id, api_key_hash, now, now),
            )
            conn.commit()

        return api_key


    def user_id_from_api_key(self, api_key: str) -> str:
        api_key = api_key.strip()

        if not api_key:
            raise ValueError("api_key krävs.")

        api_key_hash = self._hash_api_key(api_key)

        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT user_id
                FROM users
                WHERE api_key_hash = ?
                """,
                (api_key_hash,),
            ).fetchone()

        if row is None:
            raise ValueError("Ogiltig API-nyckel.")

        return row[0]


    def check_api_key(self, api_key: str) -> dict:
        user_id = self.user_id_from_api_key(api_key)
        return self.check(user_id)


    def consume_api_key(self, api_key: str) -> dict:
        user_id = self.user_id_from_api_key(api_key)
        return self.consume(user_id)


    def activate_paid_api_key(self, api_key: str):
        user_id = self.user_id_from_api_key(api_key)
        self.activate_paid(user_id)


    def check(self, user_id: str) -> dict:
        user_id = user_id.strip()

        if not user_id:
            raise ValueError("user_id krävs.")

        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT searches_used, paid
                FROM users
                WHERE user_id = ?
                """,
                (user_id,),
            ).fetchone()

        if row is None:
            return {
                "allowed": True,
                "user_id": user_id,
                "searches_used": 0,
                "free_searches": FREE_SEARCHES,
                "remaining": FREE_SEARCHES,
                "paid": False,
            }

        searches_used, paid = row

        if paid:
            return {
                "allowed": True,
                "user_id": user_id,
                "searches_used": searches_used,
                "free_searches": FREE_SEARCHES,
                "remaining": None,
                "paid": True,
            }

        if searches_used >= FREE_SEARCHES:
            return {
                "allowed": False,
                "user_id": user_id,
                "searches_used": searches_used,
                "free_searches": FREE_SEARCHES,
                "remaining": 0,
                "paid": False,
                "payment_required": True,
            }

        return {
            "allowed": True,
            "user_id": user_id,
            "searches_used": searches_used,
            "free_searches": FREE_SEARCHES,
            "remaining": FREE_SEARCHES - searches_used,
            "paid": False,
        }


    def consume(self, user_id: str) -> dict:
        user_id = user_id.strip()

        if not user_id:
            raise ValueError("user_id krävs.")

        now = datetime.now(timezone.utc).isoformat()

        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT searches_used, paid
                FROM users
                WHERE user_id = ?
                """,
                (user_id,),
            ).fetchone()

            if row is None:
                conn.execute(
                    """
                    INSERT INTO users
                    (user_id, searches_used, paid, created_at, updated_at)
                    VALUES (?, 1, 0, ?, ?)
                    """,
                    (user_id, now, now),
                )
                conn.commit()

                return {
                    "allowed": True,
                    "user_id": user_id,
                    "searches_used": 1,
                    "free_searches": FREE_SEARCHES,
                    "remaining": FREE_SEARCHES - 1,
                    "paid": False,
                }

            searches_used, paid = row

            if not paid:
                cursor = conn.execute(
                    """
                    UPDATE users
                    SET searches_used = searches_used + 1,
                        updated_at = ?
                    WHERE user_id = ?
                      AND searches_used < ?
                      AND paid = 0
                    """,
                    (now, user_id, FREE_SEARCHES),
                )

                if cursor.rowcount == 0:
                    return {
                        "allowed": False,
                        "user_id": user_id,
                        "searches_used": searches_used,
                        "free_searches": FREE_SEARCHES,
                        "remaining": 0,
                        "paid": False,
                        "payment_required": True,
                    }

                conn.commit()

                new_count = searches_used + 1

                return {
                    "allowed": True,
                    "user_id": user_id,
                    "searches_used": new_count,
                    "free_searches": FREE_SEARCHES,
                    "remaining": FREE_SEARCHES - new_count,
                    "paid": False,
                }

            conn.execute(
                """
                UPDATE users
                SET searches_used = searches_used + 1,
                    updated_at = ?
                WHERE user_id = ?
                """,
                (now, user_id),
            )
            conn.commit()

            new_count = searches_used + 1

            return {
                "allowed": True,
                "user_id": user_id,
                "searches_used": new_count,
                "free_searches": FREE_SEARCHES,
                "remaining": None,
                "paid": True,
            }


    def check_and_consume(self, user_id: str) -> dict:
        status = self.check(user_id)

        if not status["allowed"]:
            return status

        return self.consume(user_id)
        user_id = user_id.strip()

        if not user_id:
            raise ValueError("user_id krävs.")

        now = datetime.now(timezone.utc).isoformat()

        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT searches_used, paid
                FROM users
                WHERE user_id = ?
                """,
                (user_id,),
            ).fetchone()

            if row is None:
                conn.execute(
                    """
                    INSERT INTO users
                    (user_id, searches_used, paid, created_at, updated_at)
                    VALUES (?, 1, 0, ?, ?)
                    """,
                    (user_id, now, now),
                )
                conn.commit()

                return {
                    "allowed": True,
                    "user_id": user_id,
                    "searches_used": 1,
                    "free_searches": FREE_SEARCHES,
                    "remaining": FREE_SEARCHES - 1,
                    "paid": False,
                }

            searches_used, paid = row

            if paid:
                conn.execute(
                    """
                    UPDATE users
                    SET searches_used = searches_used + 1,
                        updated_at = ?
                    WHERE user_id = ?
                    """,
                    (now, user_id),
                )
                conn.commit()

                return {
                    "allowed": True,
                    "user_id": user_id,
                    "searches_used": searches_used + 1,
                    "free_searches": FREE_SEARCHES,
                    "remaining": None,
                    "paid": True,
                }

            if searches_used >= FREE_SEARCHES:
                return {
                    "allowed": False,
                    "user_id": user_id,
                    "searches_used": searches_used,
                    "free_searches": FREE_SEARCHES,
                    "remaining": 0,
                    "paid": False,
                    "payment_required": True,
                }

            conn.execute(
                """
                UPDATE users
                SET searches_used = searches_used + 1,
                    updated_at = ?
                WHERE user_id = ?
                """,
                (now, user_id),
            )
            conn.commit()

            new_count = searches_used + 1

            return {
                "allowed": True,
                "user_id": user_id,
                "searches_used": new_count,
                "free_searches": FREE_SEARCHES,
                "remaining": FREE_SEARCHES - new_count,
                "paid": False,
            }

    def create_subscription(
        self,
        user_id: str,
        paypal_subscription_id: str,
        plan: str,
        amount_sek: int,
        status: str = "ACTIVE",
        started_at: str | None = None,
        expires_at: str | None = None,
    ):
        user_id = user_id.strip()
        paypal_subscription_id = paypal_subscription_id.strip()
        plan = plan.strip()
        status = status.strip()

        if not user_id:
            raise ValueError("user_id krävs.")
        if not paypal_subscription_id:
            raise ValueError("paypal_subscription_id krävs.")
        if not plan:
            raise ValueError("plan krävs.")
        if amount_sek <= 0:
            raise ValueError("amount_sek måste vara större än 0.")

        now = datetime.now(timezone.utc).isoformat()

        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO subscriptions
                (
                    user_id,
                    paypal_subscription_id,
                    plan,
                    status,
                    amount_sek,
                    started_at,
                    expires_at,
                    created_at,
                    updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(paypal_subscription_id)
                DO UPDATE SET
                    status = excluded.status,
                    plan = excluded.plan,
                    amount_sek = excluded.amount_sek,
                    started_at = excluded.started_at,
                    expires_at = excluded.expires_at,
                    updated_at = excluded.updated_at
                """,
                (
                    user_id,
                    paypal_subscription_id,
                    plan,
                    status,
                    amount_sek,
                    started_at,
                    expires_at,
                    now,
                    now,
                ),
            )

            conn.commit()

    def update_subscription_status(
        self,
        paypal_subscription_id: str,
        status: str,
        expires_at: str | None = None,
    ):
        paypal_subscription_id = paypal_subscription_id.strip()
        status = status.strip()

        if not paypal_subscription_id:
            raise ValueError("paypal_subscription_id krävs.")
        if not status:
            raise ValueError("status krävs.")

        now = datetime.now(timezone.utc).isoformat()

        with self._connect() as conn:
            conn.execute(
                """
                UPDATE subscriptions
                SET
                    status = ?,
                    expires_at = COALESCE(?, expires_at),
                    updated_at = ?
                WHERE paypal_subscription_id = ?
                """,
                (
                    status,
                    expires_at,
                    now,
                    paypal_subscription_id,
                ),
            )

            conn.commit()

    def get_subscription(self, user_id: str):
        user_id = user_id.strip()

        if not user_id:
            raise ValueError("user_id krävs.")

        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT
                    id,
                    user_id,
                    paypal_subscription_id,
                    plan,
                    status,
                    amount_sek,
                    started_at,
                    expires_at,
                    created_at,
                    updated_at
                FROM subscriptions
                WHERE user_id = ?
                ORDER BY id DESC
                LIMIT 1
                """,
                (user_id,),
            ).fetchone()

        if row is None:
            return None

        columns = [
            "id",
            "user_id",
            "paypal_subscription_id",
            "plan",
            "status",
            "amount_sek",
            "started_at",
            "expires_at",
            "created_at",
            "updated_at",
        ]

        return dict(zip(columns, row))

    def get_subscription_by_paypal_id(self, paypal_subscription_id: str):
        paypal_subscription_id = paypal_subscription_id.strip()

        if not paypal_subscription_id:
            raise ValueError("paypal_subscription_id krävs.")

        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT
                    id,
                    user_id,
                    paypal_subscription_id,
                    plan,
                    status,
                    amount_sek,
                    started_at,
                    expires_at,
                    created_at,
                    updated_at
                FROM subscriptions
                WHERE paypal_subscription_id = ?
                LIMIT 1
                """,
                (paypal_subscription_id,),
            ).fetchone()

        if row is None:
            return None

        columns = [
            "id",
            "user_id",
            "paypal_subscription_id",
            "plan",
            "status",
            "amount_sek",
            "started_at",
            "expires_at",
            "created_at",
            "updated_at",
        ]

        return dict(zip(columns, row))


    def get_active_subscription(self, user_id: str):
        user_id = user_id.strip()

        if not user_id:
            raise ValueError("user_id krävs.")

        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT
                    id,
                    user_id,
                    paypal_subscription_id,
                    plan,
                    status,
                    amount_sek,
                    started_at,
                    expires_at,
                    created_at,
                    updated_at
                FROM subscriptions
                WHERE user_id = ?
                  AND status IN ('ACTIVE', 'APPROVED', 'CANCEL_REQUESTED')
                ORDER BY id DESC
                LIMIT 1
                """,
                (user_id,),
            ).fetchone()

        if row is None:
            return None

        columns = [
            "id",
            "user_id",
            "paypal_subscription_id",
            "plan",
            "status",
            "amount_sek",
            "started_at",
            "expires_at",
            "created_at",
            "updated_at",
        ]

        return dict(zip(columns, row))


    def mark_subscription_cancel_requested(
        self,
        paypal_subscription_id: str,
    ):
        paypal_subscription_id = paypal_subscription_id.strip()

        if not paypal_subscription_id:
            raise ValueError("paypal_subscription_id krävs.")

        now = datetime.now(timezone.utc).isoformat()

        with self._connect() as conn:
            conn.execute(
                """
                UPDATE subscriptions
                SET
                    status = 'CANCEL_REQUESTED',
                    updated_at = ?
                WHERE paypal_subscription_id = ?
                """,
                (
                    now,
                    paypal_subscription_id,
                ),
            )
            conn.commit()


    def deactivate_paid(self, user_id: str):
        user_id = user_id.strip()

        if not user_id:
            raise ValueError("user_id krävs.")

        now = datetime.now(timezone.utc).isoformat()

        with self._connect() as conn:
            conn.execute(
                """
                UPDATE users
                SET paid = 0,
                    updated_at = ?
                WHERE user_id = ?
                """,
                (now, user_id),
            )
            conn.commit()


    def activate_paid(self, user_id: str):
        user_id = user_id.strip()

        if not user_id:
            raise ValueError("user_id krävs.")

        now = datetime.now(timezone.utc).isoformat()

        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO users
                (user_id, searches_used, paid, created_at, updated_at)
                VALUES (?, 0, 1, ?, ?)
                ON CONFLICT(user_id)
                DO UPDATE SET
                    paid = 1,
                    updated_at = excluded.updated_at
                """,
                (user_id, now, now),
            )
            conn.commit()
