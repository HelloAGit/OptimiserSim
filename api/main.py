"""FastAPI application entry point."""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import uvicorn

from src.router import ModelRouter, get_router

app = FastAPI(title="Model Router / Cost Optimizer", version="1.0.0")

router = get_router()


class RouteRequest(BaseModel):
    query: str
    accuracy_threshold: Optional[float] = None
    stream: bool = False


class RouteResponse(BaseModel):
    selected_model: str
    model_endpoint: str
    estimated_tokens_input: int
    estimated_tokens_output: int
    estimated_cost_usd: float
    accuracy_threshold_used: float
    routing_timestamp: str
    complexity_score: float


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "model-router"}


@app.post("/route", response_model=RouteResponse)
async def route_query(request: RouteRequest):
    """Route a query to the optimal model."""
    try:
        result = await router.route_query(
            query=request.query,
            accuracy_threshold=request.accuracy_threshold
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/execute")
async def execute_query(request: RouteRequest):
    """Route and execute query against selected model."""
    try:
        # First route the query
        routing = await router.route_query(
            query=request.query,
            accuracy_threshold=request.accuracy_threshold
        )
        
        # Then execute against selected model
        result = await router.execute_query_with_model(
            query=request.query,
            model_name=routing["selected_model"]
        )
        
        # Update accuracy tracking (would use actual eval in production)
        router.update_accuracy(routing["selected_model"], True)
        
        return {
            "routing": routing,
            "execution": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/metrics")
async def get_metrics():
    """Get current routing metrics."""
    return router.get_metrics()


@app.get("/models")
async def list_models():
    """List all available models."""
    return router.model_registry.get_all_models()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
