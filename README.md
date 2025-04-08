# Caching proxy

https://roadmap.sh/projects/caching-server

## Usage

```
caching-proxy --port <number> --origin <url>
```

- --port is the port on which the caching proxy server will run.
- --origin is the URL of the server to which the requests will be forwarded.

For example, if the user runs the following command:

```
caching-proxy --port 3000 --origin http://dummyjson.com
```

The caching proxy server should start on port 3000 and forward requests to http://dummyjson.com.

## Clearing cache

```
caching-proxy --clear-cache
```

