# Assessment Backend

A Django-based backend system for creating, managing, and evaluating technical assessments with support for MCQ, multiple-select, and subjective questions.

## 🚀 Features

- **Multiple Question Types**: MCQ, Multiple MCQ (MMCQ), and Subjective questions
- **Dynamic Assessment Generation**: Create assessments with fixed or random question pools
- **Async Evaluation**: Background processing with Celery for evaluation tasks
- **RESTful API**: Complete API for frontend integration
- **Admin Interface**: Django admin for managing questions and assessments
- **Docker Support**: Fully containerized setup with Docker Compose

## 📋 Prerequisites

- Docker Desktop (v20.10+) with Compose plugin (for PostgreSQL & Redis)
- **UV** - Fast Python package installer (auto-installed by setup.sh)
- Python 3.11+ (managed by UV via venv)

**Note:** This setup uses UV + local venv for Python, and Docker only for databases.

## ⚡ Quick Start (Recommended)

### Option 1: Using Setup Script (Easiest) ⭐

The setup script uses **UV** for blazing-fast Python package management:

```bash
# 1. Run the automated setup
./setup.sh

# This will:
# - Install UV if needed
# - Create/activate .venv
# - Install dependencies (10-100x faster than pip!)
# - Start PostgreSQL & Redis in Docker
# - Run migrations
# - Seed sample data

# 2. Start Django dev server
source .venv/bin/activate
python manage.py runserver
```

The application will be available at: **http://localhost:8000**

**See [UV_SETUP.md](UV_SETUP.md) for detailed UV usage guide.**

### Option 2: Manual Setup

```bash
# 1. Ensure .env file exists
cp .env.example .env  # Only if .env doesn't exist

# 2. Install UV (if not installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 3. Create venv and install dependencies
uv venv .venv
source .venv/bin/activate
uv pip install -r requirements.txt

# 4. Start PostgreSQL and Redis
docker compose up -d postgres redis

# 5. Wait for PostgreSQL (about 5 seconds)
sleep 5

# 6. Run migrations
python manage.py migrate

# 7. Seed the database with sample data
python manage.py seed_data

# 8. (Optional) Create admin superuser
python manage.py createsuperuser

# 9. Start Django dev server
python manage.py runserver
```

## 📦 What Gets Created

After running the setup, your database will contain:

### Sample Questions

- **5 MCQ Questions**: Single-choice technical questions
- **2 MMCQ Questions**: Multiple-choice with multiple correct answers
- **3 Subjective Questions**: Written response questions

### Assessment Configurations

1. **Technical Screening - MCQ** (30 minutes)
   - 5 multiple-choice questions
   - All questions skippable
2. **Comprehensive Technical Assessment** (1 hour)
   - Mixed question types
   - Includes MCQ, MMCQ, and subjective questions
3. **Quick Aptitude Test** (15 minutes)
   - Random selection from question pool
   - Quick technical screening

## 🔧 Development Setup (UV + Docker Databases)

**Current Recommended Approach:** UV for Python, Docker for databases

```bash
# 1. Install UV (ultra-fast package installer)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Create and activate virtual environment with UV
uv venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# 3. Install dependencies (10-100x faster than pip!)
uv pip install -r requirements.txt

# 4. Start databases with Docker
docker compose up -d postgres redis

# 5. Run migrations
python manage.py migrate

# 6. Seed data
python manage.py seed_data

# 7. Start development server
python manage.py runserver

# 8. In another terminal, start Celery worker
source .venv/bin/activate
python -m celery -A evaluation.celery worker -Q default,evaluation_queue --pool=solo
```

**Why UV?**

- ⚡ 10-100x faster than pip
- 🔒 Reliable dependency resolution
- 🚀 Zero configuration needed
- 💯 Drop-in pip replacement

See [UV_SETUP.md](UV_SETUP.md) for complete UV guide.

## 📚 API Endpoints

### Assessment Management

- `GET /evaluation/assessment-configs` - List available assessments
- `POST /evaluation/start-assessment` - Create a new assessment attempt
- `GET /evaluation/assessment-state?assessment_id={id}` - Get assessment state
- `GET /evaluation/assessment-history` - Get user's assessment history

### Questions

- `GET /evaluation/questions?assessment_id={id}&question_id={qid}` - Get question details

### Submit Answers

- `POST /evaluation/submit-assessment-answer-mcq` - Submit MCQ answer
- `POST /evaluation/submit-assessment-answer-mmcq` - Submit MMCQ answer
- `POST /evaluation/submit-assessment-answer-subjective` - Submit text answer

### Evaluation & Results

- `POST /evaluation/close-assessment` - Complete and evaluate assessment
- `GET /evaluation/fetch-report?assessmentId={id}` - Get assessment report
- `GET /evaluation/fetch-individual-scorecard?assessment_id={id}` - Get scorecard

### Admin Panel

- `GET /admin/` - Django admin interface (requires superuser)

## 🔐 Admin Interface

Access the Django admin panel at **http://localhost:8000/admin/**

You can manage:

- Questions (create, edit, delete)
- Assessment Configurations
- Question Attempts
- Assessment Attempts

