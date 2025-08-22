FROM node:18-slim

WORKDIR /home/www
COPY ./www /home/


RUN cd ../ && npm install adm-zip && node /home/ho-wrapper.js
RUN cd /home/www && npm install