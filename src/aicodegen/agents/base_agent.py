"""Base agent architecture for the multi-agent platform."""

import asyncio
import enum
import logging
from abc import abstractmethod
from datetime import datetime
from typing import Dict, Any, List, Optional, Union
from uuid import uuid4

from ..models.base import BaseAIModel
from ..database.models import Agent as AgentModel, Task as TaskModel, Message as MessageModel
from ..database.connection import get_db
from .agent_memory import AgentMemory


class AgentState(enum.Enum):
    """Agent state enumeration."""
    IDLE = "idle"
    BUSY = "busy"
    THINKING = "thinking"
    COMMUNICATING = "communicating"
    ERROR = "error"
    OFFLINE = "offline"


class AgentCapability(enum.Enum):
    """Agent capability enumeration."""
    CODE_GENERATION = "code_generation"
    REQUIREMENTS_ANALYSIS = "requirements_analysis"
    PROJECT_PLANNING = "project_planning"
    TESTING = "testing"
    DOCUMENTATION = "documentation"
    DEPLOYMENT = "deployment"
    MONITORING = "monitoring"
    RESEARCH = "research"
    DESIGN = "design"
    COMMUNICATION = "communication"


class TaskResult:
    """Result of task execution."""
    
    def __init__(
        self,
        success: bool,
        result: Any = None,
        error: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.success = success
        self.result = result
        self.error = error
        self.metadata = metadata or {}
        self.timestamp = datetime.utcnow()


class BaseAgent(BaseAIModel):
    """
    Base agent class extending BaseAIModel with agent-specific capabilities.
    
    This class provides the foundation for all specialized agents in the platform,
    including task execution, communication, memory management, and state tracking.
    """
    
    def __init__(
        self,
        agent_id: str,
        name: str,
        agent_type: str,
        config: Dict[str, Any],
        capabilities: List[AgentCapability],
        description: Optional[str] = None
    ):
        """
        Initialize the base agent.
        
        Args:
            agent_id: Unique identifier for the agent
            name: Human-readable name for the agent
            agent_type: Type/category of the agent
            config: Configuration dictionary for the agent
            capabilities: List of agent capabilities
            description: Optional description of the agent
        """
        super().__init__(config)
        
        self.agent_id = agent_id
        self.name = name
        self.agent_type = agent_type
        self.capabilities = capabilities
        self.description = description or f"{name} - {agent_type} agent"
        
        # Agent state management
        self.state = AgentState.IDLE
        self.current_task_id: Optional[str] = None
        self.project_id: Optional[str] = None
        
        # Performance tracking
        self.tasks_completed = 0
        self.tasks_failed = 0
        self.total_execution_time = 0.0
        
        # Initialize memory system
        self.memory = AgentMemory(agent_id=agent_id, config=config.get("memory", {}))
        
        # Set up logging
        self.logger = logging.getLogger(f"agent.{agent_type}.{agent_id}")
        
        # Communication callbacks
        self._message_handlers: Dict[str, callable] = {}
        self._status_callbacks: List[callable] = []
    
    @property
    def is_available(self) -> bool:
        """Check if agent is available for new tasks."""
        return self.state in [AgentState.IDLE]
    
    @property
    def success_rate(self) -> float:
        """Calculate agent success rate."""
        total_tasks = self.tasks_completed + self.tasks_failed
        if total_tasks == 0:
            return 0.0
        return self.tasks_completed / total_tasks
    
    @property
    def average_execution_time(self) -> float:
        """Calculate average task execution time."""
        if self.tasks_completed == 0:
            return 0.0
        return self.total_execution_time / self.tasks_completed
    
    async def execute_task(
        self,
        task_id: str,
        task_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> TaskResult:
        """
        Execute a task assigned to this agent.
        
        Args:
            task_id: Unique identifier for the task
            task_data: Task data and requirements
            context: Additional context for task execution
            
        Returns:
            TaskResult containing execution results
        """
        if not self.is_available:
            return TaskResult(
                success=False,
                error=f"Agent {self.name} is not available (current state: {self.state.value})"
            )
        
        self.logger.info(f"Starting task execution: {task_id}")
        start_time = datetime.utcnow()
        
        try:
            # Update agent state
            await self.update_status(AgentState.BUSY)
            self.current_task_id = task_id
            
            # Store task context in memory
            await self.memory.store_context(
                context_type="task_execution",
                content={
                    "task_id": task_id,
                    "task_data": task_data,
                    "context": context,
                    "started_at": start_time.isoformat()
                }
            )
            
            # Execute the task (implemented by subclasses)
            result = await self._execute_task_impl(task_id, task_data, context)
            
            # Update performance metrics
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            self.total_execution_time += execution_time
            
            if result.success:
                self.tasks_completed += 1
                self.logger.info(f"Task {task_id} completed successfully in {execution_time:.2f}s")
            else:
                self.tasks_failed += 1
                self.logger.error(f"Task {task_id} failed: {result.error}")
            
            # Store result in memory
            await self.memory.store_context(
                context_type="task_result",
                content={
                    "task_id": task_id,
                    "success": result.success,
                    "result": result.result,
                    "error": result.error,
                    "execution_time": execution_time,
                    "completed_at": datetime.utcnow().isoformat()
                }
            )
            
            return result
            
        except Exception as e:
            self.tasks_failed += 1
            error_msg = f"Unexpected error during task execution: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            
            return TaskResult(
                success=False,
                error=error_msg,
                metadata={"exception_type": type(e).__name__}
            )
        
        finally:
            # Reset agent state
            await self.update_status(AgentState.IDLE)
            self.current_task_id = None
    
    @abstractmethod
    async def _execute_task_impl(
        self,
        task_id: str,
        task_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> TaskResult:
        """
        Implementation-specific task execution logic.
        
        This method must be implemented by each specialized agent.
        
        Args:
            task_id: Unique identifier for the task
            task_data: Task data and requirements
            context: Additional context for task execution
            
        Returns:
            TaskResult containing execution results
        """
        pass
    
    async def communicate(
        self,
        recipient: Union[str, "BaseAgent"],
        message: str,
        message_type: str = "agent_to_agent",
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Send a message to another agent or human.
        
        Args:
            recipient: Recipient agent ID or agent instance
            message: Message content
            message_type: Type of message
            metadata: Additional message metadata
            
        Returns:
            True if message was sent successfully
        """
        try:
            await self.update_status(AgentState.COMMUNICATING)
            
            recipient_id = recipient if isinstance(recipient, str) else recipient.agent_id
            
            # Store message in memory
            await self.memory.store_context(
                context_type="communication",
                content={
                    "recipient_id": recipient_id,
                    "message": message,
                    "message_type": message_type,
                    "metadata": metadata,
                    "sent_at": datetime.utcnow().isoformat()
                }
            )
            
            # TODO: Implement actual message routing through communication hub
            self.logger.info(f"Sent message to {recipient_id}: {message[:100]}...")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send message: {str(e)}")
            return False
        
        finally:
            await self.update_status(AgentState.IDLE)
    
    async def receive_message(
        self,
        sender_id: str,
        message: str,
        message_type: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Receive and process a message from another agent or human.
        
        Args:
            sender_id: ID of the message sender
            message: Message content
            message_type: Type of message
            metadata: Additional message metadata
        """
        try:
            # Store received message in memory
            await self.memory.store_context(
                context_type="received_message",
                content={
                    "sender_id": sender_id,
                    "message": message,
                    "message_type": message_type,
                    "metadata": metadata,
                    "received_at": datetime.utcnow().isoformat()
                }
            )
            
            # Process message through registered handlers
            if message_type in self._message_handlers:
                await self._message_handlers[message_type](sender_id, message, metadata)
            else:
                # Default message processing
                await self._process_message_default(sender_id, message, message_type, metadata)
            
            self.logger.info(f"Processed message from {sender_id}: {message[:100]}...")
            
        except Exception as e:
            self.logger.error(f"Failed to process message from {sender_id}: {str(e)}")
    
    async def _process_message_default(
        self,
        sender_id: str,
        message: str,
        message_type: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Default message processing logic."""
        # Can be overridden by subclasses for custom message handling
        pass
    
    async def update_status(self, new_state: AgentState) -> None:
        """
        Update agent status and notify callbacks.
        
        Args:
            new_state: New agent state
        """
        old_state = self.state
        self.state = new_state
        
        self.logger.debug(f"Agent state changed: {old_state.value} -> {new_state.value}")
        
        # Store state change in memory
        await self.memory.store_context(
            context_type="state_change",
            content={
                "old_state": old_state.value,
                "new_state": new_state.value,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        
        # Notify status callbacks
        for callback in self._status_callbacks:
            try:
                await callback(self.agent_id, old_state, new_state)
            except Exception as e:
                self.logger.error(f"Status callback failed: {str(e)}")
    
    def register_message_handler(self, message_type: str, handler: callable) -> None:
        """
        Register a message handler for a specific message type.
        
        Args:
            message_type: Type of message to handle
            handler: Async function to handle the message
        """
        self._message_handlers[message_type] = handler
    
    def register_status_callback(self, callback: callable) -> None:
        """
        Register a callback for status changes.
        
        Args:
            callback: Async function to call on status changes
        """
        self._status_callbacks.append(callback)
    
    async def get_context(self, context_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Retrieve context from agent memory.
        
        Args:
            context_type: Optional filter by context type
            
        Returns:
            List of context entries
        """
        return await self.memory.get_context(context_type=context_type)
    
    async def clear_context(self, context_type: Optional[str] = None) -> None:
        """
        Clear context from agent memory.
        
        Args:
            context_type: Optional filter by context type
        """
        await self.memory.clear_context(context_type=context_type)
    
    def get_capabilities(self) -> List[str]:
        """Get list of agent capabilities."""
        return [cap.value for cap in self.capabilities]
    
    def has_capability(self, capability: Union[str, AgentCapability]) -> bool:
        """
        Check if agent has a specific capability.
        
        Args:
            capability: Capability to check
            
        Returns:
            True if agent has the capability
        """
        if isinstance(capability, str):
            return capability in [cap.value for cap in self.capabilities]
        return capability in self.capabilities
    
    def get_status_info(self) -> Dict[str, Any]:
        """
        Get comprehensive agent status information.
        
        Returns:
            Dictionary containing agent status and metrics
        """
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "type": self.agent_type,
            "state": self.state.value,
            "current_task_id": self.current_task_id,
            "project_id": self.project_id,
            "capabilities": self.get_capabilities(),
            "performance": {
                "tasks_completed": self.tasks_completed,
                "tasks_failed": self.tasks_failed,
                "success_rate": self.success_rate,
                "average_execution_time": self.average_execution_time
            },
            "is_available": self.is_available
        }
    
    async def shutdown(self) -> None:
        """Gracefully shutdown the agent."""
        self.logger.info(f"Shutting down agent {self.name}")
        
        try:
            # Update state to offline
            await self.update_status(AgentState.OFFLINE)
            
            # Close memory connections
            await self.memory.close()
            
            self.logger.info(f"Agent {self.name} shutdown complete")
            
        except Exception as e:
            self.logger.error(f"Error during agent shutdown: {str(e)}")
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(id={self.agent_id}, name={self.name}, state={self.state.value})>"
