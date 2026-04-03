ARG IMAGE_TAG="3.14.5-slim-trixie"
FROM python:$IMAGE_TAG AS builder

ARG POETRY_VERSION=2.4.1
ENV POETRY_VIRTUALENVS_CREATE=false
ENV POETRY_NO_INTERACTION=1
ENV POETRY_CACHE_DIR=/tmp/poetry_cache

COPY pyproject.toml poetry.lock ./

RUN pip install --no-cache-dir "poetry==$POETRY_VERSION" && \
    poetry install --no-root --only main

FROM python:$IMAGE_TAG AS runner

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONFAULTHANDLER=1
ENV BINPATH="/usr/local/bin"
ENV PYTHONPATH="/usr/local/lib/python3.14/site-packages"
ENV APP_PATH=/app

RUN mkdir -p $APP_PATH/src && \
    addgroup --system app_group && \
    adduser --system --ingroup app_group app_user && \
    chown -v -R app_user:app_group $APP_PATH

USER app_user
WORKDIR $APP_PATH

COPY --from=builder /usr/local/lib/python3.14/site-packages ${PYTHONPATH}
COPY --from=builder /usr/local/bin/alembic ${BINPATH}/alembic
COPY --from=builder /usr/local/bin/uvicorn ${BINPATH}/uvicorn
COPY --chown=app_user:app_group entrypoint.sh alembic.ini ./
COPY --chown=app_user:app_group src src

WORKDIR $APP_PATH

# check entrypoint to ensure they match
EXPOSE 8080
ENTRYPOINT ["./entrypoint.sh"]
