FROM node:22-alpine
WORKDIR /app
COPY src/frontend/public-website/package*.json ./
RUN npm install
COPY src/frontend/public-website .
CMD ["npm", "run", "dev", "--", "--host"]
