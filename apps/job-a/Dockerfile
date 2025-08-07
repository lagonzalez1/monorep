FROM python-base


WORKDIR /app

USER verse:verse

COPY --chown=verse:verse static_data /static_data
COPY --chown=verse:verse apps/job-a/requirements.txt ./
    
RUN pip install --no-cache-dir -r requirements.txt

COPY --chown=verse:verse apps/job-a/app.py ./


CMD ["python", "app.py"]
