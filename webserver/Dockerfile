###########
# BUILDER #
###########

# pull the official docker image
FROM python:3.10.10-slim AS builder

# set work directory
WORKDIR /app

# set env variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc

# install python dependencies
RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /usr/src/app/wheels -r requirements.txt

##########
# RUNNER #
##########

# pull official base image
FROM python:3.10.10-slim AS runner

# set env variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# create the app user
RUN addgroup --system app && adduser --system --group app

# create the appropriate directories
ENV APP_HOME=/home/app/web
RUN mkdir $APP_HOME
WORKDIR $APP_HOME

# make directories so they would have right permissions
RUN mkdir $APP_HOME/staticfiles
RUN mkdir $APP_HOME/media

# install dependencies
RUN apt-get update && \
    apt-get install -y netcat && \
    rm -rf /var/lib/apt/lists/*

COPY --from=builder /usr/src/app/wheels /wheels
RUN pip install --upgrade pip
RUN pip install --no-cache /wheels/*

# copy project
COPY . $APP_HOME

# give permissions to user 'app'
RUN chown -R app:app $APP_HOME
RUN chmod +x $APP_HOME/entrypoint.sh

# run as user 'app'
USER app

# run entrypoint.sh (wait for db to start and run initial commands)
WORKDIR $APP_HOME/webserver
ENTRYPOINT ["/home/app/web/webserver/entrypoint.sh"]
