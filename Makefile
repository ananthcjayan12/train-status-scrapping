.PHONY: build build-no-cache run run-detached stop logs clean test help pull init

# Default target
help:
	@echo "Available commands:"
	@echo "  make pull         - Pull required Docker images"
	@echo "  make build        - Build the Docker image (with cache)"
	@echo "  make build-no-cache - Build the Docker image (without cache)"
	@echo "  make run          - Run the application in foreground"
	@echo "  make run-detached - Run the application in background"
	@echo "  make stop         - Stop the running application"
	@echo "  make logs         - View application logs"
	@echo "  make clean        - Remove containers and local artifacts"
	@echo "  make setup-local  - Setup local development environment"
	@echo "  make help         - Show this help message"

# Pull required Docker images
pull:
	docker pull python:3.11-slim

# Build the Docker image with cache
build: pull
	docker-compose build

# Build the Docker image without cache
build-no-cache: pull
	for i in 1 2 3; do \
		docker-compose build --no-cache && break || { \
			echo "Retry $$i..."; \
			sleep 5; \
		} \
	done

# Run the application in foreground
run:
	docker-compose up

# Run the application in background
run-detached:
	docker-compose up -d

# Stop the application
stop:
	docker-compose down

# View logs
logs:
	docker-compose logs -f

# Clean up
clean:
	docker-compose down -v
	rm -rf logs/*
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -type f -name "*.pyc" -delete
	docker system prune -f

# Setup local development environment
setup-local:
	python3 -m venv venv
	. venv/bin/activate && pip install -r requirements.txt
	mkdir -p logs

# Create necessary directories
init:
	mkdir -p logs 