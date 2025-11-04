import asyncio
from scraper import WebScraper


async def test_simple_scrape():
    scraper = WebScraper()
    
    print("Testing simple scraping...")
    result = await scraper.scrape(
        url="https://example.com",
        render_js=False
    )
    
    print(f"✅ Status Code: {result['status_code']}")
    print(f"✅ HTML Length: {len(result['html'])} characters")
    print(f"✅ Response Time: {result['response_time']} seconds")
    
    await scraper.close()


async def test_js_rendering():
    scraper = WebScraper()
    
    print("\nTesting JavaScript rendering...")
    result = await scraper.scrape(
        url="https://example.com",
        render_js=True
    )
    
    print(f"✅ Status Code: {result['status_code']}")
    print(f"✅ HTML Length: {len(result['html'])} characters")
    print(f"✅ Response Time: {result['response_time']} seconds")
    
    await scraper.close()


async def test_data_extraction():
    scraper = WebScraper()
    
    print("\nTesting data extraction...")
    result = await scraper.scrape(
        url="https://example.com",
        render_js=False,
        extract={
            "title": "h1",
            "paragraphs": "p"
        }
    )
    
    print(f"✅ Status Code: {result['status_code']}")
    print(f"✅ Extracted Data: {result['extracted_data']}")
    print(f"✅ Response Time: {result['response_time']} seconds")
    
    await scraper.close()


async def main():
    print("=" * 60)
    print("Web Scraper Test Suite")
    print("=" * 60)
    
    try:
        await test_simple_scrape()
        await test_js_rendering()
        await test_data_extraction()
        
        print("\n" + "=" * 60)
        print("✅ All tests passed!")
        print("=" * 60)
    
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")


if __name__ == "__main__":
    asyncio.run(main())
