FROM python-base as base

WORKDIR /app

USER verse:verse

COPY --chown=verse:verse apps/server-one/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY --chown=verse:verse apps/server-one/app.py ./
CMD ["python", "app.py"]

FROM base AS test


WORKDIR /app
COPY apps/server-one/tests ./

RUN python -m pytest tests