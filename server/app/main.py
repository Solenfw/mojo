from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from server.app.api.v1 import auth, speaking, users, srs, gamification, lessons, onboarding, nlp, writing, placement_tests

app = FastAPI(
    title="Linguasphere API",
    version="0.1.0",
    description="Backend API for Linguasphere: advanced Japanese learning, SRS, gamification, and social features.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ],
    allow_origin_regex=r"^https?://.*$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_prefix = "/api/v1"
app.include_router(auth.router, prefix=api_prefix)
app.include_router(users.router, prefix=api_prefix)
app.include_router(onboarding.router, prefix=api_prefix)
app.include_router(placement_tests.router, prefix=api_prefix)
app.include_router(srs.router, prefix=api_prefix, tags=["srs"])
app.include_router(nlp.router, prefix=api_prefix)
app.include_router(speaking.router, prefix=api_prefix)
app.include_router(writing.router, prefix=api_prefix)
app.include_router(gamification.router, prefix=api_prefix, tags=["gamification"])
app.include_router(lessons.router, prefix=api_prefix, tags=["lessons"])


@app.get("/healthz")
async def health_check():
    return {"status": "ok"}


@app.get('/')
async def root():
    return {"message": "Welcome to the Linguasphere API"}
