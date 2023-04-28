import argparse
import http.server
import json
import os

from gptcache import cache
from gptcache.adapter.api import get, put
from gptcache.processor.pre import get_prompt
from gptcache.manager import get_data_manager, CacheBase, VectorBase
# from gptcache.embedding import OpenAI as EmbeddingOpenAI
from gptcache.embedding import Onnx as EmbeddingOnnx
from gptcache.utils.log import gptcache_log

class GPTCacheHandler(http.server.BaseHTTPRequestHandler):
    # curl -X GET  "http://localhost:8000?prompt=hello"
    def do_GET(self):
        params = self.path.split("?")[1]
        prompt = params.split("=")[1]

        result = get(prompt)

        response = json.dumps(result)

        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(bytes(response, "utf-8"))

    # curl -X PUT -d "receive a hello message" "http://localhost:8000?prompt=hello"
    def do_PUT(self):
        params = self.path.split("?")[1]
        prompt = params.split("=")[1]
        content_length = int(self.headers.get("Content-Length", "0"))
        data = self.rfile.read(content_length).decode("utf-8")

        put(prompt, data)

        self.send_response(200)
        self.end_headers()


def start_server(host: str, port: int):
    httpd = http.server.HTTPServer((host, port), GPTCacheHandler)
    print(f"Starting server at {host}:{port}")
    httpd.serve_forever()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="localhost", help="the hostname to listen on")
    parser.add_argument("--port", type=int, default=8000, help="the port to listen on")
    args = parser.parse_args()

    # set logger
    gptcache_log.setLevel("INFO")

    # embeddings
    # embeddings = EmbeddingOpenAI()
    embeddings = EmbeddingOnnx()

    sql_url = os.getenv("POSTGRE_URI")
    if sql_url is None:
        raise EnvironmentError("POSTGRE_URI env not found")
    
    milvus_host = os.getenv("MILVUS_HOST")
    milvus_port = os.getenv("MILVUS_PORT")
    if milvus_host is None or milvus_port is None:
        raise EnvironmentError("MILVUS_HOST or/and MILVUS_PORT env not found")

    # sql_url = 'postgresql://postgres:admin@localhost:5433/gptcache'
    scalar_store = CacheBase(name='postgresql', sql_url=sql_url)
    vector_base = VectorBase('milvus', host=milvus_host, port=milvus_port, dimension=embeddings.dimension)
    data_manager = get_data_manager(scalar_store, vector_base)
    cache.init(
        pre_embedding_func=get_prompt,
        data_manager=data_manager,
        embedding_func=embeddings.to_embeddings
    )

    start_server(args.host, args.port)
