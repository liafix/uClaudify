from .protocol import McpProtocolServer
from .runtime import build_seeded_operations_service


if __name__ == "__main__":
    McpProtocolServer(build_seeded_operations_service()).serve_stdio()
