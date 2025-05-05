@echo off
echo Starting the application...

echo Removing old containers and images...
docker-compose down -v

echo Building and starting new containers...
docker-compose up -d --build

echo Application started successfully.