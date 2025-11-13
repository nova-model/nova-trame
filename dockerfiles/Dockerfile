ARG SOURCE_IMAGE=source

FROM --platform=amd64 python:3.10-slim AS source

RUN apt update && apt install -y curl wget
RUN install -d -m 0755 /etc/apt/keyrings
RUN wget -q https://packages.mozilla.org/apt/repo-signing-key.gpg -O- | tee /etc/apt/keyrings/packages.mozilla.org.asc > /dev/null
RUN echo "deb [signed-by=/etc/apt/keyrings/packages.mozilla.org.asc] https://packages.mozilla.org/apt mozilla main" | tee -a /etc/apt/sources.list.d/mozilla.list > /dev/null
RUN apt update && apt install -y firefox
RUN mkdir -p /.cache /.mozilla && chmod 777 /.cache /.mozilla

COPY . /src
WORKDIR /src

RUN curl -fsSL https://pixi.sh/install.sh | sh
ENV PATH="/root/.pixi/bin:${PATH}"
RUN pixi install
SHELL [ "pixi", "run" ]
ENTRYPOINT [ "pixi", "run" ]

RUN chmod og+rwX -R /src /.cache /.mozilla

FROM --platform=amd64 python:3.10-slim AS package

RUN apt update && apt install -y curl

COPY . /src
WORKDIR /src

RUN curl -fsSL https://pixi.sh/install.sh | sh
ENV PATH="/root/.pixi/bin:${PATH}"
RUN pixi install -e production
SHELL [ "pixi", "run" ]
ENTRYPOINT [ "pixi", "run" ]

RUN chmod og+rwX -R /src
