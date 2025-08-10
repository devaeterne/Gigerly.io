# README.md (güncellenmiş)
# 🚀 gigerly.io Platform

Modern, scalable gigerly.io marketplace built with **FastAPI** and **Next.js**.

## 📋 Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Quick Start](#quick-start)
- [Development](#development)
- [API Documentation](#api-documentation)
- [Deployment](#deployment)
- [Contributing](#contributing)

## ✨ Features

### 🔐 Authentication & Authorization
- **Google OAuth** integration
- **JWT** token-based authentication
- **Role-based access control** (Admin, Moderator, HelpDesk, Freelancer, Customer)
- **Password reset** and email verification

### 💼 Project Management
- Create and manage projects
- **Budget types**: Fixed price or hourly
- **Skill-based matching**
- **Advanced search and filtering**
- **File attachments** support

### 📝 Proposal System
- Submit and manage proposals
- **Milestone-based proposals**
- **Portfolio integration**
- **Accept/reject workflow**

### 📋 Contract Management
- **Automated contract creation**
- **Milestone tracking**
- **Payment scheduling**
- **Progress monitoring**

### 💰 Payment System
- **Payoneer integration**
- **Escrow-style payments**
- **Milestone-based releases**
- **Transaction tracking**

### 🔔 Notifications
- **Push notifications** (FCM)
- **Email notifications**
- **Real-time updates**
- **Notification preferences**

### 👨‍💼 Admin Dashboard
- **User management**
- **System monitoring**
- **Analytics and reporting**
- **Moderation tools**

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Next.js Web   │    │   FastAPI API   │    │  PostgreSQL DB  │
│   (Frontend)    │◄──►│   (Backend)     │◄──►│   (Database)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │              ┌─────────────────┐              │
         │              │  Redis Cache    │              │
         └──────────────┤  (Cache/Queue)  │──────────────┘
                        └─────────────────┘
                                 │
                        ┌─────────────────┐
                        │ Background Jobs │
                        │   (Worker)      │
                        └─────────────────┘
```

### Tech Stack

**Backend:**
- **FastAPI** - Modern Python web framework
- **SQLAlchemy** - ORM with async support
- **PostgreSQL** - Primary database
- **Redis** - Caching and job queue
- **Alembic** - Database migrations

**Frontend:**
- **Next.js 14** - React framework with App Router
- **TypeScript** - Type safety
- **Tailwind CSS** - Utility-first CSS
- **shadcn/ui** - Modern UI components

**Infrastructure:**
- **Docker** - Containerization
- **Nginx** - Reverse proxy
- **Payoneer** - Payment processing
- **Firebase** - Push notifications

## 🚀 Quick Start

### Prerequisites
- **Docker** & **Docker Compose**
- **Node.js 18+** (for local development)
- **Python 3.11+** (for local development)

### 1. Clone & Setup
```bash
git clone <repository>
cd gigerly.io-platform
./scripts/setup.sh
```

### 2. Configure Environment
```bash
# Edit API environment
nano api/.env

# Edit Web environment  
nano web/.env.local
```

### 3. Start Services
```bash
# Quick start (recommended)
make start

# Or manually
docker-compose up --build
```

### 4. Initialize Database
```bash
# Run migrations and seed data
make migrate-seed
```

### 5. Access Application
- **API Docs**: http://localhost:8000/docs
- **Web App**: http://localhost:3000
- **Admin Panel**: http://localhost:3000/admin

## 🛠️ Development

### Available Commands

```bash
# Setup and start
make setup          # Initial project setup
make start          # Build, start, migrate & seed
make up             # Start services
make down           # Stop services

# Database
make migrate        # Run migrations
make migrate-create name="description"  # Create migration
make db-backup      # Create backup
make db-stats       # Show statistics

# Development
make logs           # View all logs
make shell-api      # Access API container
make shell-db       # Access database
make test           # Run tests
make lint           # Run linting
make format         # Format code

# Health & monitoring
make health         # Check all services
```

### Development Workflow

1. **Create feature branch**
```bash
git checkout -b feature/new-feature
```

2. **Make changes and test**
```bash
make test
make lint
```

3. **Test API endpoints**
```bash
./scripts/test-api.sh
```

4. **Commit and push**
```bash
git add .
git commit -m "Add new feature"
git push origin feature/new-feature
```

### Project Structure

```
freelancer-platform/
├── api/                    # FastAPI backend
│   ├── app/
│   │   ├── core/          # Database, Redis, logging
│   │   ├── models/        # SQLAlchemy models
│   │   ├── schemas/       # Pydantic schemas
│   │   ├── routes/        # API endpoints
│   │   ├── services/      # External integrations
│   │   └── main.py        # FastAPI app
│   └── alembic/           # Database migrations
├── web/                   # Next.js frontend
│   ├── app/               # App Router pages
│   ├── components/        # Reusable components
│   └── lib/               # Utilities
├── nginx/                 # Reverse proxy config
├── scripts/               # Automation scripts
└── docker-compose.yml     # Development environment
```

## 📚 API Documentation

### Authentication

```bash
# Register user
POST /api/v1/auth/register
{
  "email": "user@example.com",
  "password": "password123",
  "role": "freelancer"
}

# Login
POST /api/v1/auth/login
{
  "email": "user@example.com",
  "password": "password123"
}

# Google OAuth
POST /api/v1/auth/google
{
  "google_token": "google_access_token"
}
```

### Projects

```bash
# List projects
GET /api/v1/projects?category=web&sort_by=created_at

# Create project
POST /api/v1/projects
{
  "title": "Build E-commerce Website",
  "description": "Need a modern e-commerce platform...",
  "budget_type": "fixed",
  "budget_max": 5000,
  "currency": "USD"
}
```

### Proposals

```bash
# Submit proposal
POST /api/v1/proposals
{
  "project_id": 1,
  "cover_letter": "I'm excited to work on...",
  "bid_amount": 4500,
  "estimated_delivery_days": 30
}

# Accept proposal
POST /api/v1/proposals/1/accept
```

### Full API documentation available at: **http://localhost:8000/docs**

## 🚢 Deployment

### Production Setup

1. **Prepare environment files**
```bash
cp api/.env.example api/.env.prod
cp web/.env.local.example web/.env.production
# Update with production values
```

2. **Deploy with production compose**
```bash
docker-compose -f docker-compose.prod.yml up -d
```

3. **Run migrations**
```bash
make prod-migrate
```

### Environment Variables

**Required for production:**
- `JWT_SECRET` - Strong random secret
- `GOOGLE_CLIENT_ID` & `GOOGLE_CLIENT_SECRET`
- `DATABASE_URL` - Production database
- `REDIS_URL` - Production Redis
- `FCM_SERVER_KEY` - Firebase key
- `PAYONEER_API_KEY` & `PAYONEER_API_SECRET`

## 🤝 Contributing

1. **Fork the repository**
2. **Create feature branch**
3. **Make changes with tests**
4. **Ensure all tests pass**
5. **Submit pull request**

### Code Standards
- **Python**: Black formatting, type hints
- **TypeScript**: ESLint, Prettier
- **Tests**: Minimum 80% coverage
- **Commits**: Conventional commit format

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: Check `/docs` folder
- **Issues**: Create GitHub issue
- **API Issues**: Check http://localhost:8000/docs
- **Discord**: [Join our community](#)

---

**Built with ❤️ by the gigerly.io Platform Team**