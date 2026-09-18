# AAAradius

AAAradiusPanel is a lightweight web panel for managing RADIUS AAA users and NAS clients.

## Prerequisites

- Python 3.12+

## Development

Install dependencies:

```bash
bash .cursor/scripts/install.sh
```

Initialize the database and start the panel:

```bash
bash .cursor/scripts/start.sh
bash .cursor/scripts/run-panel.sh
```

The panel runs at http://localhost:8080.

Demo credentials:

- User: `demo` / `radius123`
- NAS client: `office-wifi`

## Tests

```bash
. .venv/bin/activate
pytest -q
```

## API

`POST /api/auth`

```json
{
  "username": "demo",
  "password": "radius123",
  "nas_name": "office-wifi"
}
```

Returns `Access-Accept` or `Access-Reject`.
