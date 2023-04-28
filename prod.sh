#!/bin/sh

export POSTGRE_URI=postgresql://postgres:admin@localhost:5433/gptcache
export MILVUS_HOST=https://in01-bdebd937604978b.aws-us-west-2.vectordb.zillizcloud.com
export MILVUS_PORT=19535

python gptcache_server/server.py
