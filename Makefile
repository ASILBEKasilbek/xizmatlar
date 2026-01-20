# Makefile for Xizmatlar Bot
# Qulaylik uchun command shortcuts

.PHONY: help install run test clean docker-up docker-down logs db-init

# Default target
help:
	@echo "Xizmatlar Bot - Available Commands:"
	@echo ""
	@echo "  make install     - Install dependencies"
	@echo "  make run         - Run bot locally"
	@echo "  make test        - Run tests"
	@echo "  make clean       - Clean up files"
	@echo "  make docker-up   - Start with Docker"
	@echo "  make docker-down - Stop Docker containers"
	@echo "  make logs        - View bot logs"
	@echo "  make db-init     - Initialize database"
	@echo ""

# Install dependencies
install:
	@echo "Installing dependencies..."
	pip install -r requirements.txt
	@echo "Done!"

# Run bot
run:
	@echo "Starting bot..."
	python main.py

# Run tests
test:
	@echo "Running tests..."
	python test_bot.py

# Clean up
clean:
	@echo "Cleaning up..."
	find . -type d -name __pycache__ -exec rm -r {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.log" -delete
	@echo "Cleaned!"

# Docker commands
docker-up:
	@echo "Starting Docker containers..."
	docker-compose up -d
	@echo "Bot started in Docker!"

docker-down:
	@echo "Stopping Docker containers..."
	docker-compose down
	@echo "Docker stopped!"

docker-logs:
	docker-compose logs -f bot

# View logs
logs:
	tail -f bot.log

# Initialize database
db-init:
	@echo "Initializing database..."
	python -c "from database import init_db; init_db(); print('Database initialized!')"

# Development mode (auto-reload)
dev:
	@echo "Starting in development mode..."
	watchmedo auto-restart --patterns="*.py" --recursive -- python main.py

# Create .env from example
setup-env:
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo ".env file created! Please edit it with your tokens."; \
	else \
		echo ".env file already exists!"; \
	fi

# Full setup
setup: setup-env install db-init
	@echo ""
	@echo "Setup complete!"
	@echo "Next steps:"
	@echo "  1. Edit .env file with your tokens"
	@echo "  2. Run 'make test' to verify"
	@echo "  3. Run 'make run' to start bot"
	@echo ""
