"""Agent memory system using ChromaDB for context storage and retrieval."""

import asyncio
import enum
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union
from uuid import uuid4

try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    chromadb = None


class MemoryType(enum.Enum):
    """Types of memory storage."""
    SHORT_TERM = "short_term"  # Recent context, cleared frequently
    LONG_TERM = "long_term"    # Persistent knowledge and experiences
    WORKING = "working"        # Current task context
    EPISODIC = "episodic"      # Specific events and interactions
    SEMANTIC = "semantic"      # General knowledge and facts


class MemoryEntry:
    """Represents a single memory entry."""
    
    def __init__(
        self,
        content: Union[str, Dict[str, Any]],
        memory_type: MemoryType,
        context_type: str,
        metadata: Optional[Dict[str, Any]] = None,
        importance: float = 0.5,
        timestamp: Optional[datetime] = None
    ):
        self.id = str(uuid4())
        self.content = content if isinstance(content, str) else json.dumps(content)
        self.memory_type = memory_type
        self.context_type = context_type
        self.metadata = metadata or {}
        self.importance = max(0.0, min(1.0, importance))  # Clamp between 0 and 1
        self.timestamp = timestamp or datetime.utcnow()
        self.access_count = 0
        self.last_accessed = self.timestamp
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert memory entry to dictionary."""
        return {
            "id": self.id,
            "content": self.content,
            "memory_type": self.memory_type.value,
            "context_type": self.context_type,
            "metadata": self.metadata,
            "importance": self.importance,
            "timestamp": self.timestamp.isoformat(),
            "access_count": self.access_count,
            "last_accessed": self.last_accessed.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MemoryEntry":
        """Create memory entry from dictionary."""
        entry = cls(
            content=data["content"],
            memory_type=MemoryType(data["memory_type"]),
            context_type=data["context_type"],
            metadata=data.get("metadata", {}),
            importance=data.get("importance", 0.5),
            timestamp=datetime.fromisoformat(data["timestamp"])
        )
        entry.id = data["id"]
        entry.access_count = data.get("access_count", 0)
        entry.last_accessed = datetime.fromisoformat(data.get("last_accessed", data["timestamp"]))
        return entry


class AgentMemory:
    """
    Agent memory system using ChromaDB for vector storage and retrieval.
    
    Provides persistent memory capabilities for agents including:
    - Context storage and retrieval
    - Semantic search over past experiences
    - Memory consolidation and cleanup
    - Different memory types (short-term, long-term, working, etc.)
    """
    
    def __init__(self, agent_id: str, config: Optional[Dict[str, Any]] = None):
        """
        Initialize agent memory system.
        
        Args:
            agent_id: Unique identifier for the agent
            config: Memory configuration options
        """
        self.agent_id = agent_id
        self.config = config or {}
        self.logger = logging.getLogger(f"memory.{agent_id}")
        
        # Memory configuration
        self.max_short_term_entries = self.config.get("max_short_term_entries", 100)
        self.max_working_entries = self.config.get("max_working_entries", 50)
        self.cleanup_interval_hours = self.config.get("cleanup_interval_hours", 24)
        self.importance_threshold = self.config.get("importance_threshold", 0.3)
        
        # ChromaDB setup
        self.chroma_client = None
        self.collection = None
        self._initialize_chromadb()
        
        # In-memory cache for recent entries
        self._memory_cache: Dict[str, MemoryEntry] = {}
        self._last_cleanup = datetime.utcnow()
    
    def _initialize_chromadb(self) -> None:
        """Initialize ChromaDB client and collection."""
        if not CHROMADB_AVAILABLE:
            self.logger.warning("ChromaDB not available, using in-memory storage only")
            return
        
        try:
            # Configure ChromaDB settings
            chroma_settings = Settings(
                chroma_db_impl="duckdb+parquet",
                persist_directory=self.config.get("persist_directory", f"./chroma_db/{self.agent_id}"),
                anonymized_telemetry=False
            )
            
            # Initialize client
            self.chroma_client = chromadb.Client(chroma_settings)
            
            # Get or create collection for this agent
            collection_name = f"agent_{self.agent_id}_memory"
            try:
                self.collection = self.chroma_client.get_collection(collection_name)
                self.logger.info(f"Loaded existing memory collection: {collection_name}")
            except Exception:
                self.collection = self.chroma_client.create_collection(
                    name=collection_name,
                    metadata={"agent_id": self.agent_id, "created_at": datetime.utcnow().isoformat()}
                )
                self.logger.info(f"Created new memory collection: {collection_name}")
                
        except Exception as e:
            self.logger.error(f"Failed to initialize ChromaDB: {str(e)}")
            self.chroma_client = None
            self.collection = None
    
    async def store_context(
        self,
        context_type: str,
        content: Union[str, Dict[str, Any]],
        memory_type: MemoryType = MemoryType.SHORT_TERM,
        importance: float = 0.5,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Store context in agent memory.
        
        Args:
            context_type: Type of context (e.g., "task_execution", "communication")
            content: Content to store
            memory_type: Type of memory storage
            importance: Importance score (0.0 to 1.0)
            metadata: Additional metadata
            
        Returns:
            Memory entry ID
        """
        try:
            # Create memory entry
            entry = MemoryEntry(
                content=content,
                memory_type=memory_type,
                context_type=context_type,
                metadata=metadata,
                importance=importance
            )
            
            # Store in cache
            self._memory_cache[entry.id] = entry
            
            # Store in ChromaDB if available
            if self.collection is not None:
                await self._store_in_chromadb(entry)
            
            # Trigger cleanup if needed
            await self._maybe_cleanup()
            
            self.logger.debug(f"Stored memory entry: {context_type} ({entry.id})")
            return entry.id
            
        except Exception as e:
            self.logger.error(f"Failed to store context: {str(e)}")
            raise
    
    async def _store_in_chromadb(self, entry: MemoryEntry) -> None:
        """Store memory entry in ChromaDB."""
        try:
            # Prepare document and metadata for ChromaDB
            document = entry.content
            metadata = {
                "agent_id": self.agent_id,
                "memory_type": entry.memory_type.value,
                "context_type": entry.context_type,
                "importance": entry.importance,
                "timestamp": entry.timestamp.isoformat(),
                "access_count": entry.access_count,
                **entry.metadata
            }
            
            # Add to collection
            self.collection.add(
                documents=[document],
                metadatas=[metadata],
                ids=[entry.id]
            )
            
        except Exception as e:
            self.logger.error(f"Failed to store in ChromaDB: {str(e)}")
            raise
    
    async def get_context(
        self,
        context_type: Optional[str] = None,
        memory_type: Optional[MemoryType] = None,
        limit: int = 50,
        min_importance: float = 0.0
    ) -> List[Dict[str, Any]]:
        """
        Retrieve context from agent memory.
        
        Args:
            context_type: Filter by context type
            memory_type: Filter by memory type
            limit: Maximum number of entries to return
            min_importance: Minimum importance threshold
            
        Returns:
            List of memory entries as dictionaries
        """
        try:
            results = []
            
            # Search in cache first
            for entry in self._memory_cache.values():
                if self._matches_filters(entry, context_type, memory_type, min_importance):
                    entry.access_count += 1
                    entry.last_accessed = datetime.utcnow()
                    results.append(entry.to_dict())
            
            # Search in ChromaDB if available and we need more results
            if self.collection is not None and len(results) < limit:
                chromadb_results = await self._search_chromadb(
                    context_type=context_type,
                    memory_type=memory_type,
                    limit=limit - len(results),
                    min_importance=min_importance
                )
                results.extend(chromadb_results)
            
            # Sort by timestamp (most recent first) and limit
            results.sort(key=lambda x: x["timestamp"], reverse=True)
            return results[:limit]
            
        except Exception as e:
            self.logger.error(f"Failed to retrieve context: {str(e)}")
            return []
    
    async def _search_chromadb(
        self,
        context_type: Optional[str] = None,
        memory_type: Optional[MemoryType] = None,
        limit: int = 50,
        min_importance: float = 0.0
    ) -> List[Dict[str, Any]]:
        """Search ChromaDB for matching entries."""
        try:
            # Build where clause for filtering
            where_clause = {"agent_id": self.agent_id}
            
            if context_type:
                where_clause["context_type"] = context_type
            
            if memory_type:
                where_clause["memory_type"] = memory_type.value
            
            if min_importance > 0.0:
                where_clause["importance"] = {"$gte": min_importance}
            
            # Query ChromaDB
            results = self.collection.get(
                where=where_clause,
                limit=limit,
                include=["documents", "metadatas"]
            )
            
            # Convert to memory entry format
            entries = []
            for i, doc_id in enumerate(results["ids"]):
                if doc_id not in self._memory_cache:  # Avoid duplicates
                    entry_data = {
                        "id": doc_id,
                        "content": results["documents"][i],
                        "memory_type": results["metadatas"][i]["memory_type"],
                        "context_type": results["metadatas"][i]["context_type"],
                        "importance": results["metadatas"][i]["importance"],
                        "timestamp": results["metadatas"][i]["timestamp"],
                        "access_count": results["metadatas"][i].get("access_count", 0),
                        "last_accessed": results["metadatas"][i].get("last_accessed", results["metadatas"][i]["timestamp"]),
                        "metadata": {k: v for k, v in results["metadatas"][i].items() 
                                   if k not in ["agent_id", "memory_type", "context_type", "importance", "timestamp", "access_count"]}
                    }
                    entries.append(entry_data)
            
            return entries
            
        except Exception as e:
            self.logger.error(f"Failed to search ChromaDB: {str(e)}")
            return []
    
    async def semantic_search(
        self,
        query: str,
        limit: int = 10,
        memory_type: Optional[MemoryType] = None,
        min_importance: float = 0.0
    ) -> List[Dict[str, Any]]:
        """
        Perform semantic search over agent memory.
        
        Args:
            query: Search query
            limit: Maximum number of results
            memory_type: Filter by memory type
            min_importance: Minimum importance threshold
            
        Returns:
            List of relevant memory entries
        """
        if self.collection is None:
            self.logger.warning("ChromaDB not available for semantic search")
            return []
        
        try:
            # Build where clause
            where_clause = {"agent_id": self.agent_id}
            
            if memory_type:
                where_clause["memory_type"] = memory_type.value
            
            if min_importance > 0.0:
                where_clause["importance"] = {"$gte": min_importance}
            
            # Perform semantic search
            results = self.collection.query(
                query_texts=[query],
                n_results=limit,
                where=where_clause,
                include=["documents", "metadatas", "distances"]
            )
            
            # Convert results to memory entry format
            entries = []
            for i, doc_id in enumerate(results["ids"][0]):
                entry_data = {
                    "id": doc_id,
                    "content": results["documents"][0][i],
                    "memory_type": results["metadatas"][0][i]["memory_type"],
                    "context_type": results["metadatas"][0][i]["context_type"],
                    "importance": results["metadatas"][0][i]["importance"],
                    "timestamp": results["metadatas"][0][i]["timestamp"],
                    "similarity_score": 1.0 - results["distances"][0][i],  # Convert distance to similarity
                    "metadata": {k: v for k, v in results["metadatas"][0][i].items() 
                               if k not in ["agent_id", "memory_type", "context_type", "importance", "timestamp"]}
                }
                entries.append(entry_data)
            
            return entries
            
        except Exception as e:
            self.logger.error(f"Failed to perform semantic search: {str(e)}")
            return []
    
    async def clear_context(
        self,
        context_type: Optional[str] = None,
        memory_type: Optional[MemoryType] = None,
        older_than: Optional[timedelta] = None
    ) -> int:
        """
        Clear context from agent memory.
        
        Args:
            context_type: Filter by context type
            memory_type: Filter by memory type
            older_than: Only clear entries older than this timedelta
            
        Returns:
            Number of entries cleared
        """
        try:
            cleared_count = 0
            cutoff_time = datetime.utcnow() - older_than if older_than else None
            
            # Clear from cache
            to_remove = []
            for entry_id, entry in self._memory_cache.items():
                if self._should_clear_entry(entry, context_type, memory_type, cutoff_time):
                    to_remove.append(entry_id)
            
            for entry_id in to_remove:
                del self._memory_cache[entry_id]
                cleared_count += 1
            
            # Clear from ChromaDB if available
            if self.collection is not None:
                chromadb_cleared = await self._clear_from_chromadb(context_type, memory_type, cutoff_time)
                cleared_count += chromadb_cleared
            
            self.logger.info(f"Cleared {cleared_count} memory entries")
            return cleared_count
            
        except Exception as e:
            self.logger.error(f"Failed to clear context: {str(e)}")
            return 0
    
    async def _clear_from_chromadb(
        self,
        context_type: Optional[str] = None,
        memory_type: Optional[MemoryType] = None,
        cutoff_time: Optional[datetime] = None
    ) -> int:
        """Clear entries from ChromaDB based on filters."""
        try:
            # Build where clause
            where_clause = {"agent_id": self.agent_id}
            
            if context_type:
                where_clause["context_type"] = context_type
            
            if memory_type:
                where_clause["memory_type"] = memory_type.value
            
            if cutoff_time:
                where_clause["timestamp"] = {"$lt": cutoff_time.isoformat()}
            
            # Get matching entries
            results = self.collection.get(
                where=where_clause,
                include=["documents"]
            )
            
            # Delete the entries
            if results["ids"]:
                self.collection.delete(ids=results["ids"])
                return len(results["ids"])
            
            return 0
            
        except Exception as e:
            self.logger.error(f"Failed to clear from ChromaDB: {str(e)}")
            return 0
    
    async def _maybe_cleanup(self) -> None:
        """Perform memory cleanup if needed."""
        now = datetime.utcnow()
        if (now - self._last_cleanup).total_seconds() > self.cleanup_interval_hours * 3600:
            await self._cleanup_memory()
            self._last_cleanup = now
    
    async def _cleanup_memory(self) -> None:
        """Perform memory cleanup and consolidation."""
        try:
            self.logger.info("Starting memory cleanup")
            
            # Clean up short-term memory if it exceeds limits
            short_term_entries = [
                entry for entry in self._memory_cache.values()
                if entry.memory_type == MemoryType.SHORT_TERM
            ]
            
            if len(short_term_entries) > self.max_short_term_entries:
                # Sort by importance and recency, keep the most important/recent
                short_term_entries.sort(
                    key=lambda x: (x.importance, x.timestamp),
                    reverse=True
                )
                
                to_remove = short_term_entries[self.max_short_term_entries:]
                for entry in to_remove:
                    if entry.id in self._memory_cache:
                        del self._memory_cache[entry.id]
            
            # Clean up working memory
            working_entries = [
                entry for entry in self._memory_cache.values()
                if entry.memory_type == MemoryType.WORKING
            ]
            
            if len(working_entries) > self.max_working_entries:
                working_entries.sort(key=lambda x: x.timestamp, reverse=True)
                to_remove = working_entries[self.max_working_entries:]
                for entry in to_remove:
                    if entry.id in self._memory_cache:
                        del self._memory_cache[entry.id]
            
            # Remove low-importance entries older than 7 days
            await self.clear_context(
                older_than=timedelta(days=7),
                memory_type=None  # Apply to all types
            )
            
            self.logger.info("Memory cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Memory cleanup failed: {str(e)}")
    
    def _matches_filters(
        self,
        entry: MemoryEntry,
        context_type: Optional[str],
        memory_type: Optional[MemoryType],
        min_importance: float
    ) -> bool:
        """Check if entry matches the given filters."""
        if context_type and entry.context_type != context_type:
            return False
        
        if memory_type and entry.memory_type != memory_type:
            return False
        
        if entry.importance < min_importance:
            return False
        
        return True
    
    def _should_clear_entry(
        self,
        entry: MemoryEntry,
        context_type: Optional[str],
        memory_type: Optional[MemoryType],
        cutoff_time: Optional[datetime]
    ) -> bool:
        """Check if entry should be cleared based on filters."""
        if context_type and entry.context_type != context_type:
            return False
        
        if memory_type and entry.memory_type != memory_type:
            return False
        
        if cutoff_time and entry.timestamp > cutoff_time:
            return False
        
        return True
    
    async def get_memory_stats(self) -> Dict[str, Any]:
        """
        Get memory system statistics.
        
        Returns:
            Dictionary containing memory statistics
        """
        try:
            stats = {
                "agent_id": self.agent_id,
                "cache_size": len(self._memory_cache),
                "memory_types": {},
                "context_types": {},
                "total_entries": 0,
                "chromadb_available": self.collection is not None
            }
            
            # Analyze cache entries
            for entry in self._memory_cache.values():
                stats["memory_types"][entry.memory_type.value] = stats["memory_types"].get(entry.memory_type.value, 0) + 1
                stats["context_types"][entry.context_type] = stats["context_types"].get(entry.context_type, 0) + 1
            
            # Get ChromaDB stats if available
            if self.collection is not None:
                chromadb_count = self.collection.count()
                stats["total_entries"] = chromadb_count
            else:
                stats["total_entries"] = len(self._memory_cache)
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Failed to get memory stats: {str(e)}")
            return {"error": str(e)}
    
    async def close(self) -> None:
        """Close memory system and cleanup resources."""
        try:
            self.logger.info("Closing agent memory system")
            
            # Clear cache
            self._memory_cache.clear()
            
            # Close ChromaDB connection if available
            if self.chroma_client is not None:
                # ChromaDB doesn't have an explicit close method
                self.chroma_client = None
                self.collection = None
            
            self.logger.info("Agent memory system closed")
            
        except Exception as e:
            self.logger.error(f"Error closing memory system: {str(e)}")


