#!/usr/bin/env python3
# fix_database_schema.py - Fix database schema issues
"""
Fix database schema issues and ensure all tables have required columns
"""

import sqlite3
import os
import logging
from typing import List, Dict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_database_schema():
    """Fix database schema issues"""
    db_path = "data/user_data.sqlite"
    
    # Ensure data directory exists
    os.makedirs("data", exist_ok=True)
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        logger.info("🔧 Fixing database schema...")
        
        # Check if tables exist and add missing columns
        tables_to_check = [
            {
                "name": "onchain_alerts",
                "columns": [
                    ("alert_id", "TEXT PRIMARY KEY"),
                    ("user_id", "INTEGER NOT NULL"),
                    ("chat_id", "INTEGER NOT NULL"),
                    ("alert_type", "TEXT NOT NULL"),
                    ("params", "TEXT NOT NULL"),
                    ("active", "BOOLEAN DEFAULT TRUE"),
                    ("triggered_count", "INTEGER DEFAULT 0"),
                    ("last_triggered", "INTEGER"),
                    ("created_at", "INTEGER NOT NULL"),
                    ("updated_at", "INTEGER DEFAULT (strftime('%s', 'now'))")
                ]
            },
            {
                "name": "user_sessions",
                "columns": [
                    ("session_id", "TEXT PRIMARY KEY"),
                    ("user_id", "INTEGER NOT NULL"),
                    ("ip_hash", "TEXT"),
                    ("user_agent_hash", "TEXT"),
                    ("created_at", "INTEGER NOT NULL"),
                    ("last_activity", "INTEGER NOT NULL"),
                    ("expires_at", "INTEGER NOT NULL"),
                    ("active", "BOOLEAN DEFAULT TRUE")
                ]
            }
        ]
        
        for table_info in tables_to_check:
            table_name = table_info["name"]
            required_columns = table_info["columns"]
            
            # Check if table exists
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name=?
            """, (table_name,))
            
            if not cursor.fetchone():
                # Create table if it doesn't exist
                columns_def = ", ".join([f"{col[0]} {col[1]}" for col in required_columns])
                create_sql = f"CREATE TABLE {table_name} ({columns_def})"
                cursor.execute(create_sql)
                logger.info(f"✅ Created table: {table_name}")
            else:
                # Check existing columns
                cursor.execute(f"PRAGMA table_info({table_name})")
                existing_columns = {row[1] for row in cursor.fetchall()}
                
                # Add missing columns
                for col_name, col_def in required_columns:
                    if col_name not in existing_columns:
                        try:
                            # Extract just the type and constraints (not PRIMARY KEY)
                            if "PRIMARY KEY" not in col_def:
                                alter_sql = f"ALTER TABLE {table_name} ADD COLUMN {col_name} {col_def}"
                                cursor.execute(alter_sql)
                                logger.info(f"✅ Added column {col_name} to {table_name}")
                        except sqlite3.Error as e:
                            logger.warning(f"⚠️ Could not add column {col_name} to {table_name}: {e}")
        
        # Create indexes if they don't exist
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_onchain_alerts_active ON onchain_alerts(active)",
            "CREATE INDEX IF NOT EXISTS idx_onchain_alerts_user_id ON onchain_alerts(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_user_sessions_active ON user_sessions(active)",
            "CREATE INDEX IF NOT EXISTS idx_user_sessions_user_id ON user_sessions(user_id)"
        ]
        
        for index_sql in indexes:
            try:
                cursor.execute(index_sql)
                logger.info(f"✅ Created index")
            except sqlite3.Error as e:
                logger.warning(f"⚠️ Could not create index: {e}")
        
        conn.commit()
        conn.close()
        
        logger.info("✅ Database schema fixed successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to fix database schema: {e}")
        return False

def fix_cross_chain_analytics():
    """Fix cross-chain analytics module"""
    try:
        # Check if CrossChainAnalyzer exists in cross_chain_analytics
        import sys
        sys.path.insert(0, 'src')
        
        from cross_chain_analytics import CrossChainAnalytics
        
        # Add missing CrossChainAnalyzer class if needed
        cross_chain_file = "src/cross_chain_analytics.py"
        
        with open(cross_chain_file, 'r') as f:
            content = f.read()
        
        if "class CrossChainAnalyzer" not in content:
            # Add the missing class
            analyzer_class = '''

class CrossChainAnalyzer:
    """Cross-chain analyzer for compatibility"""
    
    def __init__(self):
        self.analytics = CrossChainAnalytics()
    
    def analyze_cross_chain_activity(self, *args, **kwargs):
        """Analyze cross-chain activity"""
        return self.analytics.get_cross_chain_summary()
    
    def get_bridge_data(self, *args, **kwargs):
        """Get bridge data"""
        return self.analytics.get_bridge_volume()
'''
            
            with open(cross_chain_file, 'a') as f:
                f.write(analyzer_class)
            
            logger.info("✅ Added CrossChainAnalyzer class")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to fix cross-chain analytics: {e}")
        return False

def main():
    """Main function to fix all issues"""
    logger.info("🚀 Starting comprehensive bug fixes...")
    
    fixes_applied = 0
    total_fixes = 2
    
    # Fix 1: Database schema
    if fix_database_schema():
        fixes_applied += 1
        logger.info("✅ Database schema fixed")
    else:
        logger.error("❌ Database schema fix failed")
    
    # Fix 2: Cross-chain analytics
    if fix_cross_chain_analytics():
        fixes_applied += 1
        logger.info("✅ Cross-chain analytics fixed")
    else:
        logger.error("❌ Cross-chain analytics fix failed")
    
    success_rate = (fixes_applied / total_fixes) * 100
    
    logger.info(f"\n🎯 Bug Fix Summary:")
    logger.info(f"Fixes Applied: {fixes_applied}/{total_fixes}")
    logger.info(f"Success Rate: {success_rate:.1f}%")
    
    if success_rate >= 100:
        logger.info("🏆 All fixes applied successfully!")
    elif success_rate >= 80:
        logger.info("✅ Most fixes applied successfully")
    else:
        logger.warning("⚠️ Some fixes failed - manual intervention may be needed")
    
    return success_rate >= 80

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)