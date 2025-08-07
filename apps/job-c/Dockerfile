FROM python-base


WORKDIR /app

USER verse:verse

COPY --chown=verse:verse static_data /static_data
    
COPY --chown=verse:verse apps/job-c/app.py ./


CMD ["python", "app.py"]
