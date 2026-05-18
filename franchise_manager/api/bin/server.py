import os

from franchise_manager.api.server.server import franchise_manager_api
from franchise_manager.api.server.middleware import cors, proxy_headers
from franchise_manager.api.server.router import Router
from franchise_manager.api.endpoint.system import health


# #
# server

server = franchise_manager_api()

# middleware
server.middleware(cors())
server.middleware(proxy_headers())

# router
server.router(
    Router(path="/health", methods=["GET"], endpoint=health)
)

# app
app = server.app()


# #
# Run

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app="franchise_manager.api.bin.server:app",
        host=str(os.environ["DEVELOP_API_HOST"]),
        port=int(os.environ["DEVELOP_API_CONTAINER_PORT"]),
        reload=True,
    )
