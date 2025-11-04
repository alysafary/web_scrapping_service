from typing import Optional, Dict, Any, Literal, List

from pydantic import BaseModel, HttpUrl, Field


class ScrapeRequest(BaseModel):
    """Request model for scraping endpoint"""
    url: HttpUrl = Field(..., description="The URL to scrape")
    render_js: bool = Field(False, description="Render JavaScript before scraping")
    selector_type: Literal["css", "xpath"] = Field(
        "css",
        description="Type of selectors used in wait_for and extract fields"
    )
    wait_for: Optional[str] = Field(None, description="CSS selector or XPath to wait for")
    extract: Optional[Dict[str, str]] = Field(
        None,
        description="Dictionary of field names and selectors (CSS or XPath) to extract"
    )
    screenshot: bool = Field(False, description="Take a screenshot of the page")
    scrape_images: bool = Field(False, description="Extract all image elements from the page")
    use_proxy: bool = Field(False, description="Use proxy rotation")
    custom_headers: Optional[Dict[str, str]] = Field(
        None,
        description="Custom headers to send with the request"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "url": "https://example.com/",
                "render_js": True,
                "selector_type": "xpath",
                "wait_for": "//div[@class=\"main-content\"]",
                "extract": {
                    "logo": "//img[@class=\"logo-default\"]/@src",
                    "title": "//h1/text()",
                    "all_links": "//a/@href"
                },
                "screenshot": False,
                "scrape_images": False,
                "use_proxy": False
            }
        }


class ScrapeResponse(BaseModel):
    """Response model for scraping endpoint"""
    success: bool = Field(..., description="Whether the scraping was successful")
    url: str = Field(..., description="The URL that was scraped")
    status_code: int = Field(..., description="HTTP status code")
    html: Optional[str] = Field(None, description="Raw HTML content")
    extracted_data: Optional[Dict[str, Any]] = Field(
        None,
        description="Extracted data based on provided selectors"
    )
    screenshot: Optional[str] = Field(
        None,
        description="Base64 encoded screenshot (if requested)"
    )
    images: Optional[List[Dict[str, Any]]] = Field(
        None,
        description="List of image elements with src, alt, and other attributes (if scrape_images=True)"
    )
    response_time: Optional[float] = Field(
        None,
        description="Time taken to scrape in seconds"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "url": "https://example.com",
                "status_code": 200,
                "html": "<html>...</html>",
                "extracted_data": {
                    "title": "Example Domain",
                    "description": "This domain is for use in examples"
                },
                "screenshot": None,
                "images": [
                    {
                        "src": "https://example.com/image.jpg",
                        "alt": "Example image",
                        "width": "800",
                        "height": "600"
                    }
                ],
                "response_time": 1.23
            }
        }
