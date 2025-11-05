import os
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, FileResponse
from dotenv import load_dotenv
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from models import ScrapeRequest, ScrapeResponse
from scraper import WebScraper

load_dotenv()

# Lazy initialization - don't create scraper at module level
# This prevents issues with serverless functions where module-level
# initialization can cause problems with Playwright browser binaries
_scraper_instance: WebScraper = None


def get_scraper() -> WebScraper:
    """Get or create the scraper instance (lazy initialization)"""
    global _scraper_instance
    if _scraper_instance is None:
        _scraper_instance = WebScraper()
    return _scraper_instance


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Web Scraping Service starting...")
    print(f"📝 API Documentation: http://localhost:{os.getenv('API_PORT', 8000)}/docs")
    yield
    # Shutdown
    # In serverless, cleanup might not always run, but we try anyway
    scraper = get_scraper()
    try:
        await scraper.close()
    except Exception as e:
        print(f"Warning: Error during cleanup: {e}")
    print("👋 Web Scraping Service shutting down...")


app = FastAPI(
    title="Web Scraping Service",
    description="A simple web scraping API service",
    version="1.0.0",
    lifespan=lifespan
)

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

@app.get("/")
async def root():
    """Root endpoint - serves the API testing interface"""
    template_path = Path(__file__).parent / "templates" / "index.html"
    return FileResponse(template_path)


@app.get("/api")
async def api_info():
    """API information endpoint"""
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
    body: ScrapeRequest
):
    """
    Scrape a webpage and return the content
    
    Parameters:
    - url: The URL to scrape
    - render_js: Whether to render JavaScript (default: False)
    - wait_for: CSS selector to wait for before returning content
    - extract: Dictionary of CSS selectors to extract specific data
    - screenshot: Whether to take a screenshot (default: False)
    - scrape_images: Whether to extract all image elements (default: False)
    - use_proxy: Whether to use proxy rotation (default: False)
    """
    try:
        # Get scraper instance (lazy initialization)
        scraper = get_scraper()
        result = await scraper.scrape(
            url=str(body.url),
            render_js=body.render_js,
            selector_type=body.selector_type,
            wait_for=body.wait_for,
            extract=body.extract,
            screenshot=body.screenshot,
            scrape_images=body.scrape_images,
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
            images=result.get("images"),
            response_time=result.get("response_time")
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Scraping failed: {str(e)}"
        )


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
