from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

from password_checker import analyze_password, check_hibp_breached
from phishing_checker import analyze_phishing_email
from website_checker import inspect_website_security, WebsiteCheckError
from scenarios_data import SCENARIOS
from quiz_generator import generate_quiz

app = FastAPI(
    title="Cyber Security Awareness & Threat Analysis API",
    version="2.0.0",
    description="Backend services for Password Checker, Email Phishing Analyzer, Secured Website Inspector, and Security Training Scenarios."
)

# Enable CORS for frontend dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for request validation
class PasswordCheckRequest(BaseModel):
    password: str

class PhishingCheckRequest(BaseModel):
    email_body: str
    subject: Optional[str] = ""
    sender: Optional[str] = ""
    headers: Optional[str] = ""

class WebsiteCheckRequest(BaseModel):
    url: str

@app.get("/api/health")
def health_check():
    return {"status": "online", "service": "Cyber Security Suite API", "version": "2.0.0"}

@app.post("/api/password/check")
async def check_password(payload: PasswordCheckRequest):
    if not payload.password:
        raise HTTPException(status_code=400, detail="Password string cannot be empty.")
    
    result = analyze_password(payload.password)
    breach_info = await check_hibp_breached(payload.password)
    result["breach_status"] = breach_info
    
    # Adjust score if breached
    if breach_info.get("is_breached"):
        result["score"] = min(result["score"], 10)
        count = breach_info.get("count")
        result["rating"] = "Breached"
        result["badge_color"] = "danger"
        result["crack_time"] = "Instantly"
        result["warnings"].insert(0, f"Found in known data breaches ({count:,} times)." if count else "This is one of the most common leaked passwords.")
        result["suggestions"].insert(0, "Don't use this password anywhere. Change it on any account that uses it.")
        
    return result

@app.post("/api/phishing/check")
def check_phishing(payload: PhishingCheckRequest):
    if not payload.email_body.strip() and not (payload.subject or "").strip():
        raise HTTPException(status_code=400, detail="Please provide email body or subject line to analyze.")
    
    result = analyze_phishing_email(
        email_body=payload.email_body,
        subject=payload.subject or "",
        sender=payload.sender or "",
        headers=payload.headers or ""
    )
    return result

@app.post("/api/website/check")
async def check_website(payload: WebsiteCheckRequest):
    if not payload.url.strip():
        raise HTTPException(status_code=400, detail="Please provide a valid URL or domain.")

    try:
        return await inspect_website_security(payload.url)
    except WebsiteCheckError as e:
        raise HTTPException(status_code=422, detail=str(e))

@app.get("/api/scenarios")
def get_scenarios():
    return SCENARIOS

@app.get("/api/quiz")
def get_quiz(count: int = Query(10, ge=4, le=20), seed: Optional[int] = None):
    return generate_quiz(count=count, seed=seed)

@app.get("/api/scenarios/{scenario_id}")
def get_scenario_detail(scenario_id: str):
    for s in SCENARIOS:
        if s["id"] == scenario_id:
            return s
    raise HTTPException(status_code=404, detail="Scenario not found.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
