"""
FastAPI Backend -- wire the listingsAPI SDK into a REST API your frontend can call.

Install:
    pip install listingsapi fastapi uvicorn

Run:
    LISTINGSAPI_KEY='your_key' uvicorn examples.11_fastapi_backend:app --reload --port 8000

Your frontend can then call:
    GET  /locations
    GET  /locations/:id
    GET  /locations/:id/listings
    GET  /locations/:id/reviews
    POST /locations/:id/reviews/:interaction_id/respond
"""

import listingsapi
from listingsapi import APIError

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# --- Init ---
app = FastAPI(title="listingsAPI-powered API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # lock this down in production
    allow_methods=["*"],
    allow_headers=["*"],
)

client = listingsapi.ListingsAPI()  # reads LISTINGSAPI_KEY from env


# --- Helpers ---

def _page_to_dict(page):
    """Serialize a SyncPage into a JSON-friendly dict."""
    return {
        "items": [item.to_dict() for item in page],
        "has_more": page.has_more,
        "total": page.total,
    }


# --- Routes ---

@app.get("/locations")
def list_locations(
    first: int = Query(20, ge=1, le=100),
    after: str | None = None,
    q: str | None = None,
):
    """Get locations with optional search and pagination."""
    try:
        if q:
            page = client.locations.search(q, first=first, after=after)
        else:
            page = client.locations.list(first=first, after=after)
        return _page_to_dict(page)
    except APIError as e:
        raise HTTPException(status_code=getattr(e, "status_code", 500), detail=str(e))


@app.get("/locations/{location_id}")
def get_location(location_id: str):
    """Get a single location by ID."""
    try:
        loc = client.locations.retrieve(location_id)
        return loc.to_dict()
    except APIError as e:
        raise HTTPException(status_code=getattr(e, "status_code", 500), detail=str(e))


@app.get("/locations/{location_id}/listings")
def get_listings(location_id: str):
    """Get all listing types for a location."""
    try:
        return {
            "premium": [l.to_dict() for l in client.listings.premium(location_id)],
            "voice": [l.to_dict() for l in client.listings.voice(location_id)],
        }
    except APIError as e:
        raise HTTPException(status_code=getattr(e, "status_code", 500), detail=str(e))


@app.get("/locations/{location_id}/reviews")
def get_reviews(
    location_id: str,
    first: int = Query(20, ge=1, le=100),
    start_date: str | None = None,
    end_date: str | None = None,
):
    """Get reviews for a location."""
    try:
        page = client.reviews.list(
            location_id, first=first, start_date=start_date, end_date=end_date
        )
        return _page_to_dict(page)
    except APIError as e:
        raise HTTPException(status_code=getattr(e, "status_code", 500), detail=str(e))


class ReviewResponse(BaseModel):
    content: str


@app.post("/locations/{location_id}/reviews/{interaction_id}/respond")
def respond_to_review(location_id: str, interaction_id: str, body: ReviewResponse):
    """Respond to a review."""
    try:
        result = client.reviews.respond(interaction_id, body.content)
        return result.to_dict()
    except APIError as e:
        raise HTTPException(status_code=getattr(e, "status_code", 500), detail=str(e))
