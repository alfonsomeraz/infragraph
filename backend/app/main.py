from fastapi import FastAPI

from app.config import settings
from app.routes import findings, graph, ingest, resources

app = FastAPI(
    title="InfraGraph",
    description="Cloud dependency mapper — upload Terraform plan/state, explore dependency graphs",
    version="0.1.0",
)

app.include_router(ingest.router, prefix=settings.api_prefix)
app.include_router(resources.router, prefix=settings.api_prefix)
app.include_router(graph.router, prefix=settings.api_prefix)
app.include_router(findings.router, prefix=settings.api_prefix)


@app.get("/health")
async def health():
    return {"status": "ok"}
