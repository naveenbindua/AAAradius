from __future__ import annotations

from dataclasses import dataclass

from aaaradius.db import get_connection


@dataclass
class AuthResult:
    success: bool
    message: str


def authenticate(username: str, password: str, nas_name: str) -> AuthResult:
    with get_connection() as conn:
        nas = conn.execute(
            "SELECT name, enabled FROM nas_clients WHERE name = ?",
            (nas_name,),
        ).fetchone()
        if nas is None:
            result = AuthResult(False, "Unknown NAS client")
        elif not nas["enabled"]:
            result = AuthResult(False, "NAS client disabled")
        else:
            user = conn.execute(
                "SELECT username, password, enabled FROM users WHERE username = ?",
                (username,),
            ).fetchone()
            if user is None:
                result = AuthResult(False, "Unknown user")
            elif not user["enabled"]:
                result = AuthResult(False, "User disabled")
            elif user["password"] != password:
                result = AuthResult(False, "Invalid password")
            else:
                result = AuthResult(True, "Access-Accept")

        conn.execute(
            """
            INSERT INTO auth_logs (username, nas_name, success, message)
            VALUES (?, ?, ?, ?)
            """,
            (username, nas_name, int(result.success), result.message),
        )
        conn.commit()
        return result
