#!/bin/sh

export POSTGRE_URI=postgresql://postgres:admin@localhost:5433/gptcache
export MILVUS_HOST=localhost
export MILVUS_PORT=19530

python gptcache_server/server.py
