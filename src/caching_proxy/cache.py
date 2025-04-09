from contextlib import asynccontextmanager
import json
from aiohttp import ClientSession, web
import time
from multidict import CIMultiDict
import base64
import mimetypes


def load_cache():
    try:
        with open("proxy_cache", "r") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return {}

def save_cache(cache):
    with open("proxy_cache", "w") as f:
        json.dump(cache, f)

@asynccontextmanager
async def cache_session_manager(url: str):
    try:
        cache_lifetime = 24 * 60 * 60 # 1 day
        d = load_cache()
        current_time = time.time()
        if url in d:
            cached_time, cached_body, cached_status, cached_headers = d[url]
            decoded_body = base64.b64decode(cached_body)
            if current_time - cached_time < cache_lifetime:
                headers = CIMultiDict(cached_headers)
                headers.pop("Content-Encoding", None)
                headers["X-Cache"] = "HIT"
                yield web.Response(
                        body=decoded_body,
                        status=cached_status,
                        headers=headers,
                    )
                return
            else:
                # url in cache, but out of lifetime
                del d[url]

        async with ClientSession() as session:
            async with session.get(url) as resp:
                body = await resp.read()
                body_b64 = base64.b64encode(body).decode("utf-8")
                headers = CIMultiDict(resp.headers)
                
                headers.pop("Content-Encoding", None)
                headers["X-Cache"] = "MISS"
                headers["Content-Length"] = str(len(body))
                d[url] = (current_time, body_b64, resp.status, dict(resp.headers))
                save_cache(d)
                yield web.Response(
                                body=body,
                                status=resp.status,
                                headers=headers,
                        )

    except Exception as e:
        print(f"Something goes wrong: {e}")
        yield web.Response(
            status=502,
            text=f"Proxy error: {e}",
            headers={"X-Cache": "ERROR"}
        )
