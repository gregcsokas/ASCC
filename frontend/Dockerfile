FROM node:24.15-alpine AS build
WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .
RUN npm run build

RUN mkdir -p /app/out && cp -r dist/*/browser/* /app/out/

FROM nginx:alpine AS runtime
COPY --from=build /app/out /usr/share/nginx/html
COPY nginx/default.conf.template /etc/nginx/templates/default.conf.template