# Fallback in-memory implementation when ChromaDB is not available
class InMemoryAgentMemory(AgentMemory):
    """Fallback in-memory implementation of agent memory."""
    
    def __init__(self, agent_id: str, config: Optional[Dict[str, Any]] = None):
        """Initialize in-memory agent memory."""
        self.agent_id = agent_id
        self.config = config or {}
        self.logger = logging.getLogger(f"memory.{agent_id}")
        
        # Memory storage
        self._memory_store: Dict[str, MemoryEntry] = {}
        self._last_cleanup = datetime.utcnow()
        
        self.logger.warning("Using in-memory storage - memory will not persist between sessions")
    
    async def store_context(
        self,
        context_type: str,
        content: Union[str, Dict[str, Any]],
        memory_type: MemoryType = MemoryType.SHORT_TERM,
        importance: float = 0.5,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Store context in memory."""
        entry = MemoryEntry(
            content=content,
            memory_type=memory_type,
            context_type=context_type,
            metadata=metadata,
            importance=importance
        )
        
        self._memory_store[entry.id] = entry
        return entry.id
    
    async def get_context(
        self,
        context_type: Optional[str] = None,
        memory_type: Optional[MemoryType] = None,
        limit: int = 50,
        min_importance: float = 0.0
    ) -> List[Dict[str, Any]]:
        """Retrieve context from memory."""
        results = []
        
        for entry in self._memory_store.values():
            if self._matches_filters(entry, context_type, memory_type, min_importance):
                entry.access_count += 1
                entry.last_accessed = datetime.utcnow()
                results.append(entry.to_dict())
        
        # Sort by timestamp and limit
        results.sort(key=lambda x: x["timestamp"], reverse=True)
        return results[:limit]
    
    async def semantic_search(
        self,
        query: str,
        limit: int = 10,
        memory_type: Optional[MemoryType] = None,
        min_importance: float = 0.0
    ) -> List[Dict[str, Any]]:
        """Simple text-based search (no semantic capabilities)."""
        results = []
        query_lower = query.lower()
        
        for entry in self._memory_store.values():
            if (memory_type is None or entry.memory_type == memory_type) and \
               entry.importance >= min_importance and \
               query_lower in entry.content.lower():
                entry_dict = entry.to_dict()
                entry_dict["similarity_score"] = 0.5  # Placeholder score
                results.append(entry_dict)
        
        return results[:limit]
    
    async def clear_context(
        self,
        context_type: Optional[str] = None,
        memory_type: Optional[MemoryType] = None,
        older_than: Optional[timedelta] = None
    ) -> int:
        """Clear context from memory."""
        cutoff_time = datetime.utcnow() - older_than if older_than else None
        to_remove = []
        
        for entry_id, entry in self._memory_store.items():
            if self._should_clear_entry(entry, context_type, memory_type, cutoff_time):
                to_remove.append(entry_id)
        
        for entry_id in to_remove:
            del self._memory_store[entry_id]
        
        return len(to_remove)
    
    async def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory statistics."""
        stats = {
            "agent_id": self.agent_id,
            "total_entries": len(self._memory_store),
            "memory_types": {},
            "context_types": {},
            "chromadb_available": False
        }
        
        for entry in self._memory_store.values():
            stats["memory_types"][entry.memory_type.value] = stats["memory_types"].get(entry.memory_type.value, 0) + 1
            stats["context_types"][entry.context_type] = stats["context_types"].get(entry.context_type, 0) + 1
        
        return stats
    
    async def close(self) -> None:
        """Close memory system."""
        self._memory_store.clear()


# Factory function to create appropriate memory implementation
def create_agent_memory(agent_id: str, config: Optional[Dict[str, Any]] = None) -> AgentMemory:
    """
    Create agent memory instance based on availability of ChromaDB.
    
    Args:
        agent_id: Unique identifier for the agent
        config: Memory configuration options
        
    Returns:
        AgentMemory instance (ChromaDB-based or in-memory fallback)
    """
    if CHROMADB_AVAILABLE:
        return AgentMemory(agent_id, config)
    else:
        return InMemoryAgentMemory(agent_id, config)
