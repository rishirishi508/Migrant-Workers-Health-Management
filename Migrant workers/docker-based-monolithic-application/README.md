
# Docker Based Monolithic Application
### Digital Health Record Management System for Migrant Workers
---

##  Project Overview
The Digital Health Record Management System (DHRMS) for Migrant Workers is a web-based application designed to store and manage migrant workers’ health records digitally with secure, role-based access.

This project is built using a 3-tier architecture with a multi-service backend, orchestrated using Docker Compose on a Linux environment, following DevOps best practices.

The system enables location-independent access to health records, ensuring continuity of medical information for migrant workers as they move between regions.

---

##  Project Goals
- Build a modular multi-service application
- Use Linux as the primary operating system
- Containerize application services using Docker
- Orchestrate services using Docker Compose
- Implement role-based access control
- Apply DevOps practices for deployment and configuration

##  Tech Stack (DevOps Focused)


###  Frontend
- HTML, CSS, JavaScript  

###  Backend
- Python (Flask / FastAPI)
- REST APIs

###  Database
- MySQL

###  Containerization
- Docker
- Docker Compose (local setup)

###  Version Control
- Git & GitHub

---

##  Containerization Strategy

- Each service has its own `Dockerfile`
- Services are deployed as independent containers
- Environment variables used for configuration
- Containers run as non-root users

---

##  Deployment Flow
- Source code is pushed to GitHub
- Each service contains its own Dockerfile
- Docker images are built locally
- Docker Compose orchestrates and starts all services
- Services communicate with each other over a private Docker network
- Frontend accesses backend services through exposed ports

---

##  Local Development

```bash
git clone https://github.com/rishirishi508/Migrant-Workers-Health-Management.git
cd docker-based-monolithic-application
docker-compose up --build
