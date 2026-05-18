import json
import os
import sys
import logging
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