# Intellectual Systems Project

## Overview
This project demonstrates a client-server architecture using Python's asyncio for communication over TCP. It includes a server handling incoming "PING" messages from clients and optionally responding with "PONG".

## Requirements
- Python 3.10+
- Docker

## Setup
To run the server and clients:
1. Clone the repository `https://github.com/adzheliev/Intellectual-systems.git`
2. Build Docker images: `docker-compose build`
3. Start services: `docker-compose up`

## Features
- **Server:** Listens on TCP, processes "PING", responds with "PONG".
- **Clients:** Send periodic "PING" messages.
- **Logging:** Activities are logged for monitoring purposes.

## Docker Configuration
Utilizes Docker Compose for managing containerized services, ensuring seamless network setup for communication between server and clients.

Check `Dockerfile` and `docker-compose.yml` for detailed configurations.
