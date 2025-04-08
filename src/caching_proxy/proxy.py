from aiohttp import web
from urllib.parse import urlparse, urlunparse
import argparse

import cache


routes = web.RouteTableDef()
DEST = "" 
DEST_PORT = ""


async def get_back(url: str):
    # url is url of destination
    async with cache.cache_session_manager(url) as r:
        return r


@routes.get("/{tail:.*}")
async def forward(request):
    print(request.url)
    # local_url -> destination_url
    dest_url = urlparse(str(request.url))._replace(netloc=f"{DEST}:{DEST_PORT}")

    return await get_back(dest_url.geturl())

def setup_values(args):
    ### seems bad
    global DEST
    global DEST_PORT
    ###
    if args.clear_cache:
        #TODO: add cache clearing
        pass

    if not args.origin:
        raise ValueError
    DEST_PORT = args.port
    DEST = args.origin
    print(f"DEST={DEST}, DEST_PORT={DEST_PORT}")


def main():
    try:
        parser = argparse.ArgumentParser(
                    prog='caching-proxy',
                    description="CLI caching proxy server"
                )
        parser.add_argument("--origin", help="Origin url")
        parser.add_argument("--port", help="Origin port", default="80")
        parser.add_argument("--clear-cache", help="Clear local cache")
        parser.set_defaults(func=setup_values)
        args = parser.parse_args()
        args.func(args)

        app = web.Application()
        app.add_routes(routes)
        web.run_app(app)
    except ValueError:
        print("Oops! It seems like you haven't specify origin")

if __name__ == '__main__':
    main()
