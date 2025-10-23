# Build stage
FROM node:20-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm i

# Copy source code
COPY . .

# Runtime stage
FROM node:20-alpine

WORKDIR /app

# Install only production dependencies
COPY package*.json ./
RUN npm i --only=production

# Copy built application from builder
COPY --from=builder /app/src ./src
COPY --from=builder /app/tsconfig.json ./

# Install tsx for running TypeScript directly
RUN npm install -g tsx

# Expose the A2A server port
EXPOSE 9000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \
  CMD node -e "require('http').get('http://localhost:9000/.well-known/agent-card.json', (r) => {process.exit(r.statusCode === 200 ? 0 : 1)})"

# Start the A2A server
CMD ["tsx", "src/a2a-server.ts"]
