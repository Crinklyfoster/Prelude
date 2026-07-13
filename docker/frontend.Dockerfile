FROM node:22-alpine AS builder

WORKDIR /app

ARG NEXT_PUBLIC_API_URL
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL

COPY frontend/package*.json ./

RUN npm ci --ignore-scripts

COPY frontend .

RUN npm run build

FROM node:22-alpine AS runtime

WORKDIR /app

COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
COPY --from=builder /app/public ./public

EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD wget --spider http://localhost:3000 || exit 1

RUN chown -R node:node /app

USER node

CMD ["node", "server.js"]