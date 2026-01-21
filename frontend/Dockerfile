# 使用 Node LTS
FROM node:20-alpine

WORKDIR /app

# 安装依赖（使用 package-lock 或 pnpm 的话可改命令）
COPY frontend/package*.json ./
# 如果使用 pnpm 或 yarn，请调整以下命令
RUN npm ci --omit=dev

# 复制其余前端源码
COPY frontend/ ./

# 构建 Next.js 应用（需在 package.json 中有 build 脚本）
ENV NODE_ENV=production
RUN npm run build

# 运行 Next.js
# 默认 Next.js 使用 3000 端口
EXPOSE 3000
CMD ["npm", "run", "start"]