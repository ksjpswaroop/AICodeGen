"""SQLAlchemy models for the multi-agent platform."""

import enum
from datetime import datetime
from typing import Optional, List
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    Boolean,
    ForeignKey,
    Enum,
    JSON,
    Float,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

Base = declarative_base()


class ProjectStatus(enum.Enum):
    """Project status enumeration."""
    DRAFT = "draft"
    PLANNING = "planning"
    IN_PROGRESS = "in_progress"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TaskStatus(enum.Enum):
    """Task status enumeration."""
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class AgentStatus(enum.Enum):
    """Agent status enumeration."""
    IDLE = "idle"
    BUSY = "busy"
    ERROR = "error"
    OFFLINE = "offline"


class MessageType(enum.Enum):
    """Message type enumeration."""
    HUMAN_TO_AGENT = "human_to_agent"
    AGENT_TO_HUMAN = "agent_to_human"
    AGENT_TO_AGENT = "agent_to_agent"
    SYSTEM = "system"


class User(Base):
    """User model for authentication and project ownership."""
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    full_name = Column(String(100), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    owned_projects = relationship("Project", back_populates="owner")
    messages = relationship("Message", back_populates="user")


class Project(Base):
    """Project model for managing software projects."""
    
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, index=True)
    description = Column(Text)
    status = Column(Enum(ProjectStatus), default=ProjectStatus.DRAFT)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Project metadata
    charter = Column(JSON)  # Project charter document
    roadmap = Column(JSON)  # High-level roadmap
    requirements = Column(JSON)  # Project requirements
    constraints = Column(JSON)  # Project constraints and limitations
    
    # Timeline
    start_date = Column(DateTime(timezone=True))
    end_date = Column(DateTime(timezone=True))
    estimated_duration_days = Column(Integer)
    
    # Progress tracking
    progress_percentage = Column(Float, default=0.0)
    budget = Column(Float)
    actual_cost = Column(Float, default=0.0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    owner = relationship("User", back_populates="owned_projects")
    tasks = relationship("Task", back_populates="project", cascade="all, delete-orphan")
    agents = relationship("Agent", back_populates="project")
    messages = relationship("Message", back_populates="project")


class Task(Base):
    """Task model for individual work items."""
    
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    status = Column(Enum(TaskStatus), default=TaskStatus.PENDING)
    priority = Column(Integer, default=3)  # 1=High, 2=Medium, 3=Low
    
    # Task hierarchy
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    parent_task_id = Column(Integer, ForeignKey("tasks.id"))
    
    # Assignment
    assigned_agent_id = Column(Integer, ForeignKey("agents.id"))
    
    # Task details
    requirements = Column(JSON)  # Task-specific requirements
    deliverables = Column(JSON)  # Expected deliverables
    acceptance_criteria = Column(JSON)  # Acceptance criteria
    
    # Timeline
    estimated_hours = Column(Float)
    actual_hours = Column(Float, default=0.0)
    start_date = Column(DateTime(timezone=True))
    due_date = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    
    # Progress
    progress_percentage = Column(Float, default=0.0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    project = relationship("Project", back_populates="tasks")
    assigned_agent = relationship("Agent", back_populates="assigned_tasks")
    parent_task = relationship("Task", remote_side=[id])
    subtasks = relationship("Task", cascade="all, delete-orphan")
    messages = relationship("Message", back_populates="task")


class Agent(Base):
    """Agent model for AI agents in the system."""
    
    __tablename__ = "agents"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    agent_type = Column(String(50), nullable=False)  # discovery, planning, development, etc.
    description = Column(Text)
    status = Column(Enum(AgentStatus), default=AgentStatus.IDLE)
    
    # Agent configuration
    capabilities = Column(JSON)  # List of agent capabilities
    configuration = Column(JSON)  # Agent-specific configuration
    model_config = Column(JSON)  # AI model configuration
    
    # Assignment
    project_id = Column(Integer, ForeignKey("projects.id"))
    current_task_id = Column(Integer, ForeignKey("tasks.id"))
    
    # Performance metrics
    tasks_completed = Column(Integer, default=0)
    success_rate = Column(Float, default=0.0)
    average_completion_time = Column(Float, default=0.0)
    
    # State management
    memory_context = Column(JSON)  # Agent memory and context
    last_activity = Column(DateTime(timezone=True))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    project = relationship("Project", back_populates="agents")
    assigned_tasks = relationship("Task", back_populates="assigned_agent")
    sent_messages = relationship("Message", foreign_keys="Message.sender_agent_id", back_populates="sender_agent")
    received_messages = relationship("Message", foreign_keys="Message.recipient_agent_id", back_populates="recipient_agent")


class Message(Base):
    """Message model for communication between users and agents."""
    
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    message_type = Column(Enum(MessageType), nullable=False)
    
    # Context
    project_id = Column(Integer, ForeignKey("projects.id"))
    task_id = Column(Integer, ForeignKey("tasks.id"))
    
    # Participants
    user_id = Column(Integer, ForeignKey("users.id"))
    sender_agent_id = Column(Integer, ForeignKey("agents.id"))
    recipient_agent_id = Column(Integer, ForeignKey("agents.id"))
    
    # Message metadata
    metadata = Column(JSON)  # Additional message metadata
    attachments = Column(JSON)  # File attachments or references
    
    # Status
    is_read = Column(Boolean, default=False)
    is_system_message = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    read_at = Column(DateTime(timezone=True))
    
    # Relationships
    project = relationship("Project", back_populates="messages")
    task = relationship("Task", back_populates="messages")
    user = relationship("User", back_populates="messages")
    sender_agent = relationship("Agent", foreign_keys=[sender_agent_id], back_populates="sent_messages")
    recipient_agent = relationship("Agent", foreign_keys=[recipient_agent_id], back_populates="received_messages")


class WorkflowState(Base):
    """Workflow state tracking for projects."""
    
    __tablename__ = "workflow_states"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    current_phase = Column(String(50), nullable=False)  # discovery, planning, development, etc.
    previous_phase = Column(String(50))
    
    # State data
    phase_data = Column(JSON)  # Phase-specific data
    transition_conditions = Column(JSON)  # Conditions for phase transitions
    
    # Timestamps
    phase_started_at = Column(DateTime(timezone=True), server_default=func.now())
    phase_completed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    project = relationship("Project")


class Integration(Base):
    """External tool integrations."""
    
    __tablename__ = "integrations"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    integration_type = Column(String(50), nullable=False)  # jira, github, slack, etc.
    project_id = Column(Integer, ForeignKey("projects.id"))
    
    # Configuration
    config = Column(JSON)  # Integration-specific configuration
    credentials = Column(JSON)  # Encrypted credentials
    
    # Status
    is_active = Column(Boolean, default=True)
    last_sync = Column(DateTime(timezone=True))
    sync_status = Column(String(50), default="pending")
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    project = relationship("Project")
