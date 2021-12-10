FROM node:14.18.1-alpine

WORKDIR /

# Serverless part
COPY serverless.yml ./
COPY package.json ./
COPY package-lock.json ./
RUN npm ci
RUN npm install serverless

COPY . .

EXPOSE 3000
EXPOSE 3002

CMD ["node", "./node_modules/serverless/bin/serverless.js", "offline", "start",  "--host", "0.0.0.0"]