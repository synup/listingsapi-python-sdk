"""
Full-stack sample -- FastAPI backend + basic frontend.

Install:
    pip install listingsapi fastapi uvicorn

Run:
    LISTINGSAPI_KEY='your_key' python examples/fullstack/server.py

Then open http://localhost:3000
"""

from pathlib import Path

import listingsapi
from listingsapi import APIError

from fastapi import FastAPI, HTTPException, Query, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

app = FastAPI(title="listingsAPI Full-stack Sample")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

client = listingsapi.ListingsAPI()  # reads LISTINGSAPI_KEY from env
STATIC_DIR = Path(__file__).parent / "static"


# --- Helpers ---

def _page_to_dict(page):
    """Serialize a SyncPage into a JSON-friendly dict."""
    return {
        "items": [item.to_dict() for item in page],
        "has_more": page.has_more,
        "total": page.total,
    }


# -- Locations ----------------------------------------------------------------

@app.get("/api/locations")
def list_locations(
    first: int = Query(10, ge=1, le=100),
    after: str | None = None,
    q: str | None = None,
):
    try:
        if q:
            page = client.locations.search(q, first=first, after=after)
        else:
            page = client.locations.list(first=first, after=after)
        return _page_to_dict(page)
    except APIError as e:
        raise HTTPException(status_code=getattr(e, "status_code", 500), detail=str(e))


@app.get("/api/locations/{location_id}")
def get_location(location_id: str):
    try:
        loc = client.locations.retrieve(location_id)
        return loc.to_dict()
    except APIError as e:
        raise HTTPException(status_code=getattr(e, "status_code", 500), detail=str(e))


@app.post("/api/locations")
def create_location(input_data: dict = Body(...)):
    try:
        result = client.locations.create(input_data)
        return result.to_dict()
    except APIError as e:
        raise HTTPException(status_code=getattr(e, "status_code", 500), detail=str(e))


@app.put("/api/locations")
def update_location(input_data: dict = Body(...)):
    try:
        result = client.locations.update(input_data)
        return result.to_dict()
    except APIError as e:
        raise HTTPException(status_code=getattr(e, "status_code", 500), detail=str(e))


@app.post("/api/locations/archive")
def archive_locations(location_ids: list[str] = Body(...)):
    try:
        result = client.locations.archive(location_ids)
        return result.to_dict()
    except APIError as e:
        raise HTTPException(status_code=getattr(e, "status_code", 500), detail=str(e))


# -- Listings -----------------------------------------------------------------

@app.get("/api/locations/{location_id}/listings")
def get_listings(location_id: str):
    try:
        return {
            "premium": [l.to_dict() for l in client.listings.premium(location_id)],
            "voice": [l.to_dict() for l in client.listings.voice(location_id)],
        }
    except APIError as e:
        raise HTTPException(status_code=getattr(e, "status_code", 500), detail=str(e))


# -- Reviews ------------------------------------------------------------------

@app.get("/api/locations/{location_id}/reviews")
def get_reviews(location_id: str, first: int = Query(10, ge=1, le=50)):
    try:
        page = client.reviews.list(location_id, first=first)
        return _page_to_dict(page)
    except APIError as e:
        raise HTTPException(status_code=getattr(e, "status_code", 500), detail=str(e))


class ReviewResponseBody(BaseModel):
    content: str


@app.post("/api/reviews/{interaction_id}/respond")
def respond_to_review(interaction_id: str, body: ReviewResponseBody):
    try:
        result = client.reviews.respond(interaction_id, body.content)
        return result.to_dict()
    except APIError as e:
        raise HTTPException(status_code=getattr(e, "status_code", 500), detail=str(e))


# -- Analytics ----------------------------------------------------------------

@app.get("/api/locations/{location_id}/analytics/google")
def google_analytics(
    location_id: str,
    from_date: str | None = None,
    to_date: str | None = None,
):
    try:
        result = client.analytics.google(location_id, from_date=from_date, to_date=to_date)
        return result.to_dict()
    except APIError as e:
        raise HTTPException(status_code=getattr(e, "status_code", 500), detail=str(e))


@app.get("/api/locations/{location_id}/analytics/reviews")
def review_analytics(
    location_id: str,
    start_date: str | None = None,
    end_date: str | None = None,
):
    try:
        result = client.reviews.analytics.overview(
            location_id, start_date=start_date, end_date=end_date
        )
        return result.to_dict()
    except APIError as e:
        raise HTTPException(status_code=getattr(e, "status_code", 500), detail=str(e))


# -- Grid Rank ----------------------------------------------------------------

@app.get("/api/locations/{location_id}/grid-reports")
def list_grid_reports(
    location_id: str,
    page: int = Query(1),
    page_size: int = Query(10),
):
    try:
        result = client.grid_reports.list(location_id, page=page, page_size=page_size)
        return result.to_dict()
    except APIError as e:
        raise HTTPException(status_code=getattr(e, "status_code", 500), detail=str(e))


@app.get("/api/grid-report/{report_id}")
def get_grid_report(report_id: str):
    try:
        result = client.grid_reports.retrieve(report_id)
        return result.to_dict()
    except APIError as e:
        raise HTTPException(status_code=getattr(e, "status_code", 500), detail=str(e))


# -- Review Campaigns ---------------------------------------------------------

@app.get("/api/locations/{location_id}/campaigns")
def list_campaigns(location_id: str):
    try:
        campaigns = client.campaigns.list(location_id)
        return [c.to_dict() for c in campaigns]
    except APIError as e:
        raise HTTPException(status_code=getattr(e, "status_code", 500), detail=str(e))


# -- Google Connect -----------------------------------------------------------

@app.post("/api/google/connect")
def google_connect(
    success_url: str = Body(...),
    error_url: str = Body(...),
):
    try:
        result = client.connected_accounts.connect_google(
            success_url=success_url, error_url=error_url
        )
        return result.to_dict()
    except APIError as e:
        raise HTTPException(status_code=getattr(e, "status_code", 500), detail=str(e))


@app.get("/api/connected-accounts")
def connected_accounts(publisher: str | None = None, page: int = 1):
    try:
        result = client.connected_accounts.list(publisher=publisher, page=page, per_page=50)
        return result.to_dict()
    except APIError as e:
        raise HTTPException(status_code=getattr(e, "status_code", 500), detail=str(e))


# -- Serve frontend -----------------------------------------------------------

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/")
def index():
    return FileResponse(str(STATIC_DIR / "index.html"))


if __name__ == "__main__":
    import uvicorn
    print("listingsAPI Full-stack Sample -> http://localhost:3000")
    uvicorn.run(app, host="0.0.0.0", port=3000)
