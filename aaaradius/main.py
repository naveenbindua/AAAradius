from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from aaaradius.db import get_connection, init_db, seed_demo_data
from aaaradius.radius_auth import authenticate

TEMPLATES = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))

app = FastAPI(title="AAAradiusPanel", version="0.1.0")


@app.on_event("startup")
def on_startup() -> None:
    init_db()
    seed_demo_data()


class AuthRequest(BaseModel):
    username: str
    password: str
    nas_name: str


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/auth")
def api_auth(payload: AuthRequest) -> dict[str, object]:
    result = authenticate(payload.username, payload.password, payload.nas_name)
    return {
        "success": result.success,
        "message": result.message,
        "packet": "Access-Accept" if result.success else "Access-Reject",
    }


@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request):
    with get_connection() as conn:
        stats = {
            "users": conn.execute("SELECT COUNT(*) FROM users").fetchone()[0],
            "clients": conn.execute("SELECT COUNT(*) FROM nas_clients").fetchone()[0],
            "accepts": conn.execute(
                "SELECT COUNT(*) FROM auth_logs WHERE success = 1"
            ).fetchone()[0],
            "rejects": conn.execute(
                "SELECT COUNT(*) FROM auth_logs WHERE success = 0"
            ).fetchone()[0],
        }
        logs = conn.execute(
            """
            SELECT username, nas_name, success, message, created_at
            FROM auth_logs
            ORDER BY id DESC
            LIMIT 10
            """
        ).fetchall()
    return TEMPLATES.TemplateResponse(
        request,
        "dashboard.html",
        {"stats": stats, "logs": logs},
    )


@app.get("/users", response_class=HTMLResponse)
def users_page(request: Request):
    with get_connection() as conn:
        users = conn.execute(
            "SELECT id, username, enabled, created_at FROM users ORDER BY id"
        ).fetchall()
    return TEMPLATES.TemplateResponse(request, "users.html", {"users": users})


@app.post("/users")
def create_user(username: str = Form(...), password: str = Form(...)):
    with get_connection() as conn:
        try:
            conn.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                (username.strip(), password),
            )
            conn.commit()
        except Exception as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
    return RedirectResponse("/users", status_code=303)


@app.post("/users/{user_id}/delete")
def delete_user(user_id: int):
    with get_connection() as conn:
        conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()
    return RedirectResponse("/users", status_code=303)


@app.get("/clients", response_class=HTMLResponse)
def clients_page(request: Request):
    with get_connection() as conn:
        clients = conn.execute(
            "SELECT id, name, ip_address, enabled, created_at FROM nas_clients ORDER BY id"
        ).fetchall()
    return TEMPLATES.TemplateResponse(request, "clients.html", {"clients": clients})


@app.post("/clients")
def create_client(
    name: str = Form(...),
    ip_address: str = Form(...),
    secret: str = Form(...),
):
    with get_connection() as conn:
        try:
            conn.execute(
                "INSERT INTO nas_clients (name, ip_address, secret) VALUES (?, ?, ?)",
                (name.strip(), ip_address.strip(), secret),
            )
            conn.commit()
        except Exception as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
    return RedirectResponse("/clients", status_code=303)


@app.post("/clients/{client_id}/delete")
def delete_client(client_id: int):
    with get_connection() as conn:
        conn.execute("DELETE FROM nas_clients WHERE id = ?", (client_id,))
        conn.commit()
    return RedirectResponse("/clients", status_code=303)


@app.get("/test-auth", response_class=HTMLResponse)
def test_auth_page(request: Request):
    with get_connection() as conn:
        users = conn.execute("SELECT username FROM users ORDER BY username").fetchall()
        clients = conn.execute("SELECT name FROM nas_clients ORDER BY name").fetchall()
    return TEMPLATES.TemplateResponse(
        request,
        "test_auth.html",
        {"users": users, "clients": clients, "result": None},
    )


@app.post("/test-auth", response_class=HTMLResponse)
def test_auth_submit(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    nas_name: str = Form(...),
):
    result = authenticate(username, password, nas_name)
    with get_connection() as conn:
        users = conn.execute("SELECT username FROM users ORDER BY username").fetchall()
        clients = conn.execute("SELECT name FROM nas_clients ORDER BY name").fetchall()
    return TEMPLATES.TemplateResponse(
        request,
        "test_auth.html",
        {
            "users": users,
            "clients": clients,
            "result": result,
            "submitted": {"username": username, "nas_name": nas_name},
        },
    )