## 🗄️ Database Schema

### Key Models

#### Question

- Supports MCQ (answer_type=0), MMCQ (answer_type=1), Subjective (answer_type=2)
- Stores question data in JSON format
- Includes tags, difficulty level, time requirements

#### AssessmentGenerationConfig

- Defines assessment templates
- Configures question selection (fixed IDs or random pool)
- Sets duration, instructions, and display data

#### AssessmentAttempt

- Tracks user's assessment sessions
- Stores attempt status, timing, and evaluation results

#### QuestionAttempt

- Records individual question responses
- Links to assessment attempts
- Stores evaluation data

## 🧪 Testing the Setup

### 1. Check Services Status

```bash
docker compose ps
```

All services should show "Up" status.

### 2. Test API

```bash
# Get available assessments
curl http://localhost:8000/evaluation/assessment-configs

# Expected response: List of available assessments
```

### 3. Access Admin Panel

1. Create superuser (if not done during setup):
   ```bash
   source .venv/bin/activate
   python manage.py createsuperuser
   ```
2. Visit http://localhost:8000/admin/
3. Login with your credentials
4. Browse Questions and Assessment Configurations

## 📝 Common Commands

### Python/Django Commands (using UV + venv)

```bash
# Activate virtual environment
source .venv/bin/activate

# Start Django dev server
python manage.py runserver

# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Seed database (adds sample data)
python manage.py seed_data

# Clear and reseed (removes existing data first)
python manage.py seed_data --clear

# Create superuser
python manage.py createsuperuser

# Access Django shell
python manage.py shell

# Start Celery worker
python -m celery -A evaluation.celery worker -Q default,evaluation_queue --pool=solo
```

### UV Package Management

```bash
# Install new package (10-100x faster than pip!)
uv pip install package-name

# Install from requirements
uv pip install -r requirements.txt

# Update all packages
uv pip install --upgrade -r requirements.txt

# Freeze current environment
uv pip freeze > requirements.txt
```

### Docker Commands (Databases Only)

```bash
# Start databases
docker compose up -d postgres redis

# Stop databases
docker compose down

# View database logs
docker compose logs -f postgres
docker compose logs -f redis

# Restart databases
docker compose restart postgres redis

# Access PostgreSQL shell
docker compose exec postgres psql -U db_user -d postgres_db
```

## 🐛 Troubleshooting

### Port Conflicts

If ports 8000, 5433, or 6379 are already in use:

1. Edit `docker-compose.yaml`
2. Change the port mappings (e.g., "8001:8000")
3. Update `.env` accordingly

### Database Connection Issues

```bash
# Check if PostgreSQL is running
docker compose ps postgres

# Restart PostgreSQL
docker compose restart postgres

# Check PostgreSQL logs
docker compose logs postgres
```

### Migration Issues

```bash
# Reset migrations (careful - destroys data!)
docker compose down -v
docker volume rm backend_pgdb_assessments
./setup.sh
```

### Celery Not Processing Tasks

```bash
# Check Celery logs
docker compose logs celery

# Restart Celery
docker compose restart celery
```

## 🏗️ Project Structure

```
backend/
├── assessments/          # Django project settings
│   ├── settings.py       # Configuration
│   └── urls.py          # URL routing
├── evaluation/          # Main application
│   ├── models.py        # Database models
│   ├── views.py         # API endpoints
│   ├── urls.py          # URL patterns
│   ├── usecases.py      # Business logic
│   ├── repositories.py  # Database access
│   ├── evaluators/      # Question evaluators
│   ├── assessment/      # Assessment generation
│   └── management/      # Custom commands
├── OpenAIService/       # LLM integration
├── docker-compose.yaml  # Docker configuration
├── requirements.txt     # Python dependencies
├── setup.sh            # Setup script
└── .env                # Environment variables
```

## 🔑 Environment Variables

Key environment variables in `.env`:

```bash
# PostgreSQL
POSTGRES_HOST=localhost     # Use 'postgres' for Docker
POSTGRES_PORT=5433
POSTGRES_DB=postgres_db
POSTGRES_USER=db_user
POSTGRES_PASSWORD=db_password

# Redis
REDIS_HOST=localhost        # Use 'redis' for Docker
REDIS_PORT=6379
REDIS_PASSWORD=redis_password

# Celery
CELERY_USE_SSL=FALSE       # Set to TRUE for production
```

## 📚 Additional Documentation

- **[UV_SETUP.md](UV_SETUP.md)** - Complete UV setup and usage guide
- **[SETUP_GUIDE.md](SETUP_GUIDE.md)** - Detailed setup instructions for different environments
- **[TEST_RESULTS.md](TEST_RESULTS.md)** - Test results and verification details

## 📖 External Resources

- [UV Documentation](https://docs.astral.sh/uv/) - Fast Python package installer
- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Celery Documentation](https://docs.celeryproject.org/)
- [Docker Documentation](https://docs.docker.com/)

## 🤝 Contributing

When adding new features:

1. Create new questions via admin panel or by extending `seed_data.py`
2. Add new assessment configurations as needed
3. Run migrations after model changes
4. Test thoroughly before committing
