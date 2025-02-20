# Train Status Scraper API

A Flask-based API that scrapes train running status information from confirmtkt.com.

## Quick Start with Make

The project includes a Makefile for easy management. Here are the available commands:

```bash
make help         # Show all available commands
make build       # Build the Docker image
make run         # Run the application in foreground
make run-detached # Run the application in background
make stop        # Stop the application
make logs        # View application logs
make clean       # Clean up containers and artifacts
make setup-local # Setup local development environment
```

## Local Setup

1. Setup the local environment:
```bash
make setup-local
```

2. Run the Flask application:
```bash
python src/app.py
```

## Docker Setup (Recommended)

1. Build and run using make:
```bash
make build
make run-detached
```

The server will be available at `http://localhost:5001`

To view logs:
```bash
make logs
```

To stop the service:
```bash
make stop
```

## API Endpoints

### Get Train Status

**Endpoint:** `/train-status`

**Method:** GET

**Query Parameters:**
- `train_number` (required): The train number to check status for
- `day` (optional, default=1): Day selection
  - 1: Today
  - 2: Yesterday
  - 3: 2 days ago
  - 4: 3 days ago
  - 5: Tomorrow

**Example Request:**
```bash
curl "http://localhost:5001/train-status?train_number=12345&day=1"
```

**Example Response:**
```json
{
    "train_number": "12345",
    "current_status": {
        "last_station": "Station Name",
        "next_station": "Next Station",
        "last_updated": "Last Updated Time",
        "delay_status": "On time"
    }
}
```

### Health Check

**Endpoint:** `/health`

**Method:** GET

**Example Request:**
```bash
curl "http://localhost:5001/health"
```

**Example Response:**
```json
{
    "status": "healthy",
    "scraper_initialized": true
}
```

## Error Handling

The API returns appropriate HTTP status codes and error messages:

- 400: Bad Request (invalid parameters)
- 500: Internal Server Error

Error responses include an error message in the response body:
```json
{
    "error": "Error message here"
}
```

## Deployment

1. Clone the repository on your server
2. Install Docker and docker-compose
3. Deploy using make:
```bash
make build
make run-detached
```

## Logs

Logs are stored in the `logs` directory and can be viewed using:
```bash
make logs
``` 