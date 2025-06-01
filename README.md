# Payment System

A FastAPI-based payment system with user authentication and transaction management.

## Features

- User authentication with JWT tokens
- Payment processing
- Balance management
- PostgreSQL database with asyncpg
- Docker Compose setup for development
- Production-ready Dockerfile

## Development Setup

1. Clone the repository
2. Create a `.env` file with the following variables:
   ```env
   POSTGRES_USER=postgres_pay
   POSTGRES_PASSWORD=postgres123
   POSTGRES_HOST=postgres_db
   POSTGRES_PORT=5432
   POSTGRES_DB=pay
   JWT_SECRET_KEY=your_secret_key
   JWT_ALGORITHM=HS256
   JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
   ```
3. Install dependencies:
   ```bash
   uv venv
   source .venv/bin/activate  # or `.venv/Scripts/activate` on Windows
   uv pip install -r requirements.txt
   ```
4. Start the database:
   ```bash
   docker-compose up -d
   ```
5. Run the development server:
   ```bash
   uvicorn app.main:app --reload
   ```

The API will be available at http://localhost:8000

## API Documentation

When the server is running, you can access:
- Swagger UI documentation at http://localhost:8000/docs
- ReDoc documentation at http://localhost:8000/redoc

## Production Deployment

To build and run the production container:

```bash
docker build -t payment-system -f Dockerfile.prod .
docker run -p 80:80 --env-file .env payment-system
```

## Project Structure

- `app/` - Main application package
  - `models/` - SQLModel/Pydantic models
  - `route/` - API routes
  - `config.py` - Configuration management
  - `database.py` - Database setup and utilities
  - `security.py` - Authentication and security utilities
- `static/` - Static files
- `templates/` - HTML templates
- `tests/` - Test suite

## License

See [LICENSE](LICENSE) file.
