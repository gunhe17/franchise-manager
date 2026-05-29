import os

from franchise_manager.api.server.server import franchise_manager_api
from franchise_manager.api.server import middleware
from franchise_manager.api.server.router import Router
from franchise_manager.api.endpoint import system
from franchise_manager.api.server import exception


# #
# server

server = franchise_manager_api()

# middleware
server.middleware(middleware.cors())
server.middleware(middleware.proxy_headers())

# #
# router
server.router(
    Router(path="/health", methods=["GET"], endpoint=system.health)
)
# dev
server.router(
    Router(path="/dev/domain-map", methods=["GET"], endpoint=system.domain_map_page)
)
server.router(
    Router(path="/dev/domain-map/data", methods=["GET"], endpoint=system.domain_map_data)
)

# exception handler
server.exception_handler(exception.client())
server.exception_handler(exception.develop())

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