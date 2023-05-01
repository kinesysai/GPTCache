FROM python:3.10-slim

RUN apt-get update && apt-get install -y --no-install-recommends build-essential gcc g++ curl

RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y

ENV PATH="/root/.cargo/bin:${PATH}"
# ENV PYTHONPATH=/usr/lib/python3.11/site-packages

WORKDIR /app


COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN python setup.py install

CMD [ "python", "./gptcache_server/server.py", "--host", "0.0.0.0" ]