import os
from fastapi import FastAPI, HTTPException, Depends, Header, Request
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from models import ScrapeRequest, ScrapeResponse
from scraper import WebScraper

load_dotenv()

app = FastAPI(
    title="Web Scraping Service",
    description="A simple web scraping API service",
    version="1.0.0"
)

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

scraper = WebScraper()

API_KEY = os.getenv("API_KEY", "your-secret-api-key-here")


def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")
    return x_api_key


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "service": "Web Scraping API",
        "version": "1.0.0",
        "endpoints": {
            "/scrape": "POST - Scrape a webpage",
            "/health": "GET - Health check"
        },
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "web-scraping-api"}


@app.post("/scrape", response_model=ScrapeResponse)
@limiter.limit("60/minute")
async def scrape_webpage(
    request: Request,
    body: ScrapeRequest,
    api_key: str = Depends(verify_api_key)
):
    """
    Scrape a webpage and return the content
    
    Parameters:
    - url: The URL to scrape
    - render_js: Whether to render JavaScript (default: False)
    - wait_for: CSS selector to wait for before returning content
    - extract: Dictionary of CSS selectors to extract specific data
    - screenshot: Whether to take a screenshot (default: False)
    - use_proxy: Whether to use proxy rotation (default: False)
    """
    try:
        result = await scraper.scrape(
            url=str(body.url),
            render_js=body.render_js,
            selector_type=body.selector_type,
            wait_for=body.wait_for,
            extract=body.extract,
            screenshot=body.screenshot,
            use_proxy=body.use_proxy,
            custom_headers=body.custom_headers
        )
        
        return ScrapeResponse(
            success=True,
            url=str(body.url),
            status_code=result.get("status_code", 200),
            html=result.get("html"),
            extracted_data=result.get("extracted_data"),
            screenshot=result.get("screenshot"),
            response_time=result.get("response_time")
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Scraping failed: {str(e)}"
        )


@app.on_event("startup")
async def startup_event():
    print("🚀 Web Scraping Service starting...")
    print(f"📝 API Documentation: http://localhost:{os.getenv('API_PORT', 8000)}/docs")


@app.on_event("shutdown")
async def shutdown_event():
    await scraper.close()
    print("👋 Web Scraping Service shutting down...")


if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", 8000))
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )
