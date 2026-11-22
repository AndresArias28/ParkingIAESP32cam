# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Parking IA (P.I.A.): a working model that counts cars and motorcycles via ESP32-CAM cameras and shows available spots in Flutter. Flow: ESP32-CAM → JPEG over HTTP → Python/Flask backend → classifier (Car/Motorcycle/Empty) → counting rules → Firebase Realtime Database → Flutter.

Project docs are in Spanish; read them before changing behavior — they are the source of truth, not this file:
- `README.md` — current status and next steps (kept up to date as work progresses)
- `docs/constitution.md` — scope and fixed decisions (3 classes only, no plates/payments/reservations, inference/rules/storage stay separate)
- `docs/architecture.md` — components, contracts, identifiers, counting rules, Firebase data shape
- `docs/backend.md` — how to set up the model and run the Flask server
- `docs/firebase-and-flutter.md` — connecting Firebase, env vars, end-to-end test procedure
- `docs/esp32-every-2-seconds.md` — firmware/network setup for the entrance camera
- `docs/phases.md` — phase-by-phase progress log; **record verifiable progress here, don't mark empty folders as implemented**
- `docs/requirements.md` — requirements and acceptance criteria

## Commands

Backend (Python, from repo root `D:\parqueaderoIA`, using the venv):
```powershell
.\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt   # install deps
.\.venv\Scripts\python.exe -m backend.app.server                        # run the server (loads root .env)
.\.venv\Scripts\python.exe -m backend.camera_client                     # fetch one photo from an ESP32 /capture and classify it
.\.venv\Scripts\python.exe -m backend.check_firebase                    # read-only Firebase connectivity check (no writes)
```

Tests (unittest, no live model/Firebase required — see Testing below):
```powershell
.\.venv\Scripts\python.exe -m unittest discover -s backend\tests -v     # all backend tests
.\.venv\Scripts\python.exe -m unittest backend.tests.test_server -v     # single module
.\.venv\Scripts\python.exe -m unittest backend.tests.test_server.ServerTest.test_http_observation_counts_once -v  # single test
```

Flutter app (`movil_app/`, the recovered app — keep it here unless a task requires migrating it):
```powershell
cd movil_app
flutter analyze
flutter test
flutter run
```

## Architecture

Backend lives in `backend/app/` and is split into three independent layers (do not blur these):

- **`classifier.py` (`ImageClassifier`)** — loads the Teachable Machine Keras model from `ml/model/` (`keras_model.h5` + `labels.txt`, excluded from Git), resizes/normalizes input to the model's shape, and returns `{"prediction", "confidence"}`. `normalize_label` maps Teachable Machine's Spanish labels (Carro/Moto/Vacío, possibly prefixed `"0 Carro"`) to the internal ids `car`/`motorcycle`/`empty`. `InvalidImage` signals an unreadable upload.
- **`parking_service.py` (`ParkingService`)** — pure counting rules, called inside a Firebase transaction callback (`observe(camera, prediction, confidence, event_id, timestamp_ms)`). Enforces: confidence threshold (default 0.85), per-camera cooldown (default 2500 ms) measured between *accepted* events only, and a per-camera arm/disarm detector requiring two consecutive confident `empty` reads to re-arm before counting the next vehicle. Invariant: `0 <= occupied[kind] <= capacity[kind]` and `available[kind] = capacity[kind] - occupied[kind]`, always enforced inside `update()`. Returns `{"counted", "reason", "occupied", "available"}`; `reason` is one of `low_confidence`, `empty`, `already_seen`, `cooldown`, `capacity_limit`, `accepted`.
- **`firebase_repository.py` (`FirebaseRepository`)** — the only module touching Firebase Admin/RTDB. `transaction()` wraps the whole root node in one atomic update: it reads the legacy `config`/`estado` nodes (older app schema), seeds the new `parking` node from them, runs the caller's `update(parking)` callback, writes `parking` back, and mirrors the result back into `estado` so both the old and the recovered Flutter app stay in sync. Never update `parking` and `estado` outside this single transaction — that's how the two cameras avoid clobbering each other's counts.

