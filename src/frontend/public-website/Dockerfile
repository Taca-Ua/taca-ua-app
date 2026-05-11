# Estágio 1: Build
FROM node:22-alpine AS build
WORKDIR /app

# Instalar dependências
COPY src/frontend/public-website/package*.json ./
RUN npm install

# Copiar o código fonte
COPY src/frontend/public-website .

# Gerar o build (Vite vai criar a pasta /app/dist)
RUN npm run build

# Estágio 2: Serve com Nginx leve
FROM nginx:stable-alpine

# Remove a config padrão e copia os arquivos estáticos para a raiz do Nginx
RUN rm -rf /usr/share/nginx/html/*
COPY --from=build /app/dist /usr/share/nginx/html

# Configuração para suportar React Router (SPA) na raiz
RUN echo 'server { \
    listen 80; \
    location / { \
        root /usr/share/nginx/html; \
        index index.html; \
        try_files $uri $uri/ /index.html; \
    } \
}' > /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]