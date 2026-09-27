# Docker Compose Basic Project: 
Python Flask + Redis
 
**Services:** Flask web application and Redis

In this hands-on project, you will deploy a Python Flask web application and a Redis database using Docker Compose. The Flask application displays a welcome message and counts page visits.

## 1. Project architecture

```text
              User / Browser
          http://localhost:5000
                    |
                    v
        +-----------------------+
        | Docker Compose        |
        |                       |
        | Flask web container   |
        | Host port: 5000       |
        |                       |
        |  app-network          |
        |          |            |
        |          v            |
        | Redis container       |
        | Internal port: 6379   |
        |          |            |
        |          v            |
        | redis-data volume     |
        +-----------------------+
```

## 2. Prerequisites

- Docker Engine or Docker Desktop
- Docker Compose v2 (`docker compose version`)
- Port 5000 available on your computer

## 3. Create the project

```bash
mkdir docker-compose-project
cd docker-compose-project

touch app.py requirements.txt Dockerfile compose.yaml
```

Project structure:

```text
docker-compose-project/
├── app.py
├── requirements.txt
├── Dockerfile
└── compose.yaml
```

## 4. Create the Flask application

Add the following code to `app.py`:

```python
from flask import Flask
import redis
import os

app = Flask(__name__)

r = redis.Redis(
    host=os.getenv("REDIS_HOST", "redis"),
    port=6379,
    decode_responses=True
)

@app.route("/")
def home():
    count = r.incr("visits")

    return f"""
    <h1>Welcome to Docker Compose!</h1>
    <h2>Cloudnautic Flask Application</h2>
    <p>Page Visits: {count}</p>
    """

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
```

## 5. Create requirements.txt

```text
flask==3.1.1
redis==6.2.0
```

## 6. Create the Dockerfile

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

EXPOSE 5000

CMD ["python", "app.py"]
```

## 7. Create compose.yaml

```yaml
services:
  web:
    build: .
    ports:
      - "5000:5000"
    environment:
      REDIS_HOST: redis
    depends_on:
      redis:
        condition: service_healthy
    networks:
      - app-network

  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes
    volumes:
      - redis-data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 3s
      retries: 5
    networks:
      - app-network

networks:
  app-network:
    driver: bridge

volumes:
  redis-data:
```

**How it works:** Compose builds the `web` image from the Dockerfile, starts Redis, waits until its health check succeeds, then starts Flask. The web service reaches Redis using the hostname `redis` on the Compose network. The named volume preserves Redis data between container recreations.

## 8. Build and run the project

From the project directory:

```bash
docker compose config
docker compose up -d --build
docker compose ps
```

Open <http://localhost:5000> in your browser. Expected output:

```text
Welcome to Docker Compose!
Cloudnautic Flask Application
Page Visits: 1
```

Refresh the page to increase the visit counter.

## 9. Docker Compose practice commands

| Operation | Command |
|---|---|
| Build and start | `docker compose up -d --build` |
| List services | `docker compose ps` |
| Follow logs | `docker compose logs -f` |
| View Flask logs | `docker compose logs web` |
| Stop services | `docker compose stop` |
| Restart services | `docker compose restart` |
| Access Redis CLI | `docker compose exec redis redis-cli` |
| Stop and remove containers and network | `docker compose down` |
| Also delete named volumes | `docker compose down -v` |

**Scaling note:** `docker compose up -d --scale web=2` will conflict with the fixed host-port mapping `5000:5000`. To scale Flask, remove the fixed host-port mapping and use a reverse proxy/load balancer or assign distinct published ports.

## 10. Test Redis

```bash
docker compose exec redis redis-cli
```

At the Redis prompt:

```redis
GET visits
```

After one page visit, the expected result is:

```text
"1"
```

Type `exit` to leave the Redis CLI.

## 11. Test persistent storage

Stop and remove the containers **without deleting the volume**:

```bash
docker compose down
```

Start again:

```bash
docker compose up -d
```

Refresh the application. The counter should continue from its previous value because Redis uses a named volume and append-only persistence.

To completely clean up the project **including its stored data**:

```bash
docker compose down -v
```

## 12. Troubleshooting

- **Port 5000 already in use:** Change the published port to `5001:5000`, then browse to <http://localhost:5001>.
- **Flask cannot reach Redis:** Check `docker compose ps`, `docker compose logs redis`, and confirm `REDIS_HOST: redis`.
- **App not responding:** Run `docker compose logs web` and check for Python errors.
- **Counter resets after cleanup:** `docker compose down -v` deletes the named Redis volume; use `docker compose down` to preserve it.

## Learning outcomes

By completing this project, students practice multi-container applications, image builds, service discovery, container networking, environment variables, health checks, named volumes, and the Docker Compose lifecycle.
