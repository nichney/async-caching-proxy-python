from aiohttp import web, ClientSession 
from urllib.parse import urlparse, urlunparse
import argparse

routes = web.RouteTableDef()
DEST = "5.253.41.41" # TODO: get that from cmd
DEST_PORT = "3246"

async def get_back(url: str):
    # url is url of destination
    async with ClientSession() as session:
        async with session.get(url) as resp:

            return web.Response(
                        body= await resp.read(),
                        status=resp.status,
                        headers = resp.headers
                    )

@routes.get("/{tail:.*}")
async def forward(request):
    print(request.url)
    # local_url -> destination_url
    dest_url = urlparse(str(request.url))._replace(netloc=f"{DEST}:{DEST_PORT}")

    return await get_back(dest_url.geturl())

def main():
    #parser = argparse.ArgumentParser()

    app = web.Application()
    app.add_routes(routes)
    web.run_app(app)

if __name__ == '__main__':
    main()
