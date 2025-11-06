#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Assessment Backend Setup Script${NC}"
echo -e "${BLUE}  (Using UV + Local venv)${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check if .env exists, create from .env.example if not
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  .env file not found${NC}"
    if [ -f .env.example ]; then
        echo -e "${BLUE}Creating .env from .env.example...${NC}"
        cp .env.example .env
        echo -e "${GREEN}✓ .env file created from .env.example${NC}"
        echo -e "${YELLOW}Note: Please review and update .env with your configuration if needed${NC}"
    else
        echo -e "${RED}❌ Error: .env.example file not found!${NC}"
        echo -e "${YELLOW}Cannot create .env file. Please create it manually.${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}✓ .env file found${NC}"
fi

# Check if docker is installed (for Redis and Postgres)
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed. Please install Docker first (needed for Redis & Postgres).${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Docker is installed${NC}"

# Check if docker compose is available
if ! docker compose version &> /dev/null; then
    echo -e "${RED}❌ Docker Compose is not available. Please install Docker Desktop or Docker Compose plugin.${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Docker Compose is available${NC}"

# Check if UV is installed
if ! command -v uv &> /dev/null; then
    echo -e "${YELLOW}⚠️  UV is not installed.${NC}"
    echo -e "${BLUE}Installing UV...${NC}"
    curl -LsSf https://astral.sh/uv/install.sh | sh
    
    # Source the UV environment
    export PATH="$HOME/.cargo/bin:$PATH"
    
    if ! command -v uv &> /dev/null; then
        echo -e "${RED}❌ Failed to install UV. Please install manually: https://github.com/astral-sh/uv${NC}"
        exit 1
    fi
fi

echo -e "${GREEN}✓ UV is installed${NC}"

# Check if .venv exists
if [ ! -d ".venv" ]; then
    echo -e "${YELLOW}⚠️  Virtual environment not found.${NC}"
    echo -e "${BLUE}Creating virtual environment with UV...${NC}"
    uv venv .venv
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ Failed to create virtual environment${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✓ Virtual environment created${NC}"
    
    echo -e "${BLUE}Installing dependencies with UV...${NC}"
    source .venv/bin/activate
    uv pip install -r requirements.txt
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ Failed to install dependencies${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✓ Dependencies installed${NC}"
else
    echo -e "${GREEN}✓ Virtual environment found${NC}"
fi

# Activate virtual environment
source .venv/bin/activate

echo -e "${GREEN}✓ Virtual environment activated${NC}"
echo ""

# Check if llm_configs directory exists and create sample config if needed
if [ ! -d "llm_configs" ]; then
    echo -e "${YELLOW}⚠️  llm_configs directory not found${NC}"
    echo -e "${BLUE}Creating llm_configs directory...${NC}"
    mkdir -p llm_configs
    echo -e "${GREEN}✓ llm_configs directory created${NC}"
fi

if [ ! -f "llm_configs/sample_llm_config.yaml" ]; then
    echo -e "${YELLOW}⚠️  sample_llm_config.yaml not found${NC}"
    echo -e "${BLUE}Creating sample_llm_config.yaml...${NC}"
    cat > llm_configs/sample_llm_config.yaml << 'EOF'
name: "sample_llm_config"
llm_config_class: "AzureOpenAILLMConfig"
endpoint: "https://sample-endpoint.com"
deployment_name: "sample-deployment"
api_key: "sample-api-key"
api_version: "2025-02-01-preview"
tools_enabled: false
EOF
    echo -e "${GREEN}✓ sample_llm_config.yaml created${NC}"
    echo -e "${YELLOW}Note: Please update llm_configs/sample_llm_config.yaml with your actual LLM configuration${NC}"
else
    echo -e "${GREEN}✓ sample_llm_config.yaml found${NC}"
fi

echo ""

# Stop any running database containers
echo -e "${BLUE}Stopping any running database containers...${NC}"
docker compose down postgres redis 2>/dev/null

# Start PostgreSQL and Redis (only these services)
echo -e "${BLUE}Starting PostgreSQL and Redis with Docker...${NC}"
docker compose up -d postgres redis

# Wait for PostgreSQL to be ready
echo -e "${YELLOW}Waiting for PostgreSQL to be ready...${NC}"
sleep 5

# Check if postgres is ready
echo -e "${BLUE}Checking PostgreSQL connection...${NC}"
until docker compose exec -T postgres pg_isready -U db_user -d postgres_db &> /dev/null; do
    echo -e "${YELLOW}  Waiting for PostgreSQL...${NC}"
    sleep 2
done

echo -e "${GREEN}✓ PostgreSQL is ready${NC}"

# Run migrations using local venv
echo -e "${BLUE}Running database migrations (using local venv)...${NC}"
python manage.py migrate

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Migration failed!${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Migrations completed${NC}"

# Initialize prompt templates
echo -e "${BLUE}Initializing prompt templates in database (using local venv)...${NC}"
python manage.py init_prompts

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Prompt template initialization failed!${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Prompt templates initialized successfully${NC}"

# Seed the database using local venv
echo -e "${BLUE}Seeding database with sample data (using local venv)...${NC}"
python manage.py seed_data

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Database seeding failed!${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Database seeded successfully${NC}"

# Create superuser (optional)
echo ""
read -p "$(echo -e ${YELLOW}Do you want to create a Django admin superuser? [y/N]: ${NC})" -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${BLUE}Creating superuser (using local venv)...${NC}"
    python manage.py createsuperuser
fi

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  Setup completed successfully! 🎉${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo ""
echo -e "  1. Start the Django development server:"
echo -e "     ${YELLOW}source .venv/bin/activate${NC}"
echo -e "     ${YELLOW}python manage.py runserver${NC}"
echo ""
echo -e "  2. (Optional) Start Celery worker for async tasks:"
echo -e "     ${YELLOW}source .venv/bin/activate${NC}"
echo -e "     ${YELLOW}python -m celery -A evaluation.celery worker -Q default,evaluation_queue --pool=solo${NC}"
echo ""
echo -e "  3. Access the application:"
echo -e "     ${YELLOW}http://localhost:8000${NC}"
echo ""
echo -e "  4. Access Django admin (if you created a superuser):"
echo -e "     ${YELLOW}http://localhost:8000/admin/${NC}"
echo ""
echo -e "  5. View database logs:"
echo -e "     ${YELLOW}docker compose logs -f postgres${NC}"
echo ""
echo -e "  6. Stop database services when done:"
echo -e "     ${YELLOW}docker compose down${NC}"
echo ""
echo -e "${YELLOW}Note:${NC} Database services (PostgreSQL & Redis) are running in Docker."
echo -e "${YELLOW}      Django/Python runs locally using UV and .venv${NC}"
echo ""