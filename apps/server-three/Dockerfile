FROM python-base

WORKDIR /app

USER verse:verse

COPY --chown=verse:verse apps/server-three/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt


COPY --chown=verse:verse apps/server-three/service.proto ./
RUN python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. service.proto


COPY --chown=verse:verse apps/server-three/app.py ./

CMD ["python", "app.py"]