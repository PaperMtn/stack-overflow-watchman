# syntax=docker/dockerfile:1

FROM python:3.12-slim-bullseye
COPY . /opt/stack-overflow-watchman
WORKDIR /opt/stack-overflow-watchman
ENV PYTHONPATH=/opt/stack-overflow-watchman
RUN pip3 install poetry
RUN poetry build
RUN python3 -m pip install dist/*.whl
STOPSIGNAL SIGINT
WORKDIR /opt/stack-overflow-watchman
ENTRYPOINT ["stack-overflow-watchman"]