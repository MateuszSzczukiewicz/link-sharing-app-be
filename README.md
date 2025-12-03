# Link Sharing App - Backend

A RESTful API backend for a link sharing application built with Flask. Users can register, authenticate, and manage their social media profile links across multiple platforms.

## Features

- User authentication with JWT tokens
- Profile management (name, email, profile image)
- Multi-platform link management (GitHub, LinkedIn, Twitter, YouTube, etc.)
- SQLite database with automated migrations
- Comprehensive test coverage
- Docker support for containerized deployment

## Technology Stack

- **Python 3.14** - Programming language
- **Flask 3.x** - Web framework
- **SQLite** - Database
- **JWT** - Authentication
- **UV** - Fast Python package manager
- **Pytest** - Testing framework
- **Docker** - Containerization

## Prerequisites

- Python 3.14 or higher
- UV package manager
- SQLite3

## Installation

### 1. Install UV Package Manager

UV is a fast Python package manager that replaces pip and virtualenv.

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

For Windows PowerShell:
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 2. Clone the Repository

```bash
git clone <repository-url>
cd link-sharing-app-be
```

### 3. Install Dependencies

```bash
uv sync --all-extras
```

This will create a virtual environment and install all project dependencies including development tools.

### 4. Configure Environment Variables

Create a `.env` file in the project root:

```bash
SECRET_KEY=your-secret-key-here
```

Generate a secure secret key:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

## Development

### Quick Start with Helper Script

The project includes a `dev.sh` helper script for common tasks:

```bash
# Start development server
./dev.sh start

# Run tests
./dev.sh test

# Run all checks (lint + types + tests)
./dev.sh check

# Format code
./dev.sh format

# See all commands
./dev.sh
```

### Running the Application

Start the development server:

```bash
# Using helper script (recommended)
./dev.sh start

# Or directly with UV
uv run flask --app link_sharing_app --debug run

# On specific port
uv run flask run --port 8000

# Accessible from network
uv run flask run --host 0.0.0.0
```

The API will be available at `http://localhost:5000`

### Running Tests

Execute the test suite:

```bash
uv run pytest
```

Run tests with verbose output:

```bash
uv run pytest -v
```

Run specific test file:

```bash
uv run pytest tests/test_auth.py
```

### Code Coverage

Generate coverage report:

```bash
uv run coverage run -m pytest
uv run coverage report
```

Generate HTML coverage report:

```bash
uv run coverage html
```

### Code Quality

Check and fix code with Ruff:

```bash
# Check for linting issues
uv run ruff check .

# Fix auto-fixable issues
uv run ruff check --fix .

# Format code
uv run ruff format .
```

Check code without fixing:

```bash
# Lint check (used in CI)
uv run ruff check .

# Format check (used in CI)
uv run ruff format --check .
```

### Type Checking

Run type checker with mypy:

```bash
# Check types
uv run mypy link_sharing_app

# Check types in tests too
uv run mypy link_sharing_app tests
```

### Debugging

The project includes VS Code debug configurations:

1. **Python: Flask** - Debug Flask application
2. **Python: Current File** - Debug currently open file
3. **Python: Pytest Current File** - Debug current test file
4. **Python: All Tests** - Debug all tests
5. **Python: Pytest with Coverage** - Debug tests with coverage

To debug:
1. Set breakpoints in code (click left of line number)
2. Press F5 or go to Run and Debug panel
3. Select configuration and start debugging

## API Endpoints

### Authentication

- `POST /auth/register` - Register new user
- `POST /auth/login` - Login and receive JWT token

### Users

- `GET /users/<id>` - Get user profile
- `PATCH /users/<id>` - Update user profile

### Links

- `GET /links/<user_id>` - Get all links for user
- `POST /links` - Create new link
- `PATCH /links/<id>` - Update link
- `DELETE /links/<id>` - Delete link

## Database Schema

### Users Table
- `id` - Primary key
- `email` - Unique user email
- `password` - Hashed password
- `first_name` - User's first name
- `last_name` - User's last name
- `image_url` - Profile image URL

### Links Table
- `id` - Primary key
- `user_id` - Foreign key to users
- `platform` - Social media platform
- `url` - Link URL
- `created` - Timestamp

Supported platforms: GitHub, Frontend_Mentor, Twitter, LinkedIn, YouTube, Facebook, Twitch, Dev.to, Codewars, Codepen, freeCodeCamp, GitLab, Hashnode, Stack_Overflow

## Production Deployment

### Using Docker

Build the Docker image:

```bash
docker build -t link-sharing-app-be .
```

Run the container:

```bash
docker run -d -p 8000:8000 \
  -e SECRET_KEY=your-secret-key \
  --name link-sharing-app \
  link-sharing-app-be
```

### Using Docker Compose

Create a `docker-compose.yml` file:

```yaml
version: '3.8'
services:
  backend:
    build: .
    ports:
      - "8000:8000"
    environment:
      - SECRET_KEY=${SECRET_KEY}
    restart: unless-stopped
```

Run with:

```bash
docker-compose up -d
```

### Using Waitress (WSGI Server)

For production without Docker:

```bash
uv run waitress-serve --host 0.0.0.0 --port 8000 --call 'link_sharing_app:create_app'
```

## Dependency Management

### Adding Dependencies

Add a production dependency:

```bash
uv add package-name
```

Add a development dependency:

```bash
uv add --dev package-name
```

### Updating Dependencies

Update all dependencies to latest compatible versions:

```bash
uv lock --upgrade
```

Update specific package:

```bash
uv lock --upgrade-package package-name
```

### Syncing Dependencies

Sync environment with lock file:

```bash
uv sync
```

Sync including development dependencies:

```bash
uv sync --all-extras
```

## Project Structure

```
link-sharing-app-be/
├── link_sharing_app/
│   ├── __init__.py       # Application factory
│   ├── auth.py           # Authentication endpoints
│   ├── db.py             # Database initialization
│   ├── links.py          # Link management endpoints
│   ├── users.py          # User management endpoints
│   └── schema.sql        # Database schema
├── tests/
│   ├── conftest.py       # Test configuration
│   ├── test_auth.py      # Authentication tests
│   ├── test_db.py        # Database tests
│   ├── test_link.py      # Link management tests
│   └── test_user.py      # User management tests
├── .github/
│   └── workflows/        # CI/CD pipelines
├── Dockerfile            # Docker configuration
├── pyproject.toml        # Project metadata and dependencies
├── uv.lock              # Locked dependencies
└── README.md            # This file
```

## CI/CD

The project includes GitHub Actions workflows:

- **CI Pipeline** - Runs on pull requests
  - Code formatting checks
  - Linting
  - Test suite
  - Docker build verification

- **CD Pipeline** - Runs on main branch pushes
  - Builds and pushes Docker images to Docker Hub
  - Tags images with commit SHA and latest

## License

This project is licensed under the MIT License.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Support

For issues and questions, please open an issue on the GitHub repository.
