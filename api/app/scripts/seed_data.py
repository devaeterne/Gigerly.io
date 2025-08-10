# api/app/scripts/seed_data.py
"""Seed database with sample data for development"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime, date, timedelta
from decimal import Decimal

# Add the parent directory to Python path
sys.path.append(str(Path(__file__).parent.parent.parent))

from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import AsyncSessionLocal
from app.models import (
    User, UserProfile, UserRole, UserStatus,
    Project, ProjectStatus, ProjectBudgetType, ProjectComplexity,
    Proposal, ProposalStatus,
    Contract, ContractStatus, ContractType,
    Milestone, MilestoneStatus,
    Notification, NotificationType, NotificationPriority
)
import logging

logger = logging.getLogger(__name__)

async def create_sample_users(db: AsyncSession):
    """Create sample users with profiles"""
    
    users_data = [
        {
            "email": "admin@platform.com",
            "role": UserRole.admin,
            "profile": {
                "display_name": "Platform Admin",
                "first_name": "Admin",
                "last_name": "User",
                "title": "Platform Administrator",
                "bio": "Platform administrator account",
                "is_available": False,
                "currency": "USD"
            }
        },
        {
            "email": "customer1@example.com",
            "role": UserRole.customer,
            "profile": {
                "display_name": "John Smith",
                "first_name": "John",
                "last_name": "Smith",
                "title": "Product Manager",
                "bio": "Looking for talented freelancers to help build amazing products.",
                "country": "United States",
                "city": "San Francisco",
                "currency": "USD"
            }
        },
        {
            "email": "freelancer1@example.com",
            "role": UserRole.freelancer,
            "profile": {
                "display_name": "Sarah Developer",
                "first_name": "Sarah",
                "last_name": "Johnson",
                "title": "Full-Stack Developer",
                "bio": "Experienced full-stack developer specializing in React, Node.js, and Python.",
                "skills": [
                    {"name": "React", "level": "Expert"},
                    {"name": "Node.js", "level": "Expert"},
                    {"name": "Python", "level": "Advanced"},
                    {"name": "PostgreSQL", "level": "Advanced"}
                ],
                "hourly_rate": Decimal("75.00"),
                "country": "Canada",
                "city": "Toronto",
                "currency": "USD",
                "total_earnings": Decimal("15000.00"),
                "completed_projects": 12,
                "average_rating": Decimal("4.8"),
                "total_reviews": 12
            }
        },
        {
            "email": "freelancer2@example.com",
            "role": UserRole.freelancer,
            "profile": {
                "display_name": "Mike Designer",
                "first_name": "Mike",
                "last_name": "Chen",
                "title": "UI/UX Designer",
                "bio": "Creative UI/UX designer with 8+ years of experience in mobile and web design.",
                "skills": [
                    {"name": "Figma", "level": "Expert"},
                    {"name": "Adobe Creative Suite", "level": "Expert"},
                    {"name": "User Research", "level": "Advanced"},
                    {"name": "Prototyping", "level": "Advanced"}
                ],
                "hourly_rate": Decimal("65.00"),
                "country": "United Kingdom",
                "city": "London",
                "currency": "USD",
                "total_earnings": Decimal("22000.00"),
                "completed_projects": 18,
                "average_rating": Decimal("4.9"),
                "total_reviews": 18
            }
        }
    ]
    
    created_users = []
    
    for user_data in users_data:
        # Create user
        user = User(
            email=user_data["email"],
            role=user_data["role"],
            status=UserStatus.active,
            is_active=True,
            is_verified=True,
            email_verified_at=datetime.utcnow()
        )
        
        db.add(user)
        await db.flush()  # Get the user ID
        
        # Create profile
        profile_data = user_data["profile"]
        profile = UserProfile(
            user_id=user.id,
            **profile_data
        )
        
        db.add(profile)
        created_users.append(user)
        
    await db.commit()
    logger.info(f"Created {len(created_users)} sample users")
    return created_users

async def create_sample_projects(db: AsyncSession, users: list):
    """Create sample projects"""
    
    # Find customer user
    customer = next(user for user in users if user.role == UserRole.customer)
    
    projects_data = [
        {
            "title": "E-commerce Website Development",
            "description": """
            We're looking for an experienced full-stack developer to build a modern e-commerce website. 
            
            Requirements:
            - React/Next.js frontend
            - Node.js/Express backend
            - PostgreSQL database
            - Payment integration (Stripe)
            - Admin dashboard
            - Mobile responsive design
            
            Timeline: 6-8 weeks
            Budget: $3000-5000
            """,
            "budget_type": ProjectBudgetType.fixed,
            "budget_min": Decimal("3000.00"),
            "budget_max": Decimal("5000.00"),
            "complexity": ProjectComplexity.intermediate,
            "estimated_duration": 45,
            "deadline": date.today() + timedelta(days=60),
            "category": "Web Development",
            "subcategory": "E-commerce",
            "required_skills": [
                {"name": "React", "required": True},
                {"name": "Node.js", "required": True},
                {"name": "PostgreSQL", "required": True},
                {"name": "Payment Integration", "required": False}
            ],
            "tags": ["ecommerce", "react", "nodejs", "fullstack"]
        },
        {
            "title": "Mobile App UI Design",
            "description": """
            We need a talented UI/UX designer to create a modern and intuitive design for our mobile app.
            
            Scope:
            - User research and personas
            - Wireframes and user flows
            - High-fidelity mockups
            - Interactive prototypes
            - Design system and style guide
            
            Platform: iOS and Android
            Industry: Healthcare
            """,
            "budget_type": ProjectBudgetType.fixed,
            "budget_min": Decimal("2000.00"),
            "budget_max": Decimal("3500.00"),
            "complexity": ProjectComplexity.intermediate,
            "estimated_duration": 30,
            "deadline": date.today() + timedelta(days=45),
            "category": "Design",
            "subcategory": "Mobile App Design",
            "required_skills": [
                {"name": "Figma", "required": True},
                {"name": "User Research", "required": True},
                {"name": "Mobile Design", "required": True},
                {"name": "Prototyping", "required": False}
            ],
            "tags": ["mobile", "ui", "ux", "healthcare", "design"]
        },
        {
            "title": "API Development for SaaS Platform",
            "description": """
            Looking for a backend developer to create RESTful APIs for our SaaS platform.
            
            Technical Requirements:
            - FastAPI or Django REST Framework
            - PostgreSQL database
            - JWT authentication
            - Rate limiting
            - API documentation
            - Unit tests
            
            This is an ongoing project with potential for long-term collaboration.
            """,
            "budget_type": ProjectBudgetType.HOURLY,
            "hourly_rate_min": Decimal("50.00"),
            "hourly_rate_max": Decimal("80.00"),
            "complexity": ProjectComplexity.COMPLEX,
            "estimated_duration": 60,
            "category": "Backend Development",
            "subcategory": "API Development",
            "required_skills": [
                {"name": "Python", "required": True},
                {"name": "FastAPI", "required": False},
                {"name": "PostgreSQL", "required": True},
                {"name": "API Design", "required": True}
            ],
            "tags": ["api", "backend", "python", "saas"]
        }
    ]
    
    created_projects = []
    
    for project_data in projects_data:
        project = Project(
            customer_id=customer.id,
            status=ProjectStatus.open,
            **project_data
        )
        
        db.add(project)
        created_projects.append(project)
    
    await db.commit()
    logger.info(f"Created {len(created_projects)} sample projects")
    return created_projects

async def create_sample_proposals(db: AsyncSession, projects: list, users: list):
    """Create sample proposals"""
    
    # Find freelancer users
    freelancers = [user for user in users if user.role == UserRole.freelancer]
    
    proposals_data = [
        {
            "project": projects[0],  # E-commerce project
            "freelancer": freelancers[0],  # Sarah Developer
            "cover_letter": """
            Hi there!
            
            I'm excited about your e-commerce project. With 5+ years of experience in full-stack development, 
            I've built several e-commerce platforms using the exact tech stack you mentioned.
            
            My approach:
            1. Planning & Architecture (Week 1)
            2. Backend API Development (Weeks 2-3)
            3. Frontend Development (Weeks 4-5)
            4. Payment Integration & Testing (Week 6)
            5. Deployment & Optimization (Week 7)
            
            I can deliver a production-ready solution within your timeline and budget.
            
            Best regards,
            Sarah
            """,
            "bid_amount": Decimal("4200.00"),
            "estimated_delivery_days": 42,
            "proposed_milestones": [
                {"title": "Project Setup & Planning", "amount": 800, "days": 7},
                {"title": "Backend API Development", "amount": 1200, "days": 14},
                {"title": "Frontend Development", "amount": 1400, "days": 14},
                {"title": "Payment Integration", "amount": 500, "days": 5},
                {"title": "Testing & Deployment", "amount": 300, "days": 2}
            ]
        },
        {
            "project": projects[1],  # Mobile App Design
            "freelancer": freelancers[1],  # Mike Designer
            "cover_letter": """
            Hello!
            
            I specialize in healthcare app design and have created interfaces for 3 medical apps 
            that are currently live on the App Store.
            
            What I'll deliver:
            - User research & personas
            - Complete user journey mapping
            - Wireframes for all screens
            - High-fidelity designs
            - Interactive prototypes
            - Design system documentation
            
            I understand the importance of accessibility and compliance in healthcare apps.
            
            Looking forward to working with you!
            Mike
            """,
            "bid_amount": Decimal("2800.00"),
            "estimated_delivery_days": 28,
            "proposed_milestones": [
                {"title": "Research & Wireframes", "amount": 800, "days": 10},
                {"title": "High-fidelity Designs", "amount": 1200, "days": 12},
                {"title": "Prototypes & Design System", "amount": 800, "days": 6}
            ]
        }
    ]
    
    created_proposals = []
    
    for proposal_data in proposals_data:
        proposal = Proposal(
            project_id=proposal_data["project"].id,
            freelancer_id=proposal_data["freelancer"].id,
            cover_letter=proposal_data["cover_letter"],
            bid_amount=proposal_data["bid_amount"],
            currency="USD",
            estimated_delivery_days=proposal_data["estimated_delivery_days"],
            proposed_milestones=proposal_data["proposed_milestones"],
            status=ProposalStatus.pending
        )
        
        db.add(proposal)
        created_proposals.append(proposal)
        
        # Update project proposal count
        proposal_data["project"].proposal_count += 1
    
    await db.commit()
    logger.info(f"Created {len(created_proposals)} sample proposals")
    return created_proposals

async def create_sample_notifications(db: AsyncSession, users: list):
    """Create sample notifications"""
    
    notifications_data = [
        {
            "user": users[1],  # Customer
            "type": NotificationType.proposal_received,
            "priority": NotificationPriority.normal,
            "title": "New Proposal Received",
            "message": "Sarah Developer submitted a proposal for your E-commerce Website Development project.",
            "payload": {"project_id": 1, "proposal_id": 1}
        },
        {
            "user": users[2],  # Freelancer 1
            "type": NotificationType.new_project_posted,
            "priority": NotificationPriority.normal,
            "title": "New Project Matches Your Skills",
            "message": "A new API Development project has been posted that matches your React and Node.js skills.",
            "payload": {"project_id": 3}
        },
        {
            "user": users[3],  # Freelancer 2
            "type": NotificationType.new_project_posted,
            "priority": NotificationPriority.normal,
            "title": "New Design Project Available",
            "message": "A Mobile App UI Design project has been posted in your area of expertise.",
            "payload": {"project_id": 2}
        }
    ]
    
    created_notifications = []
    
    for notif_data in notifications_data:
        notification = Notification(
            user_id=notif_data["user"].id,
            type=notif_data["type"],
            priority=notif_data["priority"],
            title=notif_data["title"],
            message=notif_data["message"],
            payload=notif_data["payload"],
            is_read=False,
            is_sent_push=False,
            is_sent_email=False
        )
        
        db.add(notification)
        created_notifications.append(notification)
    
    await db.commit()
    logger.info(f"Created {len(created_notifications)} sample notifications")
    return created_notifications

async def seed_database():
    """Main function to seed the database with sample data"""
    logger.info("Starting database seeding...")
    
    async with AsyncSessionLocal() as db:
        try:
            # Create sample data
            users = await create_sample_users(db)
            projects = await create_sample_projects(db, users)
            proposals = await create_sample_proposals(db, projects, users)
            notifications = await create_sample_notifications(db, users)
            
            logger.info("Database seeding completed successfully!")
            logger.info(f"Created: {len(users)} users, {len(projects)} projects, {len(proposals)} proposals, {len(notifications)} notifications")
            
        except Exception as e:
            logger.error(f"Database seeding failed: {e}")
            await db.rollback()
            raise
        
if __name__ == "__main__":
    asyncio.run(seed_database())