# Estágio 1: Build
FROM node:22-alpine AS build
WORKDIR /app

# Instalar dependências
COPY src/frontend/admin-panel/package*.json ./
RUN npm install

# Copiar o código fonte
COPY src/frontend/admin-panel .

# Gerar o build (Vite vai criar a pasta /app/dist)
RUN npm run build

# Estágio 2: Serve com Nginx leve
FROM nginx:stable-alpine

# IMPORTANTE: Como usas base: '/admin/', o Nginx precisa de servir 
# os ficheiros dentro dessa pasta para que as rotas funcionem.
RUN mkdir -p /usr/share/nginx/html/admin

# Copia os ficheiros estáticos do estágio anterior para a subpasta admin
COPY --from=build /app/dist /usr/share/nginx/html/admin/

# Copia uma configuração mínima de Nginx para lidar com Single Page Application (SPA)
# Isso evita erros 404 ao dar refresh em sub-rotas do React
RUN echo 'server { \
    listen 80; \
    location /admin/ { \
        root /usr/share/nginx/html; \
        index index.html; \
        try_files $uri $uri/ /admin/index.html; \
    } \
}' > /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]