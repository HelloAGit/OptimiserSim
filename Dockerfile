# OptimiserSim

OptimiserSim is a FastAPI-based model router that selects the lowest-cost Fireworks AI model likely to satisfy a target accuracy threshold. It estimates token usage, routes queries, and exposes metrics for cost and model selection.

## Repository structure

* `api/main.py` — FastAPI entry point
* `src/` — routing, analysis, metrics, and model registry logic
* `config.yaml` — application configuration
* `requirements.txt` — Python dependencies
* `Dockerfile` — container build for deployment

## Local run

```bash
git clone https://github.com/HelloAGit/OptimiserSim.git
cd OptimiserSim
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export FIREWORKS_API_KEY="your_api_key"
python -m api.main
```

The API will start on:

* `http://127.0.0.1:8000`

Health check:

* `GET /health`

## API endpoints

* `GET /health` — service health
* `POST /route` — returns selected model and estimated token/cost values
* `POST /execute` — routes and executes the query
* `GET /metrics` — routing and cost metrics
* `GET /models` — available model registry

## Example request

```bash
curl -X POST "http://127.0.0.1:8000/route" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Summarize the main causes of the French Revolution.",
    "accuracy_threshold": 0.85,
    "stream": false
  }'
```

## Docker run

Build:

```bash
docker build -t optimisersim .
```

Run:

```bash
docker run --rm -p 8000:8000 \
  -e FIREWORKS_API_KEY="your_api_key" \
  optimisersim
```

Then verify:

```bash
curl http://127.0.0.1:8000/health
```

## Deployment notes for Natively AI

* Application entry point: `api.main:app`
* Container port: `8000`
* Health endpoint: `/health`
* Required environment variable: `FIREWORKS_API_KEY`

Before submitting, confirm:

1. The container builds successfully.
2. The app starts without import or config errors.
3. `GET /health` returns HTTP 200.
4. The Fireworks API key is configured in the deployment environment.

## Troubleshooting

### INFRA_ERROR during scoring

This usually means the deployment platform could not build, start, or health-check the app.

Check the following:

* Docker image builds successfully
* `requirements.txt` installs without errors
* `config.yaml` is present in the image
* `FIREWORKS_API_KEY` is set in the runtime environment
* The app binds to `0.0.0.0` on port `8000`
* `/health` responds with HTTP 200

### Missing API key

If requests to `/execute` fail, confirm that the runtime environment includes:

```bash
FIREWORKS_API_KEY=your_api_key
```

## License

MIT
