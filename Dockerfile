FROM python:2-stretch

WORKDIR /usr/src/app

# Install postgres
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# install requirements
# this way when you build you won't need to install again
# and since COPY is cached we don't need to wait
COPY conf/requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

# Copy the Configuration and the Scripts
COPY conf /conf
COPY scripts /usr/src/scripts
RUN chmod a+x /usr/src/scripts/runserver.sh
RUN pip install django-grappelli
RUN pip install lxml
RUN pip install django-jet
# Copy the source.
COPY src /usr/src/app

WORKDIR /usr/src/app/PyGeon

# App port number is configured through the gunicorn config file
ENTRYPOINT ["/usr/src/scripts/runserver.sh"]
