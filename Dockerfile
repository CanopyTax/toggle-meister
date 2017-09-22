FROM python:alpine

ENV PYCURL_SSL_LIBRARY=openssl \
    PYTHONPATH=. \
    DOCKER=True

# compile requirements for some python libraries
RUN apk --no-cache add curl-dev bash postgresql-dev \
    gcc make libffi-dev musl-dev musl-utils && \
    python3 -m pip install gunicorn "invoke==0.13.0" alembic

# install python reqs
COPY requirements.txt /app/
WORKDIR /app

RUN export PYCURL_SSL_LIBRARY=openssl && \
    pip3 install -r requirements.txt --user -U


# build frontend
COPY tmeister/static /app/tmeister/static
RUN apk --no-cache add nodejs git && \
    cd /app/tmeister/static && \
    npm install && \
    npm run postinstall && \
    npm run build && \
    apk --no-cache del nodejs git && \
    rm -rf node_modules spec src bin &&  \
    cd /app


EXPOSE 8445
CMD ["dumb-init", "startup.sh"]
COPY . /app
