# Hiring Assessments Assignment

A full-stack assessment platform for creating, managing, and evaluating technical assessments with support for MCQ, multiple-select, and subjective questions.

## Project Structure

This repository contains:

- **Backend** (`/backend`) - Django-based REST API with async evaluation using Celery
- **Frontend** (`/frontend`) - React + TypeScript frontend application

## Quick Start

### Backend Setup

For detailed backend setup instructions, see [backend/README.md](backend/README.md).

**Quick setup using the automated script:**

```bash
cd backend
./setup.sh
```

The setup script will:

- Install UV (if needed) for fast Python package management
- Create and activate a virtual environment
- Install all dependencies
- Start PostgreSQL & Redis in Docker
- Run database migrations
- Seed sample data

After setup, start the Django development server:

```bash
source .venv/bin/activate
python manage.py runserver
```

The backend API will be available at: **http://localhost:8000**

### Frontend Setup

For detailed frontend setup instructions, see [frontend/README.md](frontend/README.md).

**Quick setup:**

```bash
cd frontend
npm install
npm run dev
```

The frontend will be available at: **http://localhost:3000** (or the port configured in your setup)

## Documentation

- **[Backend README](backend/README.md)** - Complete backend documentation, API endpoints, database schema, and development guide
- **[Frontend README](frontend/README.md)** - Frontend setup and development instructions

## Features

- **Multiple Question Types**: MCQ, Multiple MCQ (MMCQ), and Subjective questions
- **Dynamic Assessment Generation**: Create assessments with fixed or random question pools
- **Async Evaluation**: Background processing with Celery for evaluation tasks
- **RESTful API**: Complete API for frontend integration
- **Admin Interface**: Django admin for managing questions and assessments
- **Docker Support**: Containerized database services

## Tech Stack

### Backend

- Django & Django REST Framework
- PostgreSQL
- Redis
- Celery
- UV (Python package manager)

### Frontend

- React
- TypeScript
- Vite
- Tailwind CSS
