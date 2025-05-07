FROM node:18

WORKDIR /frontend

COPY package.json .

RUN yarn install

COPY . .

CMD ["yarn", "dev"]