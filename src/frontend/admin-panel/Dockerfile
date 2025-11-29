FROM node:22-alpine
WORKDIR /app
COPY src/frontend/admin-panel/package*.json ./
RUN npm install
COPY src/frontend/admin-panel .
CMD ["npm", "run", "dev", "--", "--host"]
