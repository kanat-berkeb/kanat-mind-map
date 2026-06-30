FROM node:24-alpine AS base

WORKDIR /app

COPY certs/Fortinet_CA_SSL.crt /usr/local/share/ca-certificates/Fortinet_CA_SSL.crt
RUN cat /usr/local/share/ca-certificates/Fortinet_CA_SSL.crt \
      >> /etc/ssl/certs/ca-certificates.crt \
    && apk add --no-cache ca-certificates libc6-compat \
    && update-ca-certificates

ENV SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt
ENV NODE_EXTRA_CA_CERTS=/usr/local/share/ca-certificates/Fortinet_CA_SSL.crt
ENV npm_config_cafile=/etc/ssl/certs/ca-certificates.crt

FROM base AS dependencies

COPY apps/api/package.json apps/api/package-lock.json ./
RUN npm ci

FROM base AS builder

COPY --from=dependencies /app/node_modules ./node_modules
COPY apps/api/ ./

RUN npm run build

FROM base AS runner

ENV NODE_ENV=production
ENV PORT=3001

COPY apps/api/package.json apps/api/package-lock.json ./
RUN npm ci --omit=dev && npm cache clean --force

COPY --from=builder --chown=node:node /app/dist ./dist

USER node

EXPOSE 3001

CMD ["node", "dist/main.js"]
