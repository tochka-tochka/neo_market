FROM node:22-alpine AS base
WORKDIR /app/frontend
COPY package*.json ./

FROM base AS builder
RUN npm ci
COPY . .
RUN npm run build

FROM node:22-alpine AS prod
WORKDIR /app/frontend

COPY --from=builder /app/frontend/build ./build 
COPY --from=builder /app/frontend/package.json ./package.json
COPY --from=builder /app/frontend/node_modules ./node_modules

EXPOSE 3000
CMD ["node", "build/index.js"]