FROM node:21.7.1
ARG ENV_FILE
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY $ENV_FILE .env
COPY . .
RUN npm run build
RUN npm install -g serve
EXPOSE 5001
CMD ["serve", "-s", "dist", "-l", "5001"]