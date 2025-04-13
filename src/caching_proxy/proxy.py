from aiohttp import web
from urllib.parse import urlparse, urlunparse
import argparse
from os import remove
import sys

from .cache import cache_session_manager


routes = web.RouteTableDef()
DEST = "" 
DEST_PORT = ""

@routes.get("/{tail:.*}")
async def forward(request):
    print(request.url)
    # local_url -> destination_url
    dest_url = urlparse(str(request.url))._replace(netloc=f"{DEST}:{DEST_PORT}")

    async with cache_session_manager(dest_url.geturl()) as r:
        return r


def setup_values(args):
    ### seems bad
    global DEST
    global DEST_PORT
    ###
    if args.clear_cache:
        try:
            remove("proxy_cache")
            print("Cache clear now!")
        except FileNotFoundError:
            print("Cache already empty!")
        finally:
            sys.exit() # terminate app

    if not args.origin:
        raise ValueError
    DEST_PORT = args.port
    DEST = args.origin


def main():
    try:
        parser = argparse.ArgumentParser(
                    prog='caching-proxy',
                    description="CLI caching proxy server"
                )
        parser.add_argument("--origin", help="Origin url")
        parser.add_argument("--port", help="Origin port", default="80")
        parser.add_argument("--clear-cache", action="store_true", help="Clear local cache")
        parser.set_defaults(func=setup_values)
        args = parser.parse_args()
        args.func(args)

        app = web.Application()
        app.add_routes(routes)
        web.run_app(app)
    except ValueError:
        print("Oops! It seems like you haven't specify origin")
        print("Use --help to see usage")

if __name__ == '__main__':
    main()
