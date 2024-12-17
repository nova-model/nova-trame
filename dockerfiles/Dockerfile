ARG SOURCE_IMAGE=source

FROM --platform=amd64 regproxy.ornl.gov/hub_proxy/python:3.10-slim AS source

# make sure image can run as non-root user
ENV POETRY_CACHE_DIR=/poetry/.cache
ENV POETRY_CONFIG_DIR=/poetry/.config
ENV POETRY_HOME=/poetry

RUN pip install poetry
COPY . /src
WORKDIR /src

RUN apt update && apt install -y wget
RUN install -d -m 0755 /etc/apt/keyrings
RUN wget -q https://packages.mozilla.org/apt/repo-signing-key.gpg -O- | tee /etc/apt/keyrings/packages.mozilla.org.asc > /dev/null
RUN echo "deb [signed-by=/etc/apt/keyrings/packages.mozilla.org.asc] https://packages.mozilla.org/apt mozilla main" | tee -a /etc/apt/sources.list.d/mozilla.list > /dev/null
RUN apt update && apt install -y firefox
RUN mkdir -p /.cache /.mozilla && chmod 777 /.cache /.mozilla

RUN poetry install
RUN poetry build --format=wheel

RUN chmod og+rwX -R /poetry
RUN chmod og+rwX -R /src
