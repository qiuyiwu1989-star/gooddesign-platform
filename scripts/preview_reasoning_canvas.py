#!/usr/bin/env python3
"""推理画布本机预览：在仓库根目录启动只读静态服务，默认端口 8897。"""
import argparse
import functools
import http.server
import os
import socketserver


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8897)
    args = parser.parse_args()
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=root)
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("127.0.0.1", args.port), handler) as httpd:
        print(f"推理画布预览: http://127.0.0.1:{args.port}/extensions/reasoning-canvas/")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    main()
