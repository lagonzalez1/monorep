FROM python-base
WORKDIR /app

USER verse:verse

COPY --chown=verse:verse static_data /static_data

COPY --chown=verse:verse apps/server-two/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY --chown=verse:verse apps/server-two/app.py ./


CMD ["python", "app.py"]