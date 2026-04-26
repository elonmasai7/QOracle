FROM node:20-alpine AS build
WORKDIR /app
COPY frontend/package.json frontend/package-lock.json frontend/tsconfig.json frontend/vite.config.ts frontend/tailwind.config.ts frontend/postcss.config.js frontend/index.html ./
COPY frontend/src ./src
RUN npm install && npm run build

FROM nginx:1.27-alpine
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
