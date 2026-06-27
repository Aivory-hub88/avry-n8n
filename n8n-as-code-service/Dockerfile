FROM node:18-alpine

WORKDIR /app

# Copy dependency manifests if they exist, then install
COPY package*.json ./
RUN if [ -f package.json ]; then npm install --production; fi

# Pull in the service runtime source code
COPY . .

# Expose the service port designated in your compose config
EXPOSE 3500

CMD ["node", "index.js"]
