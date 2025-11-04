# Web Scraping Service

A simplified web scraping API service inspired by ScrapingBee. This service provides an easy-to-use REST API for
scraping web pages with JavaScript rendering support, proxy rotation, and data extraction capabilities.

## Features

- 🌐 **RESTful API** - Simple HTTP API for web scraping
- 🎭 **JavaScript Rendering** - Scrape modern SPAs built with React, Vue, Angular, etc.
- 🔄 **Proxy Rotation** - Basic proxy support to avoid rate limiting
- ⚡ **Rate Limiting** - Built-in rate limiting to prevent abuse
- 📊 **Data Extraction** - Extract specific data using CSS selectors
- 📸 **Screenshots** - Capture screenshots of web pages
- 🎯 **Custom Headers** - Send custom HTTP headers with requests

## Installation

### Prerequisites

- Python 3.9+
- Poetry (Python dependency manager)
- Redis (optional, for rate limiting)

### Setup

1. Clone the repository:

```bash
git clone https://github.com/alysafary/web_scrapping_service.git
cd web_scrapping_service
```

2. Install Poetry (if not already installed):

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

3. Install dependencies:

```bash
poetry install
```

4. Install Playwright browsers:

```bash
poetry run playwright install chromium
```

5. Create a `.env` file:

```bash
cp .env.example .env
```

6. Edit `.env` and set your configuration (optional):

```env
API_HOST=0.0.0.0
API_PORT=8000
```

## Usage

### Starting the Server

Using Make (simplest):

```bash
make run
```

Or with Poetry:

```bash
poetry run python main.py
```

Or activate the Poetry shell first:

```bash
poetry shell
python main.py
```

Or with uvicorn:

```bash
poetry run uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

Interactive API documentation: `http://localhost:8000/docs`

### API Endpoints

#### POST /scrape

Scrape a webpage with optional JavaScript rendering and data extraction.

**Request Headers:**

```
Content-Type: application/json
```

**Request Body:**

```json
{
  "url": "https://example.com",
  "render_js": true,
  "wait_for": ".main-content",
  "extract": {
    "title": "h1",
    "description": ".description",
    "price": ".price"
  },
  "screenshot": false,
  "use_proxy": false,
  "custom_headers": {
    "Accept-Language": "en-US"
  }
}
```

**Response:**

```json
{
  "success": true,
  "url": "https://example.com",
  "status_code": 200,
  "html": "<html>...</html>",
  "extracted_data": {
    "title": "Example Domain",
    "description": "This domain is for use in examples",
    "price": "$99.99"
  },
  "screenshot": null,
  "response_time": 1.23
}
```

### Example Usage

#### Python

```python
import requests

url = "http://localhost:8000/scrape"
headers = {
    "Content-Type": "application/json"
}

payload = {
    "url": "https://example.com",
    "render_js": True,
    "extract": {
        "title": "h1",
        "paragraphs": "p"
    }
}

response = requests.post(url, json=payload, headers=headers)
print(response.json())
```

#### cURL

```bash
curl -X POST "http://localhost:8000/scrape" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "render_js": true,
    "extract": {
      "title": "h1"
    }
  }'
```

#### JavaScript/Node.js

## Configuration

### Environment Variables

| Variable                | Description                  | Default     |
|-------------------------|------------------------------|-------------|
| `API_HOST`              | Host to bind the server      | `0.0.0.0`   |
| `API_PORT`              | Port to run the server       | `8000`      |
| `REDIS_HOST`            | Redis host for rate limiting | `localhost` |
| `REDIS_PORT`            | Redis port                   | `6379`      |
| `RATE_LIMIT_PER_MINUTE` | Requests per minute limit    | `60`        |
| `PROXY_ENABLED`         | Enable proxy rotation        | `false`     |
| `PROXY_LIST`            | Comma-separated proxy URLs   | ``          |

### Proxy Configuration

To enable proxy rotation, set in your `.env`:

```env
PROXY_ENABLED=true
PROXY_LIST=http://proxy1.com:8080,http://proxy2.com:8080,http://proxy3.com:8080
```

## API Parameters

### Request Parameters

| Parameter        | Type    | Required | Description                                  |
|------------------|---------|----------|----------------------------------------------|
| `url`            | string  | Yes      | The URL to scrape                            |
| `render_js`      | boolean | No       | Enable JavaScript rendering (default: false) |
| `wait_for`       | string  | No       | CSS selector to wait for before returning    |
| `extract`        | object  | No       | Dictionary of field names and CSS selectors  |
| `screenshot`     | boolean | No       | Take a screenshot (requires render_js: true) |
| `use_proxy`      | boolean | No       | Use proxy rotation (default: false)          |
| `custom_headers` | object  | No       | Custom HTTP headers to send                  |

## Rate Limiting

The API includes built-in rate limiting:

- 60 requests per minute per IP address (default)
- Configurable via environment variables

## Development

### Project Structure

```
web_scrapping_service/
├── main.py              # FastAPI application and routes
├── models.py            # Pydantic models for requests/responses
├── scraper.py           # Web scraping logic
├── pyproject.toml       # Poetry dependencies and configuration
├── Makefile             # Convenient command shortcuts
├── setup.sh             # Automated setup script
├── .env.example         # Example environment variables
└── README.md           # This file
```

## Use Cases

- Price monitoring
- Content aggregation
- Market research
- SEO monitoring
- Data extraction for analysis
- Automated testing

## License

MIT License - feel free to use this in your projects!

