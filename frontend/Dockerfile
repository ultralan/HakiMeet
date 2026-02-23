FROM node:20-alpine AS build

WORKDIR /app

COPY package.json ./

# 使用淘宝 npm 镜像
RUN npm config set registry https://registry.npmmirror.com && npm install

COPY . .
RUN npm run build

# --- 生产镜像 ---
FROM nginx:alpine

# 复制构建产物
COPY --from=build /app/dist /usr/share/nginx/html

# 自定义 nginx 配置（反向代理后端 API）
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
