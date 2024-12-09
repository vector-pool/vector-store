


## setting up docker

version: '3.8'

services:
  postgres:
    image: postgres:latest
    container_name: postgres-container
    environment:
      POSTGRES_USER: your_username       # Replace with your desired username
      POSTGRES_PASSWORD: your_password     # Replace with your desired password
      POSTGRES_DB: your_database           # Replace with your desired database name
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:


## docker upload 
docker-compose up -d

## create database 

psql -h localhost -U your_username -d your_database




psql -U postgres