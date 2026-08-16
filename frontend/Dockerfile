# syntax=docker/dockerfile:1.7
FROM node:22-alpine AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN --mount=type=cache,id=lien-quan-npm-cache,target=/root/.npm \
    npm ci --cache /root/.npm --prefer-offline

FROM node:22-alpine AS builder
WORKDIR /app
ARG NEXT_PUBLIC_API_URL
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL
ARG BACKEND_API_URL=http://backend:8000
ENV BACKEND_API_URL=$BACKEND_API_URL
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN --mount=type=cache,id=lien-quan-next-cache,target=/app/.next/cache \
    npm run build

FROM node:22-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
RUN addgroup -S app && adduser -S app -G app
COPY --from=builder --chown=app:app /app/public ./public
COPY --from=builder --chown=app:app /app/.next/standalone ./
COPY --from=builder --chown=app:app /app/.next/static ./.next/static
USER app
EXPOSE 3000
CMD ["node", "server.js"]
