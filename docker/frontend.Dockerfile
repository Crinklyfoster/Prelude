FROM node:22-alpine

WORKDIR /app

COPY frontend/package*.json ./

RUN npm ci

COPY frontend .

RUN npm run build

EXPOSE 3000

RUN adduser --disabled-password --gecos "" nextuser

USER nextuser

CMD ["npm", "run", "start"]