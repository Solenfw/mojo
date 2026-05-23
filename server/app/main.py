from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import auth, users, srs, gamification, lessons, league

app = FastAPI(
    title="Linguasphere API",
    version="0.1.0",
    description="Backend API for Linguasphere: advanced Japanese learning, SRS, gamification, and social features.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_prefix = "/api/v1"
app.include_router(auth.router, prefix=api_prefix)
app.include_router(users.router, prefix=api_prefix)
# app.include_router(onboarding.router, prefix=api_prefix, tags=["onboarding"])
app.include_router(srs.router, prefix=api_prefix, tags=["srs"])
# app.include_router(nlp.router, prefix=api_prefix, tags=["nlp"])
# app.include_router(admin.router, prefix=api_prefix, tags=["admin"])
app.include_router(gamification.router, prefix=api_prefix, tags=["gamification"])
app.include_router(lessons.router, prefix=api_prefix, tags=["lessons"])
app.include_router(league.router, prefix=api_prefix, tags=["league"])
# app.include_router(shop.router, prefix=api_prefix, tags=["shop"])
# app.include_router(social.router, prefix=api_prefix, tags=["social"])


@app.get("/healthz")
async def health_check():
    return {"status": "ok"}


@app.get('/')
async def root():
    return {"message": "Welcome to the Linguasphere API"}
