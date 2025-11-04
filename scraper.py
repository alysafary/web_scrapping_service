import asyncio
import time
import base64
from typing import Optional, Dict, Literal
import httpx
from playwright.async_api import async_playwright, Browser, Page
from bs4 import BeautifulSoup
from lxml import html as lxml_html
import random
import os


class WebScraper:
    
    def __init__(self):
        self.browser: Optional[Browser] = None
        self.playwright = None
        self.proxy_list = self._load_proxies()
        
    def _load_proxies(self):
        proxy_enabled = os.getenv("PROXY_ENABLED", "false").lower() == "true"
        if not proxy_enabled:
            return []
        
        proxy_string = os.getenv("PROXY_LIST", "")
        return [p.strip() for p in proxy_string.split(",") if p.strip()]
    
    def _get_random_proxy(self) -> Optional[str]:
        if not self.proxy_list:
            return None
        return random.choice(self.proxy_list)
    
    async def _init_browser(self):
        if not self.playwright:
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(
                headless=True,
                args=['--no-sandbox', '--disable-setuid-sandbox']
            )
    
    async def _scrape_with_js(
        self,
        url: str,
        selector_type: Literal["css", "xpath"] = "css",
        wait_for: Optional[str] = None,
        screenshot: bool = False,
        use_proxy: bool = False,
        custom_headers: Optional[Dict[str, str]] = None
    ) -> Dict:
        await self._init_browser()
        
        proxy = None
        if use_proxy:
            proxy_url = self._get_random_proxy()
            if proxy_url:
                proxy = {"server": proxy_url}
        
        context = await self.browser.new_context(
            proxy=proxy,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
        
        if custom_headers:
            await context.set_extra_http_headers(custom_headers)
        
        page = await context.new_page()
        
        try:
            response = await page.goto(url, wait_until="networkidle", timeout=30000)
            
            if wait_for:
                if selector_type == "xpath":
                    await page.locator(f"xpath={wait_for}").wait_for(timeout=10000)
                else:
                    await page.wait_for_selector(wait_for, timeout=10000)
            
            html = await page.content()
            
            screenshot_data = None
            if screenshot:
                screenshot_bytes = await page.screenshot(full_page=True)
                screenshot_data = base64.b64encode(screenshot_bytes).decode('utf-8')
            
            return {
                "html": html,
                "status_code": response.status if response else 200,
                "screenshot": screenshot_data
            }
        
        finally:
            await page.close()
            await context.close()
    
    async def _scrape_simple(
        self,
        url: str,
        use_proxy: bool = False,
        custom_headers: Optional[Dict[str, str]] = None
    ) -> Dict:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        if custom_headers:
            headers.update(custom_headers)
        
        proxies = None
        if use_proxy:
            proxy_url = self._get_random_proxy()
            if proxy_url:
                proxies = {
                    "http://": proxy_url,
                    "https://": proxy_url
                }
        
        async with httpx.AsyncClient(
            headers=headers,
            proxies=proxies,
            timeout=30.0,
            follow_redirects=True
        ) as client:
            response = await client.get(url)
            
            return {
                "html": response.text,
                "status_code": response.status_code,
                "screenshot": None
            }
    
    def _extract_data(
        self,
        html_content: str,
        selectors: Dict[str, str],
        selector_type: Literal["css", "xpath"] = "css"
    ) -> Dict:
        extracted = {}
        
        if selector_type == "xpath":
            # Use lxml for XPath extraction
            tree = lxml_html.fromstring(html_content)
            
            for field_name, selector in selectors.items():
                try:
                    elements = tree.xpath(selector)
                    
                    if len(elements) == 0:
                        extracted[field_name] = None
                    elif len(elements) == 1:
                        # Handle both Element and string results
                        if hasattr(elements[0], 'text_content'):
                            extracted[field_name] = elements[0].text_content().strip()
                        else:
                            extracted[field_name] = str(elements[0]).strip()
                    else:
                        extracted[field_name] = [
                            el.text_content().strip() if hasattr(el, 'text_content') else str(el).strip()
                            for el in elements
                        ]
                except Exception as e:
                    extracted[field_name] = f"Error: {str(e)}"
        else:
            # Use BeautifulSoup for CSS selectors
            soup = BeautifulSoup(html_content, 'lxml')
            
            for field_name, selector in selectors.items():
                elements = soup.select(selector)
                
                if len(elements) == 0:
                    extracted[field_name] = None
                elif len(elements) == 1:
                    extracted[field_name] = elements[0].get_text(strip=True)
                else:
                    extracted[field_name] = [el.get_text(strip=True) for el in elements]
        
        return extracted
    
    async def scrape(
        self,
        url: str,
        render_js: bool = False,
        selector_type: Literal["css", "xpath"] = "css",
        wait_for: Optional[str] = None,
        extract: Optional[Dict[str, str]] = None,
        screenshot: bool = False,
        use_proxy: bool = False,
        custom_headers: Optional[Dict[str, str]] = None
    ) -> Dict:
        """
        Main scraping method
        
        Args:
            url: URL to scrape
            render_js: Whether to render JavaScript
            selector_type: Type of selector ('css' or 'xpath')
            wait_for: CSS selector or XPath to wait for (only with render_js=True)
            extract: Dictionary of selectors to extract data
            screenshot: Whether to take a screenshot (only with render_js=True)
            use_proxy: Whether to use proxy rotation
            custom_headers: Custom HTTP headers
        
        Returns:
            Dictionary with scraped data
        """
        start_time = time.time()
        
        try:
            if render_js:
                result = await self._scrape_with_js(
                    url=url,
                    selector_type=selector_type,
                    wait_for=wait_for,
                    screenshot=screenshot,
                    use_proxy=use_proxy,
                    custom_headers=custom_headers
                )
            else:
                if screenshot or wait_for:
                    raise ValueError(
                        "Screenshot and wait_for require render_js=True"
                    )
                result = await self._scrape_simple(
                    url=url,
                    use_proxy=use_proxy,
                    custom_headers=custom_headers
                )
            
            extracted_data = None
            if extract and result.get("html"):
                extracted_data = self._extract_data(
                    result["html"],
                    extract,
                    selector_type
                )
            
            response_time = time.time() - start_time
            
            return {
                "status_code": result["status_code"],
                "html": result["html"],
                "extracted_data": extracted_data,
                "screenshot": result.get("screenshot"),
                "response_time": round(response_time, 2)
            }
        
        except Exception as e:
            raise Exception(f"Scraping error: {str(e)}")
    
    async def close(self):
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
