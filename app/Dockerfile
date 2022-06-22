
# ========= BUILD =========
FROM node:16-alpine as builder

ENV NODE_OPTIONS --max_old_space_size=512
WORKDIR /app

RUN npm install tsc -g
COPY package.json .
COPY package-lock.json .
RUN npm install --only=production

COPY . .

RUN npm run build

# ========= RUN =========
FROM nginx:1.21-alpine as production
ENV NODE_ENV production
COPY --from=builder /app/build /usr/share/nginx/html
COPY conf/nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
