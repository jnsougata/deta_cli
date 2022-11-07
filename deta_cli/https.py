import requests
import json
import time
from .sign import singature
from typing import Dict, Any, Union, List, Optional

BASE_URL = "https://v1.deta.sh"

def request(
        access_token: str,
        path: str,
        method: str,
        headers: dict = {},
        query: dict = {},
        body: Any = None,
        content_type: str = "application/json",
    ) -> requests.Response:
        timestamp = str(int(time.time()))
        raw_body = json.dumps(body) if body else ""
        sig = singature(
            access_token=access_token,
            http_method=method,
            uri=path,
            timestamp=timestamp,
            content_type=content_type,
            raw_body=raw_body,
        )
        headers["X-Deta-Timestamp"] = timestamp
        headers["X-Deta-Signature"] = sig
        headers["Content-Type"] = content_type
        url = BASE_URL + path
        return requests.request(method=method, url=url, headers=headers, params=query, data=raw_body.encode("UTF-8"))