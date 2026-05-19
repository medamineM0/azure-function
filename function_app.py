import os
import sys
import json
import logging
import requests
import azure.functions as func

BASE_DIR = os.path.dirname(__file__)
SRC_DIR = os.path.join(BASE_DIR, "src")

if SRC_DIR not in sys.path:
    sys.path.append(SRC_DIR)

from utils import YARS

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

@app.route(route="Scrap", methods=["GET", "POST"])
def Scrap(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Scrap function processed a request.")
    
    permalinks = None
    permalink =  None
    proxy_url = os.environ.get("WEBSHARE_PROXY_URL")
    
    if not permalink:
        try:
            req_body = req.get_json()
            permalinks = req_body.get("permalinks")
            if not permalinks:
                permalink = req_body.get("permalink")
        except ValueError:
            pass

    links_to_process = []
    if isinstance(permalinks, list) and permalinks:
        links_to_process = permalinks
    elif permalink:
        links_to_process = [permalink]

    if not links_to_process:
        return func.HttpResponse(
            json.dumps({"error": "Missing permalink(s)"}),
            status_code=400,
            mimetype="application/json",
        )

    
    miner = YARS(proxy=proxy_url)
    results = []
    for link in links_to_process:
        if "reddit.com" in link:
            link = link.split("reddit.com", 1)[1]

        data = miner.scrape_post_details(link)
        results.append(data)

    return func.HttpResponse(
        json.dumps(results, ensure_ascii=False, indent=4),
        status_code=200,
        mimetype="application/json",
    )


@app.route(route="SerperSearch", methods=["GET"])
def SerperSearch(req: func.HttpRequest) -> func.HttpResponse:
    model = req.params.get("model")

    if not model:
        return func.HttpResponse(
            json.dumps({"error": "Missing query param: model"}),
            status_code=400,
            mimetype="application/json",
        )

    serper_url = os.environ.get("SERPER_URL", "")
    api_key = os.environ.get("SERPER_API_KEY", "")

    if not serper_url:
        return func.HttpResponse(
            json.dumps({"error": "Missing SERPER_URL"}),
            status_code=500,
            mimetype="application/json",
        )

    if not api_key:
        return func.HttpResponse(
            json.dumps({"error": "Missing SERPER_API_KEY"}),
            status_code=500,
            mimetype="application/json",
        )

    headers = {
        "X-API-KEY": api_key,
        "Content-Type": "application/json",
    }

    queries = {
        "comprehensive": f'site:reddit.com "{model}" (review OR thoughts OR impressions OR "months later" OR "worth it")',
        "friction_failure": f'site:reddit.com "{model}" (issue OR broken OR problem OR regret OR fix OR annoying)',
        "comparison": f'site:reddit.com "{model}" (vs OR "compared to" OR "upgrade from")',
    }

    results = {}
    for key, query in queries.items():
        try:
            response = requests.post(
                serper_url,
                headers=headers,
                json={"q": query},
                timeout=30,
            )
            response.raise_for_status()
            results[key] = response.json()
        except requests.RequestException as exc:
            logging.error("Serper request failed for %s: %s", key, exc)
            results[key] = {
                "error": str(exc),
                "status": getattr(getattr(exc, "response", None), "status_code", None),
                "body": getattr(getattr(exc, "response", None), "text", None),
            }

    return func.HttpResponse(
        json.dumps(results, ensure_ascii=False, indent=4),
        status_code=200,
        mimetype="application/json",
    )