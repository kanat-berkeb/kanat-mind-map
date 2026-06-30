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

COPY apps/web/package.json apps/web/package-lock.json ./
RUN npm ci

FROM base AS builder

ENV NEXT_TELEMETRY_DISABLED=1

COPY --from=dependencies /app/node_modules ./node_modules
COPY apps/web/ ./

ARG NEXT_PUBLIC_API_BASE_URL=http://localhost:3001
ENV NEXT_PUBLIC_API_BASE_URL=${NEXT_PUBLIC_API_BASE_URL}

RUN npm run build

FROM base AS runner

ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1
ENV HOSTNAME=0.0.0.0
ENV PORT=3000

COPY --from=builder --chown=node:node /app/public ./public
COPY --from=builder --chown=node:node /app/.next/standalone ./
COPY --from=builder --chown=node:node /app/.next/static ./.next/static

USER node

EXPOSE 3000

CMD ["node", "server.js"]
