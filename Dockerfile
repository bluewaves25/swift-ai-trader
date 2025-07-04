FROM node:18
WORKDIR /app
COPY backend/package*.json ./backend/
RUN cd backend && npm install
COPY backend/ ./backend/
RUN apt-get update && apt-get install -y python3 python3-pip
RUN pip3 install -r backend/requirements.txt
EXPOSE 3000
WORKDIR /app/backend/src
CMD ["npm", "run", "dev"]