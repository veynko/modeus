FROM python:3.12.6-slim AS builder

WORKDIR /bot

RUN apt-get update
# RUN apt-get update && \
#     apt-get install -y --no-install-recommends gcc

COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip \
    pip wheel --wheel-dir /bot/wheels -r requirements.txt

FROM python:3.12.6-slim

WORKDIR /bot

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY --from=builder /bot/wheels /bot/wheels
COPY --from=builder /bot/requirements.txt .
RUN pip install --no-cache /bot/wheels/*

COPY src .

RUN addgroup --system app && adduser --system --group app
USER app

ENTRYPOINT ["python3", "main.py"]
CMD [ "args" ]