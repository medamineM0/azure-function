from __future__ import annotations

import logging
import requests
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

from sessions import RandomUserAgentSession

class YARS:
    __slots__ = ("headers", "session", "proxy", "timeout")

    def __init__(self, proxy=None, timeout=10, random_user_agent=True):
        self.session = RandomUserAgentSession() if random_user_agent else requests.Session()
        self.proxy = proxy
        self.timeout = timeout

        retries = Retry(
            total=5,
            backoff_factor=2,
            status_forcelist=[429, 500, 502, 503, 504],
        )

        self.session.mount("https://", HTTPAdapter(max_retries=retries))

        if proxy:
            self.session.proxies.update({"http": proxy, "https": proxy})

    def scrape_post_details(self, permalink):
        url = f"https://www.reddit.com{permalink}.json"

        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            # logging.info("Post details request successful : %s", url)
        except Exception as e:
            # logging.info("Post details request unsccessful: %e", e)
            if response.status_code != 200:
                print(f"Failed to fetch post data: {response.status_code}")
                return None

        post_data = response.json()
        if not isinstance(post_data, list) or len(post_data) < 2:
            # logging.info("Unexpected post data structre")
            print("Unexpected post data structure")
            return None

        main_post = post_data[0]["data"]["children"][0]["data"]
        title = main_post["title"]
        body = main_post.get("selftext", "")

        comments = self._extract_comments(post_data[1]["data"]["children"])
        # logging.info("Successfully scraped post: %s", title)
        return {
            "id": main_post.get("id", ""),
            "title": title,
            "body": body,
            "author": main_post.get("author", ""),
            "score": main_post.get("score", 0),
            "ups": main_post.get("ups", 0),
            "downs": main_post.get("downs", 0),
            "num_comments": main_post.get("num_comments", 0),
            "created_utc": main_post.get("created_utc", ""),
            "comments": comments,
        }

    def _extract_comments(self, comments):
        # logging.info("Extracting comments")
        extracted_comments = []
        for comment in comments:
            if isinstance(comment, dict) and comment.get("kind") == "t1":
                comment_data = comment.get("data", {})
                extracted_comment = {
                    "id": comment_data.get("id", ""),
                    "author": comment_data.get("author", ""),
                    "body": comment_data.get("body", ""),
                    "score": comment_data.get("score", ""),
                    "ups": comment_data.get("ups", 0),
                    "downs": comment_data.get("downs", 0),
                    "parent_id": comment_data.get("parent_id", ""),
                    "depth": comment_data.get("depth", ""),
                    "created_utc": comment_data.get("created_utc", ""),
                    "replies": [],
                }

                replies = comment_data.get("replies", "")
                if isinstance(replies, dict):
                    extracted_comment["replies"] = self._extract_comments(
                        replies.get("data", {}).get("children", [])
                    )
                extracted_comments.append(extracted_comment)
        # logging.info("Successfully extracted comments")
        return extracted_comments