# web/Dockerfile (multi-stage)

# Builder stage
FROM node:18-alpine AS builder

WORKDIR /app

# Install dependencies and build the application
COPY package.json package-lock.json ./
RUN npm ci

COPY . .
ENV NEXT_TELEMETRY_DISABLED 1
RUN npm run build

# Runtime stage
FROM node:18-alpine AS runtime

WORKDIR /app
ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED 1

# Install only production dependencies
COPY package.json package-lock.json ./
RUN npm ci --omit=dev && npm cache clean --force

# Copy build output
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/next.config.js ./next.config.js

# Run as non-root user
RUN chown -R node:node /app
USER node

EXPOSE 3000

CMD ["npm", "start"]
