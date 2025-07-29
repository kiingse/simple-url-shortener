# URL Shortener

A simple URL shortening tool built with FastAPI, PostgreSQL and Docker. This tool allows you to create shortened URLs and manage redirects efficiently.

## Features

- Shorten long URLs to easily shareable links
- Configure the length of shortened URLs in .env
- RESTful API for easy integration
- Containerized with Docker for simple deployment
- Optimized Docker image using multistage building


## Tech Stack

- **Backend**: Python 3.12, FastAPI, Pydantic
- **Database**: PostgreSQL 17.5
- **ORM**: SQLAlchemy
- **Dependency Management**: Poetry
- **Containerization**: Docker, Docker Compose


## Prerequisites

- Docker and Docker Compose installed on your system
- Git (for cloning the repository)


## Getting Started

### Clone the Repository

```bash
git clone <repository-url>
cd url-shortener
```

### Running the Application

Start the application using Docker Compose:

```bash
docker compose up --build
```

The API will be available at `http://localhost:8000`. See `http://localhost:8000/docs` for docs in OpenAPI schema.

## API Endpoints

### Shorten a URL

Provide the URL to be shortened as a query parameter `original_url`.

E.g.
```
POST /api/v1/short-url?original_url=https%3A%2F%2Fexample.com%2Fvery%2Flong%2Furl%2Fthat%2Fneeds%2Fshortening

Response:
{
  "short_url": "http://localhost:8000/api/v1/DiAYfM"
}
```


### Access a Shortened URL

```
GET /{short_code}

e.g. GET api/v1/DiAYfM

Response:
{
  "original_url": "https://example.com/very/long/url/that/needs/shortening"
}
```


### Healthcheck

```
GET /api/v1/healthcheck

Response:
{
  "status": "OK",
  "database": "connected"
}
```

## Development

### Running Tests

After starting the container, tests can be run using a simple script `./run_test.sh`. The tests utilize [testcontainers](https://testcontainers-python.readthedocs.io/en/latest/) and the [Schemathesis](https://schemathesis.readthedocs.io/en/stable/index.html) tool.


### Database Migrations

Database migrations are handled automatically using Alembic when the container starts.


## Additional info
Since this is a REST API, there is no direct redirection using e.g. RedirectResponse, but rather a JSON format response:

```json
{
  "original_url": "https://example.com/"
}
```
For this reason, the URL includes `/api/v1`. This is intentional.


## License
MIT
