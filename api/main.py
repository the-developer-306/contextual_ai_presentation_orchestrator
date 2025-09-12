from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import upload, generate, download, auth, memory
from utils.middleware import AuditAndFilterMiddleware

app = FastAPI(title="AI Presentation Orchestrator")

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# app.add_middleware(AuditAndFilterMiddleware)

# Routers
app.include_router(auth.router, prefix="/api")
app.include_router(upload.router, prefix="/api")
app.include_router(generate.router, prefix="/api")
app.include_router(download.router, prefix="/api")
app.include_router(memory.router, prefix="/api")

@app.get("/")
def root():
    return {"message": "AI Presentation Orchestrator is running "}
