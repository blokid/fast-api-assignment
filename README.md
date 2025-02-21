# Fast API Assignment

A FastAPI application with email verification functionality.

## Prerequisites

Before you begin, ensure you have the following installed:
- Python 3.11.3 or higher
- Docker
- Docker Compose

**Note:** If you have a local database used by other projects, ensure port 5432 (PostgreSQL) is not in use to avoid conflicts.

## Database Schema

This database schema was created based on the project implementation to represent the data models and relationships:
[Database Diagram](https://dbdiagram.io/d/67b4b0a5263d6cf9a099729f)

## Quick Start

1. Clone the repository:
```bash
git clone https://github.com/MinHtet-O/fast-api-assignment.git
cd fast-api-assignment
```

2. Set up environment variables:
Create a `.env` file in the root directory with the following variables:
```env
EMAIL_API_KEY=re_TpMbBgu9_Hnhz4wya8YrsAiW5zgUjWd9U
email_verification_base_url=http://localhost:8000/api/v1
smtp_host=
smtp_port=
smtp_username=
smtp_password=
APP_ENV=test  # Important: Set to 'test' to use Docker PostgreSQL. 'dev' will use localhost PostgreSQL
```

**Important Notes:** 
- Make sure to set `APP_ENV=test` in your `.env` file. If set to `dev`, the application will attempt to connect to PostgreSQL running on localhost instead of the Docker container.
- For email testing, you can use [Mailtrap](https://mailtrap.io/) to set up a test inbox. Use the provided SMTP credentials in your `.env` file.

3. Start the application:
```bash
docker-compose up -d
```

4. Run database migrations:
```bash
docker-compose exec app poetry run alembic upgrade head
```

5. Run unit tests:
```bash
docker-compose exec app poetry run pytest
```

## API Documentation

Once the application is running, visit [http://localhost:8000/docs](http://localhost:8000/docs) to access the Swagger UI documentation for the API endpoints.

## Environment Variables

| Variable | Description |
|----------|-------------|
| `EMAIL_API_KEY` | API key for email service |
| `email_verification_base_url` | Base URL for email verification endpoints |
| `smtp_host` | SMTP server host |
| `smtp_port` | SMTP server port |
| `smtp_username` | SMTP username |
| `smtp_password` | SMTP password |
| `APP_ENV` | Application environment (test/dev). Use 'test' for Docker PostgreSQL |

## Development Workflow

### Commit Messages
This repository follows [Semantic Commit Messages](https://gist.github.com/joshbuchea/6f47e86d2510bce28f8e7f42ae84c716) to maintain clear and standardized commit history. Examples:
```
feat: add email verification endpoint
fix: correct database connection string
chore: update dependencies
test: add unit tests for user service
docs: update API documentation
```

### Branch and PR Strategy
- Main features are developed in separate branches and merged through Pull Requests
- Each PR must follow the repository's PR template
- Feature branches are merged using squash and merge strategy
- Small commits (chores, fixes, tests) can be pushed directly to the main branch for convenience

## Development

Make sure all ports required by the application (such as PostgreSQL 5432) are not in conflict with your local services before starting the development environment.

## Troubleshooting

If you encounter port conflicts:
1. Stop any local PostgreSQL service
2. Modify the port mapping in `docker-compose.yml` if needed
3. Ensure no other services are using the required ports
4. Verify that `APP_ENV` is set to `test` in your `.env` file

## Technology Stack

### Core Framework and Tools
- **FastAPI**: Modern, fast web framework for building APIs with Python
- **Uvicorn**: Lightning-fast ASGI server implementation
- **Docker & Docker Compose**: Containerization and service orchestration

### Database and ORM
- **PostgreSQL**: Primary database
- **SQLAlchemy**: Python SQL toolkit and ORM
- **Alembic**: Database migration tool


### Data Validation and Settings
- **Pydantic**: Data validation using Python type annotations
- **pydantic-settings**: Settings management using Pydantic
- **email-validator**: Email validation library

### Testing and Development
- **pytest**: Testing framework
- **Poetry**: Dependency management

### Code Quality and Formatting
- **black**: Code formatter

### Email Services
- **Mailtrap**: Email testing service (development)

### Logging and Monitoring
- **loguru**: Python logging made simple

## License

[MIT License](LICENSE)