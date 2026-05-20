# Azure Functions Scrapper

This project is my debut with Microsoft Azure. I used Azure Functions to create a small scraping function as a learning exercise.

## What it does

- Runs a simple scrape task via an Azure Function
- Serves as a first step into Azure development

## API documentation

Base URL (local): `http://localhost:7071/api`

### Scrap

Scrapes a Reddit post or multiple posts and returns the scraped details.

- **Method**: `GET`, `POST`
- **Route**: `/Scrap`
- **Auth**: Function key (if required by your host settings)

**Request body (POST)**

Send either a single `permalink` or a list of `permalinks`.

```json
{
	"permalink": "https://www.reddit.com/r/some_sub/comments/abc123/some_post/"
}
```

```json
{
	"permalinks": [
		"https://www.reddit.com/r/some_sub/comments/abc123/some_post/",
		"https://www.reddit.com/r/another/comments/def456/another_post/"
	]
}
```

**Response (200)**

Returns an array of scraped objects, one per link.

```json
[
	{
		"title": "...",
		"author": "...",
		"content": "..."
	}
]
```

**Error responses**

- `400` if no `permalink` or `permalinks` is provided.

**Environment variables**

- `WEBSHARE_PROXY_URL` (optional) to route scraping through a proxy.

### SerperSearch

Performs several Reddit search queries using the Serper API and returns the raw results grouped by query type.

- **Method**: `GET`
- **Route**: `/SerperSearch`
- **Query params**: `model` (required)

**Request example**

```
GET /api/SerperSearch?model=steam%20deck
```

**Response (200)**

```json
{
	"comprehensive": { "...": "..." },
	"friction_failure": { "...": "..." },
	"comparison": { "...": "..." }
}
```

**Error responses**

- `400` if `model` query param is missing.
- `500` if `SERPER_URL` or `SERPER_API_KEY` is missing.

**Environment variables**

- `SERPER_URL` (required) Serper API endpoint.
- `SERPER_API_KEY` (required) Serper API key.

## Why I built it

- Get hands-on experience with Azure Functions and the local runtime
- Practice structuring a small Python project for serverless use
- Learn how to configure settings and dependencies for deployment

## How it is structured

- Function entrypoint and host configuration live at the repository root
- Source code is organized under the `src/` folder
- Dependencies are listed in `requirements.txt`

## Local development

1. Create and activate a Python virtual environment.
2. Install dependencies with `pip install -r requirements.txt`.
3. Start the Functions host.

## Production testing

Test the endpoints in production via HTTP (Postman or `curl`).

**Prerequisites**

- App URL: `https://<app-name>.azurewebsites.net`
- Function key (auth level is Function)
- Endpoints:
	- `POST /api/Scrap`
	- `GET /api/SerperSearch?model=...`

**Auth options**

1. Query string: `?code=<FUNCTION_KEY>`
2. Header: `x-functions-key: <FUNCTION_KEY>`

**Postman**

- Scrap
	- Method: `POST`
	- URL: `https://<app-name>.azurewebsites.net/api/Scrap?code=<FUNCTION_KEY>`
	- Body (raw JSON):

```json
{
	"permalink": "https://www.reddit.com/r/..."
}
```

- SerperSearch
	- Method: `GET`
	- URL: `https://<app-name>.azurewebsites.net/api/SerperSearch?model=steam%20deck&code=<FUNCTION_KEY>`

**curl**

```bash
curl -X POST "https://<app-name>.azurewebsites.net/api/Scrap?code=<FUNCTION_KEY>" \
	-H "Content-Type: application/json" \
	-d '{"permalink":"https://www.reddit.com/r/..."}'
```

```bash
curl "https://<app-name>.azurewebsites.net/api/SerperSearch?model=steam%20deck&code=<FUNCTION_KEY>"
```