`server.py` (`create_app`, `main`) wires these together as a Flask app. `main()` loads `.env` via `local_config.load_local_env()`, builds a `FirebaseRepository`-backed `ParkingService` only when `PARKING_FIREBASE_ENABLED=1`, and exposes:
- `GET /health` — model-loaded check only, not a Firebase or accuracy check.
- `POST /api/v1/predict[?camera=entrance-01|exit-01]` — accepts multipart `image` or a raw `image/jpeg` body (max 5 MB). Without `camera`, only classifies. With `camera` and an active `parking_service`, requires header `X-Camera-Token` matching `PARKING_CAMERA_TOKEN` (compared with `hmac.compare_digest`), then calls `ParkingService.observe(...)` and merges `counted`/`reason`/`occupied`/`available` into the response.

Cameras are fixed: `entrance-01` (action `in`) and `exit-01` (action `out`); see `CAMERAS`/`CAMERA_ACTION`. There is no third camera — unknown `camera` values are rejected with 400.

Config/credentials: `local_config.py` loads `D:\parqueaderoIA\.env` (not committed) with `override=False`, so variables already set in the shell session win. Relevant vars: `PARKING_FIREBASE_ENABLED`, `FIREBASE_DATABASE_URL`, `GOOGLE_APPLICATION_CREDENTIALS`, `PARKING_CAMERA_TOKEN`, `PARKING_HOST`, `PARKING_PORT`. `backend/serviceAccountKey.json` is the Firebase service account — gitignored, never touch Firebase production data from local/doc tasks.

Flutter app (`movil_app/lib/`): `main.dart` entry point, `firebase_options.dart` (gitignored, generated), `parking_station.dart` subscribes to the `parking` RTDB node and renders occupied/available/recent events. It is read-only UI — no inference or direct camera access from Flutter, per `docs/constitution.md`.

Firmware (`firmware/entrada/parking_entrada.ino` + `secrets.example.h`) captures JPEG and POSTs it to the backend every ~2s over `WIFI_STA`; `firmware/capturar-fotos/` is the older direct-AP dataset-capture sketch, kept separate. `ml/training/capture_dataset.py` is a dependency-free tool for saving labeled captures into `ml/dataset/` (gitignored, only `.gitkeep` markers tracked).

## Testing

`backend/tests/` uses stdlib `unittest` with fakes instead of the real model/Firebase:
- `test_server.py` — HTTP contract via Flask's test client, using a `FakeClassifier` and an in-memory `MemoryRepository` (a dict-backed stand-in for the Firebase transaction).
- `test_parking_service.py` / `test_firebase_repository.py` — rule and transaction-merge logic in isolation.

When changing counting rules or the Firebase schema, add cases for: confidence boundary, duplicate detection while a vehicle stays in frame, cooldown timing, capacity limits (both directions), and detector re-arm after repeated `empty` reads — per `docs/constitution.md`'s note that cooldown reduces duplicates but does not guarantee one count per vehicle.

## Working conventions (from AGENTS.md)

- Identifiers: internal code/data use `car`, `motorcycle`, `empty`; UI text uses `Carro`, `Moto`, `Vacío`.
- Work in phases and log verifiable progress in `docs/phases.md`; don't present empty/scaffolded folders as implemented features.
- Never commit passwords, tokens, private keys, or service accounts, in code, docs, or examples — see `.gitignore` for the excluded patterns (`.env`, `serviceAccount*.json`, `secrets.h`, etc.).
- Keep dataset and trained models out of Git (`ml/dataset/`, `ml/model/`) — only markers/docs are tracked.
- Don't deploy, publish, or touch real Firebase as part of local documentation tasks.
