# pull the official docker image
FROM node:19-alpine
ENV NODE_ENV="development"

# create the appropriate directories
ENV APP_HOME=/home/app/web
RUN mkdir -p $APP_HOME
WORKDIR $APP_HOME

COPY package*.json ./

# install dependencies
RUN npm install
# RUN npm ci --only=production

# copy project
COPY . .
