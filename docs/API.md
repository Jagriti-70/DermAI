# Flask API

Base URL for local development: `http://127.0.0.1:5000`

## `GET /api/health`

Example response:

```json
{
  "status": "ok",
  "backend": "heuristic",
  "classes": 10,
  "time": "2026-01-01T12:00:00"
}
```

`backend` is either `heuristic` or `tensorflow`.

## `GET /api/classes`

Returns the class labels and static informational text configured in `backend/app.py`.

## `POST /api/predict`

Send `multipart/form-data` with an image file under the field name `image`.

```bash
curl -X POST http://127.0.0.1:5000/api/predict \
  -F "image=@sample.jpg"
```

The response includes `prediction`, `confidence`, `severity`, `advice`, `top3`, `image_url`, `backend`, and `timestamp`.

**Caution:** When `backend` is `heuristic`, the prediction and confidence are synthetic demo outputs. Even in TensorFlow mode, performance and class-index mapping must be independently validated before interpreting outputs.

## `GET /api/history`

Returns up to the latest 20 locally stored records, newest first. History is stored in `prediction_history.json` in the Flask prototype directory.
