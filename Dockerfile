# Base Python container image for all Verse Python apps
FROM python:3.11.9-slim-bookworm

RUN addgroup --gid 1001 verse
RUN adduser  --uid 1001 --ingroup verse verse
USER verse:verse

WORKDIR /app

COPY --chown=verse:verse pyproject.toml pyproject.toml
COPY --chown=verse:verse lib/verse/ lib/verse/

COPY --chown=verse:verse requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

RUN pip install --no-cache-dir .[test]
RUN pip install --no-cache-dir .[dev]


# Removed /lib to /app/lib
ENV PYTHONPATH=/app/lib

# Removed .local to /app/lib
ENV VIRTUAL_ENV=/app/.venv

RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN pip install --upgrade pip 
RUN pip install uv
RUN uv pip install -r pyproject.toml
RUN rm pyproject.toml
