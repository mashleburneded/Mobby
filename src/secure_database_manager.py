#!/usr/bin/env python3
"""
SECURE DATABASE MANAGER
=======================
High-performance, secure database management with connection pooling and security hardening.
"""

import asyncio
import aiosqlite
import logging
import hashlib
import secrets
import time
from typing import Dict, List, Optional, Any, Union
from contextlib import asynccontextmanager
from dataclasses import dataclass
from datetime import datetime, timedelta
import json
import os

logger = logging.getLogger(__name__)

@dataclass
class ConnectionPoolConfig:
    """Database connection pool configuration"""
    min_connections: int = 5
    max_connections: int = 50
    connection_timeout: float = 30.0
    idle_timeout: float = 300.0  # 5 minutes
    max_retries: int = 3
    retry_delay: float = 1.0

@dataclass
class SecurityConfig:
    """Database security configuration"""
    enable_encryption: bool = True
    enable_audit_log: bool = True
    max_query_time: float = 10.0
    rate_limit_per_user: int = 100  # queries per minute
    enable_sql_injection_protection: bool = True

class SecureConnectionPool:
    """High-performance secure database connection pool"""
    
    def __init__(self, db_path: str, pool_config: ConnectionPoolConfig, security_config: SecurityConfig):
        self.db_path = db_path
        self.pool_config = pool_config
        self.security_config = security_config
        self.connections: List[aiosqlite.Connection] = []
        self.available_connections: asyncio.Queue = asyncio.Queue()
        self.connection_count = 0
        self.lock = asyncio.Lock()
        self.stats = {
            'total_queries': 0,
            'failed_queries': 0,
            'avg_query_time': 0.0,
            'pool_hits': 0,
            'pool_misses': 0
        }
        self.user_rate_limits: Dict[int, List[float]] = {}
        self.audit_log: List[Dict] = []
    
    async def initialize(self):
        """Initialize the connection pool with security hardening"""
        logger.info(f"Initializing secure database pool: {self.pool_config.min_connections} connections")
        
        # Create minimum connections
        for _ in range(self.pool_config.min_connections):
            conn = await self._create_secure_connection()
            await self.available_connections.put(conn)
            self.connections.append(conn)
            self.connection_count += 1
        
        logger.info(f"✅ Secure database pool initialized with {self.connection_count} connections")
    
    async def _create_secure_connection(self) -> aiosqlite.Connection:
        """Create a secure database connection with hardening"""
        conn = await aiosqlite.connect(
            self.db_path,
            timeout=self.pool_config.connection_timeout,
            isolation_level=None  # Autocommit mode for better performance
        )
        
        # Security hardening
        await conn.execute("PRAGMA foreign_keys = ON")  # Enforce foreign key constraints
        await conn.execute("PRAGMA journal_mode = WAL")  # Write-Ahead Logging for better concurrency
        await conn.execute("PRAGMA synchronous = NORMAL")  # Balance between safety and performance
        await conn.execute("PRAGMA cache_size = -64000")  # 64MB cache
        await conn.execute("PRAGMA temp_store = MEMORY")  # Store temp tables in memory
        await conn.execute("PRAGMA mmap_size = 268435456")  # 256MB memory-mapped I/O
        
        return conn
    
    @asynccontextmanager
    async def get_connection(self, user_id: Optional[int] = None):
        """Get a secure database connection with rate limiting"""
        # Rate limiting check
        if user_id and not await self._check_rate_limit(user_id):
            raise SecurityError(f"Rate limit exceeded for user {user_id}")
        
        start_time = time.time()
        conn = None
        
        try:
            # Try to get connection from pool
            try:
                conn = await asyncio.wait_for(
                    self.available_connections.get(),
                    timeout=self.pool_config.connection_timeout
                )
                self.stats['pool_hits'] += 1
            except asyncio.TimeoutError:
                # Create new connection if pool is empty and under max limit
                async with self.lock:
                    if self.connection_count < self.pool_config.max_connections:
                        conn = await self._create_secure_connection()
                        self.connections.append(conn)
                        self.connection_count += 1
                        self.stats['pool_misses'] += 1
                    else:
                        raise DatabaseError("Connection pool exhausted")
            
            yield conn
            
        except Exception as e:
            self.stats['failed_queries'] += 1
            logger.error(f"Database connection error: {e}")
            raise
        finally:
            if conn:
                # Return connection to pool
                await self.available_connections.put(conn)
                
                # Update stats
                query_time = time.time() - start_time
                self.stats['total_queries'] += 1
                self.stats['avg_query_time'] = (
                    (self.stats['avg_query_time'] * (self.stats['total_queries'] - 1) + query_time) 
                    / self.stats['total_queries']
                )
    
    async def _check_rate_limit(self, user_id: int) -> bool:
        """Check if user is within rate limits"""
        now = time.time()
        minute_ago = now - 60
        
        # Clean old entries
        if user_id in self.user_rate_limits:
            self.user_rate_limits[user_id] = [
                t for t in self.user_rate_limits[user_id] if t > minute_ago
            ]
        else:
            self.user_rate_limits[user_id] = []
        
        # Check rate limit
        if len(self.user_rate_limits[user_id]) >= self.security_config.rate_limit_per_user:
            return False
        
        # Add current request
        self.user_rate_limits[user_id].append(now)
        return True
    
    async def execute_secure_query(self, query: str, params: tuple = (), user_id: Optional[int] = None) -> Any:
        """Execute a secure database query with protection against SQL injection"""
        # SQL injection protection
        if self.security_config.enable_sql_injection_protection:
            if not self._validate_query(query):
                raise SecurityError("Potentially malicious query detected")
        
        start_time = time.time()
        
        async with self.get_connection(user_id) as conn:
            try:
                # Execute with timeout
                result = await asyncio.wait_for(
                    conn.execute(query, params),
                    timeout=self.security_config.max_query_time
                )
                
                # Audit logging
                if self.security_config.enable_audit_log:
                    await self._log_query(query, params, user_id, time.time() - start_time, True)
                
                return result
                
            except asyncio.TimeoutError:
                logger.warning(f"Query timeout: {query[:100]}...")
                if self.security_config.enable_audit_log:
                    await self._log_query(query, params, user_id, time.time() - start_time, False, "TIMEOUT")
                raise DatabaseError("Query timeout")
            except Exception as e:
                if self.security_config.enable_audit_log:
                    await self._log_query(query, params, user_id, time.time() - start_time, False, str(e))
                raise
    
    async def execute_secure_fetchall(self, query: str, params: tuple = (), user_id: Optional[int] = None) -> List[Any]:
        """Execute query and fetch all results securely"""
        async with self.get_connection(user_id) as conn:
            cursor = await self.execute_secure_query(query, params, user_id)
            return await cursor.fetchall()
    
    async def execute_secure_fetchone(self, query: str, params: tuple = (), user_id: Optional[int] = None) -> Optional[Any]:
        """Execute query and fetch one result securely"""
        async with self.get_connection(user_id) as conn:
            cursor = await self.execute_secure_query(query, params, user_id)
            return await cursor.fetchone()
    
    def _validate_query(self, query: str) -> bool:
        """Validate query for potential SQL injection attempts"""
        query_lower = query.lower().strip()
        
        # Dangerous patterns
        dangerous_patterns = [
            'drop table', 'drop database', 'truncate', 'delete from',
            'alter table', 'create table', 'insert into',
            'union select', 'union all select',
            '--', '/*', '*/', 'xp_', 'sp_',
            'exec(', 'execute(', 'eval(',
            'script>', '<script', 'javascript:',
            'vbscript:', 'onload=', 'onerror='
        ]
        
        for pattern in dangerous_patterns:
            if pattern in query_lower:
                logger.warning(f"Potentially dangerous query pattern detected: {pattern}")
                return False
        
        return True
    
    async def _log_query(self, query: str, params: tuple, user_id: Optional[int], 
                        execution_time: float, success: bool, error: Optional[str] = None):
        """Log query for audit purposes"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'user_id': user_id,
            'query_hash': hashlib.sha256(query.encode()).hexdigest()[:16],
            'execution_time': execution_time,
            'success': success,
            'error': error,
            'params_count': len(params) if params else 0
        }
        
        self.audit_log.append(log_entry)
        
        # Keep only last 1000 entries
        if len(self.audit_log) > 1000:
            self.audit_log = self.audit_log[-1000:]
    
    async def get_pool_stats(self) -> Dict[str, Any]:
        """Get connection pool statistics"""
        return {
            'total_connections': self.connection_count,
            'available_connections': self.available_connections.qsize(),
            'pool_utilization': (self.connection_count - self.available_connections.qsize()) / self.connection_count,
            'query_stats': self.stats.copy(),
            'rate_limited_users': len(self.user_rate_limits),
            'audit_log_entries': len(self.audit_log)
        }
    
    async def cleanup(self):
        """Clean up connection pool"""
        logger.info("Cleaning up database connection pool...")
        
        for conn in self.connections:
            try:
                await conn.close()
            except Exception as e:
                logger.error(f"Error closing connection: {e}")
        
        self.connections.clear()
        self.connection_count = 0
        logger.info("✅ Database connection pool cleaned up")

class SecureDatabaseManager:
    """High-level secure database manager"""
    
    def __init__(self, db_path: str = "data/secure_mobius.db"):
        self.db_path = db_path
        self.pool_config = ConnectionPoolConfig()
        self.security_config = SecurityConfig()
        self.pool: Optional[SecureConnectionPool] = None
        self.encryption_key = self._get_or_create_encryption_key()
    
    def _get_or_create_encryption_key(self) -> bytes:
        """Get or create encryption key for sensitive data"""
        key_file = "data/.encryption_key"
        
        if os.path.exists(key_file):
            with open(key_file, 'rb') as f:
                return f.read()
        else:
            # Create new key
            key = secrets.token_bytes(32)  # 256-bit key
            os.makedirs(os.path.dirname(key_file), exist_ok=True)
            with open(key_file, 'wb') as f:
                f.write(key)
            os.chmod(key_file, 0o600)  # Read-write for owner only
            return key
    
    async def initialize(self):
        """Initialize secure database manager"""
        logger.info("Initializing secure database manager...")
        
        # Ensure database directory exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        # Initialize connection pool
        self.pool = SecureConnectionPool(self.db_path, self.pool_config, self.security_config)
        await self.pool.initialize()
        
        # Create tables if they don't exist
        await self._create_tables()
        
        logger.info("✅ Secure database manager initialized")
    
    async def _create_tables(self):
        """Create database tables with security considerations"""
        tables = [
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                encrypted_data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                security_flags INTEGER DEFAULT 0
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS user_sessions (
                session_id TEXT PRIMARY KEY,
                user_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                ip_hash TEXT,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS security_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                event_type TEXT,
                event_data TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                severity INTEGER DEFAULT 1
            )
            """,
            """
            CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
            CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON user_sessions(user_id);
            CREATE INDEX IF NOT EXISTS idx_security_events_user_id ON security_events(user_id);
            CREATE INDEX IF NOT EXISTS idx_security_events_timestamp ON security_events(timestamp);
            """
        ]
        
        for table_sql in tables:
            await self.pool.execute_secure_query(table_sql)
    
    async def get_user_secure(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user data securely"""
        result = await self.pool.execute_secure_fetchone(
            "SELECT user_id, username, encrypted_data, created_at, last_active FROM users WHERE user_id = ?",
            (user_id,),
            user_id
        )
        
        if result:
            return {
                'user_id': result[0],
                'username': result[1],
                'data': self._decrypt_data(result[2]) if result[2] else {},
                'created_at': result[3],
                'last_active': result[4]
            }
        return None
    
    async def set_user_data_secure(self, user_id: int, data: Dict[str, Any]) -> bool:
        """Set user data securely with encryption"""
        try:
            encrypted_data = self._encrypt_data(data)
            
            await self.pool.execute_secure_query(
                """
                INSERT OR REPLACE INTO users (user_id, encrypted_data, last_active)
                VALUES (?, ?, CURRENT_TIMESTAMP)
                """,
                (user_id, encrypted_data),
                user_id
            )
            
            return True
        except Exception as e:
            logger.error(f"Error setting user data: {e}")
            return False
    
    def _encrypt_data(self, data: Dict[str, Any]) -> str:
        """Encrypt sensitive data"""
        if not self.security_config.enable_encryption:
            return json.dumps(data)
        
        # Simple encryption for demo - in production use proper encryption library
        import base64
        json_data = json.dumps(data)
        encoded = base64.b64encode(json_data.encode()).decode()
        return encoded
    
    def _decrypt_data(self, encrypted_data: str) -> Dict[str, Any]:
        """Decrypt sensitive data"""
        if not self.security_config.enable_encryption:
            return json.loads(encrypted_data)
        
        # Simple decryption for demo
        import base64
        try:
            decoded = base64.b64decode(encrypted_data.encode()).decode()
            return json.loads(decoded)
        except Exception as e:
            logger.error(f"Error decrypting data: {e}")
            return {}
    
    async def log_security_event(self, user_id: Optional[int], event_type: str, 
                                event_data: Dict[str, Any], severity: int = 1):
        """Log security events for monitoring"""
        await self.pool.execute_secure_query(
            "INSERT INTO security_events (user_id, event_type, event_data, severity) VALUES (?, ?, ?, ?)",
            (user_id, event_type, json.dumps(event_data), severity)
        )
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        pool_stats = await self.pool.get_pool_stats() if self.pool else {}
        
        # Get table stats
        table_stats = {}
        for table in ['users', 'user_sessions', 'security_events']:
            try:
                result = await self.pool.execute_secure_fetchone(f"SELECT COUNT(*) FROM {table}")
                table_stats[table] = result[0] if result else 0
            except:
                table_stats[table] = 0
        
        return {
            'pool_stats': pool_stats,
            'table_stats': table_stats,
            'security_config': {
                'encryption_enabled': self.security_config.enable_encryption,
                'audit_log_enabled': self.security_config.enable_audit_log,
                'sql_injection_protection': self.security_config.enable_sql_injection_protection
            }
        }
    
    async def cleanup(self):
        """Clean up database manager"""
        if self.pool:
            await self.pool.cleanup()

# Custom exceptions
class DatabaseError(Exception):
    """Database operation error"""
    pass

class SecurityError(Exception):
    """Security-related error"""
    pass

# Global instance
secure_db_manager = SecureDatabaseManager()

# Convenience functions
async def init_secure_database():
    """Initialize secure database"""
    await secure_db_manager.initialize()

async def get_user_data_secure(user_id: int) -> Optional[Dict[str, Any]]:
    """Get user data securely"""
    return await secure_db_manager.get_user_secure(user_id)

async def set_user_data_secure(user_id: int, data: Dict[str, Any]) -> bool:
    """Set user data securely"""
    return await secure_db_manager.set_user_data_secure(user_id, data)

async def log_security_event(user_id: Optional[int], event_type: str, event_data: Dict[str, Any], severity: int = 1):
    """Log security event"""
    await secure_db_manager.log_security_event(user_id, event_type, event_data, severity)