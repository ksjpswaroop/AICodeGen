"""Database utility functions and management commands."""

import os
import sys
from typing import Optional
from pathlib import Path
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from alembic import command
from alembic.config import Config as AlembicConfig

from .connection import engine, SessionLocal, DatabaseManager
from .models import Base, User, Project, Agent, Task, Message


class DatabaseUtils:
    """Utility class for database operations."""
    
    @staticmethod
    def get_alembic_config() -> AlembicConfig:
        """Get Alembic configuration."""
        # Get the path to the migrations directory
        migrations_dir = Path(__file__).parent / "migrations"
        alembic_cfg = AlembicConfig(str(migrations_dir / "alembic.ini"))
        alembic_cfg.set_main_option("script_location", str(migrations_dir))
        return alembic_cfg
    
    @staticmethod
    def create_migration(message: str, autogenerate: bool = True) -> None:
        """
        Create a new database migration.
        
        Args:
            message: Migration message
            autogenerate: Whether to auto-generate migration from model changes
        """
        try:
            alembic_cfg = DatabaseUtils.get_alembic_config()
            command.revision(
                alembic_cfg,
                message=message,
                autogenerate=autogenerate
            )
            print(f"✅ Created migration: {message}")
        except Exception as e:
            print(f"❌ Failed to create migration: {e}")
            raise
    
    @staticmethod
    def run_migrations() -> None:
        """Run all pending database migrations."""
        try:
            alembic_cfg = DatabaseUtils.get_alembic_config()
            command.upgrade(alembic_cfg, "head")
            print("✅ Database migrations completed successfully")
        except Exception as e:
            print(f"❌ Failed to run migrations: {e}")
            raise
    
    @staticmethod
    def rollback_migration(revision: str = "-1") -> None:
        """
        Rollback database migration.
        
        Args:
            revision: Revision to rollback to (default: previous revision)
        """
        try:
            alembic_cfg = DatabaseUtils.get_alembic_config()
            command.downgrade(alembic_cfg, revision)
            print(f"✅ Rolled back to revision: {revision}")
        except Exception as e:
            print(f"❌ Failed to rollback migration: {e}")
            raise
    
    @staticmethod
    def get_migration_history() -> None:
        """Display migration history."""
        try:
            alembic_cfg = DatabaseUtils.get_alembic_config()
            command.history(alembic_cfg)
        except Exception as e:
            print(f"❌ Failed to get migration history: {e}")
            raise
    
    @staticmethod
    def get_current_revision() -> Optional[str]:
        """Get current database revision."""
        try:
            alembic_cfg = DatabaseUtils.get_alembic_config()
            command.current(alembic_cfg)
        except Exception as e:
            print(f"❌ Failed to get current revision: {e}")
            return None
    
    @staticmethod
    def seed_database() -> None:
        """Seed database with initial data."""
        db = SessionLocal()
        try:
            # Check if data already exists
            if db.query(User).first():
                print("Database already seeded")
                return
            
            # Create admin user
            admin_user = User(
                username="admin",
                email="admin@aicodegen.dev",
                full_name="System Administrator",
                hashed_password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # secret
                is_active=True,
                is_superuser=True
            )
            db.add(admin_user)
            
            # Create sample project
            sample_project = Project(
                name="Sample Multi-Agent Project",
                description="A sample project to demonstrate multi-agent capabilities",
                owner=admin_user,
                charter={
                    "objectives": ["Demonstrate multi-agent collaboration"],
                    "scope": "Sample project for testing",
                    "constraints": {"budget": 10000, "timeline": "30 days"}
                },
                requirements={
                    "functional": ["User authentication", "Project management"],
                    "non_functional": ["Performance", "Security"]
                }
            )
            db.add(sample_project)
            
            # Create sample agents
            agents_data = [
                {
                    "name": "Discovery Agent",
                    "agent_type": "discovery",
                    "description": "Handles project initiation and requirements gathering",
                    "capabilities": ["requirements_analysis", "stakeholder_interviews"]
                },
                {
                    "name": "Planning Agent",
                    "agent_type": "planning",
                    "description": "Manages project planning and task breakdown",
                    "capabilities": ["work_breakdown", "timeline_estimation", "resource_planning"]
                },
                {
                    "name": "Development Agent",
                    "agent_type": "development",
                    "description": "Handles code generation and development tasks",
                    "capabilities": ["code_generation", "api_integration", "testing"]
                }
            ]
            
            for agent_data in agents_data:
                agent = Agent(
                    name=agent_data["name"],
                    agent_type=agent_data["agent_type"],
                    description=agent_data["description"],
                    capabilities=agent_data["capabilities"],
                    project=sample_project
                )
                db.add(agent)
            
            db.commit()
            print("✅ Database seeded successfully")
            
        except SQLAlchemyError as e:
            db.rollback()
            print(f"❌ Failed to seed database: {e}")
            raise
        finally:
            db.close()
    
    @staticmethod
    def clear_database() -> None:
        """Clear all data from database (keep schema)."""
        db = SessionLocal()
        try:
            # Delete in reverse order of dependencies
            db.query(Message).delete()
            db.query(Task).delete()
            db.query(Agent).delete()
            db.query(Project).delete()
            db.query(User).delete()
            
            db.commit()
            print("✅ Database cleared successfully")
            
        except SQLAlchemyError as e:
            db.rollback()
            print(f"❌ Failed to clear database: {e}")
            raise
        finally:
            db.close()
    
    @staticmethod
    def check_database_health() -> dict:
        """
        Check database health and return status information.
        
        Returns:
            Dictionary with health check results
        """
        health_status = {
            "database_connected": False,
            "tables_exist": False,
            "migrations_current": False,
            "sample_data_exists": False,
            "error": None
        }
        
        try:
            # Check database connection
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            health_status["database_connected"] = True
            
            # Check if tables exist
            from sqlalchemy import inspect
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            expected_tables = ["users", "projects", "tasks", "agents", "messages"]
            health_status["tables_exist"] = all(table in tables for table in expected_tables)
            
            # Check if sample data exists
            db = SessionLocal()
            try:
                user_count = db.query(User).count()
                health_status["sample_data_exists"] = user_count > 0
            finally:
                db.close()
                
        except Exception as e:
            health_status["error"] = str(e)
        
        return health_status
    
    @staticmethod
    def print_database_stats() -> None:
        """Print database statistics."""
        db = SessionLocal()
        try:
            stats = {
                "Users": db.query(User).count(),
                "Projects": db.query(Project).count(),
                "Tasks": db.query(Task).count(),
                "Agents": db.query(Agent).count(),
                "Messages": db.query(Message).count(),
            }
            
            print("\n📊 Database Statistics:")
            print("-" * 30)
            for entity, count in stats.items():
                print(f"{entity:12}: {count:6}")
            print("-" * 30)
            
        except SQLAlchemyError as e:
            print(f"❌ Failed to get database stats: {e}")
        finally:
            db.close()


def init_database() -> None:
    """Initialize database with tables and migrations."""
    print("🔧 Initializing database...")
    
    try:
        # Create tables
        DatabaseManager.create_tables()
        print("✅ Database tables created")
        
        # Run migrations
        DatabaseUtils.run_migrations()
        
        # Seed with initial data
        DatabaseUtils.seed_database()
        
        # Print stats
        DatabaseUtils.print_database_stats()
        
        print("🎉 Database initialization completed successfully!")
        
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        raise


if __name__ == "__main__":
    """Command-line interface for database management."""
    if len(sys.argv) < 2:
        print("Usage: python -m aicodegen.database.utils <command>")
        print("Commands: init, migrate, seed, clear, stats, health")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "init":
        init_database()
    elif command == "migrate":
        DatabaseUtils.run_migrations()
    elif command == "seed":
        DatabaseUtils.seed_database()
    elif command == "clear":
        DatabaseUtils.clear_database()
    elif command == "stats":
        DatabaseUtils.print_database_stats()
    elif command == "health":
        health = DatabaseUtils.check_database_health()
        print("🏥 Database Health Check:")
        for key, value in health.items():
            status = "✅" if value else "❌"
            print(f"{status} {key}: {value}")
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
