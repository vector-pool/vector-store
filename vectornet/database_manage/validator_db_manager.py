import psycopg2
from psycopg2 import sql
from typing import List, Optional, Tuple
import bittensor as bt
import json
from dotenv import load_dotenv
import os

load_dotenv()
db_user_name = os.getenv("POSTGRESQL_VALIDATOR_USER_NAME")
password = os.getenv("VALI_DB_PASSWORD")
db_port = os.getenv("DB_PORT")

class ValidatorDBManager:
    def __init__(self, db_name: str):
        """Initialize ValidatorDBManager with a miner uid."""
        self.db_name = db_name
        self.conn = None
        self.ensure_database_exists()
        self.connect_to_db()
        self.create_tables()

    def ensure_database_exists(self) -> bool:
        """Ensure the database exists, create if not."""
        conn = psycopg2.connect(dbname='postgres', user=db_user_name, password=password, host='localhost', port=db_port)
        conn.autocommit = True
        try:
            with conn.cursor() as cur:
                if isinstance(self.db_name, int):
                    self.db_name = str(self.db_name)
                cur.execute(sql.SQL("SELECT 1 FROM pg_database WHERE datname = %s"), [self.db_name])
                exists = cur.fetchone()

                if not exists:
                    cur.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(self.db_name)))
                    return False
                return True
        finally:
            conn.close()

    def connect_to_db(self):
        """Connect to the specified database."""
        self.conn = psycopg2.connect(dbname=self.db_name, user=db_user_name, password=password, host='localhost', port=db_port)
        bt.logging.debug("Correctly connected to MinerDBManager")
        
    def create_tables(self):
        """Create tables if they do not exist."""
        commands = (
            """
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL UNIQUE,
                name VARCHAR(255) NOT NULL UNIQUE
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS organizations (
                id SERIAL PRIMARY KEY,
                organization_id INTEGER NOT NULL UNIQUE,
                name VARCHAR(255) NOT NULL,
                user_id INTEGER NOT NULL REFERENCES users(user_id)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS namespaces (
                id SERIAL PRIMARY KEY,
                namespace_id INTEGER NOT NULL UNIQUE,
                name VARCHAR(255) NOT NULL,
                category VARCHAR(255) NOT NULL,
                user_id INTEGER NOT NULL REFERENCES users(user_id),
                organization_id INTEGER NOT NULL REFERENCES organizations(organization_id),
                pageids_info JSONB NOT NULL  -- Changed from INTEGER[] to JSONB
                storage_size INTEGER NOT NULL,
            )
            """
        )
        with self.conn.cursor() as cur:
            for command in commands:
                cur.execute(command)
            self.conn.commit()

    def get_user(self, user_id: int) -> Tuple[Optional[int], Optional[str]]:
        """Retrieve user ID and name by user_id."""
        with self.conn.cursor() as cur:
            cur.execute("SELECT user_id, name FROM users WHERE user_id = %s", (user_id,))
            result = cur.fetchone()
            if result:
                return result[0], result[1] 
            else:
                return None, None  

    def get_organization(self, user_id: int, organization_id: int) -> Tuple[Optional[int], Optional[str]]:
        """Retrieve organization ID by organization_id and user_id."""
        with self.conn.cursor() as cur:
            cur.execute(
                "SELECT organization_id, name FROM organizations WHERE organization_id = %s AND user_id = %s",
                (organization_id, user_id)
            )
            result = cur.fetchone()
            if result:
                return result[0], result[1]  
            else:
                return None, None 

    def get_namespace(self, user_id: int, organization_id: int, namespace_id: int) -> Tuple[Optional[int], Optional[str]]:
        """Retrieve namespace ID by namespace_id, user_id, and organization_id."""
        with self.conn.cursor() as cur:
            cur.execute(
                "SELECT namespace_id, name FROM namespaces WHERE namespace_id = %s AND user_id = %s AND organization_id = %s",
                (namespace_id, user_id, organization_id)
            )
            result = cur.fetchone()
            if result:
                return result[0], result[1]  
            else:
                return None, None

    def add_user(self, user_id: int, name: str) -> int:
        """Add a new user if not exists, return user ID."""
        existing_user_id, existing_user_name = self.get_user(user_id)
        if existing_user_id is None:
            with self.conn.cursor() as cur:
                cur.execute("INSERT INTO users (user_id, name) VALUES (%s, %s) RETURNING user_id", (user_id, name))
                self.conn.commit()
        return user_id

    def add_organization(self, organization_id: int, user_id: int, name: str) -> int:
        """Add a new organization if not exists, return organization ID."""
        existing_organization_id, existing_organization_name = self.get_organization(user_id, organization_id)
        if existing_organization_id is None:
            with self.conn.cursor() as cur:
                cur.execute("INSERT INTO organizations (organization_id, user_id, name) VALUES (%s, %s, %s) RETURNING organization_id", (organization_id, user_id, name))
                self.conn.commit()
        return organization_id
    
    def add_namespace(self, namespace_id: int, user_id: int, organization_id: int, name: str, category: str, pageids_info: dict, storage_size: int) -> int:
        """Add a new namespace, return namespace ID."""
        existing_namespace_id, existing_namespace_name = self.get_namespace(user_id, organization_id, namespace_id)
        if existing_namespace_id is None:
            with self.conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO namespaces (namespace_id, user_id, organization_id, name, category, pageids_info, storage_size) VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING namespace_id",
                    (namespace_id, user_id, organization_id, name, category, json.dumps(pageids_info), storage_size)  
                )
                self.conn.commit()
                return cur.fetchone()[0]  # Return the newly created namespace ID
        return namespace_id
    
    def get_db_data(self, user_id, organization_id, namespace_id):
        db_user_id, db_user_name = self.get_user(user_id)
        db_organization_id, db_organization_name = self.get_organization(user_id, organization_id)
        db_namespace_id, db_namespace_name = self.get_namespace(user_id, organization_id, namespace_id)
        
        return db_user_id, db_user_name, db_organization_id, db_organization_name, db_namespace_id, db_namespace_name

    def get_random_unit_ids(self) -> Optional[Tuple[int, int, int, str, str, str, str, List[int]]]:
        """Retrieve one random row from the namespaces table with user and organization details, including category and pageids."""
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT 
                    n.user_id, 
                    n.organization_id, 
                    n.namespace_id, 
                    u.name AS user_name, 
                    o.name AS organization_name, 
                    n.name AS namespace_name,
                    n.category,
                    n.pageids_info
                FROM 
                    namespaces n
                JOIN 
                    users u ON n.user_id = u.user_id
                JOIN 
                    organizations o ON n.organization_id = o.organization_id
                ORDER BY RANDOM() 
                LIMIT 1;
            """)
            result = cur.fetchone()
            return result if result else None

    def check_uniquness(self, user_name: str, organization_name: str, namespace_name: str) -> int:
        """Check if a namespace with the given names is unique."""
        with self.conn.cursor() as cur:
            cur.execute("SELECT user_id FROM users WHERE name = %s", (user_name,))
            user_result = cur.fetchone()
            if user_result is None:
                return 1  
            user_id = user_result[0]

            cur.execute("SELECT organization_id FROM organizations WHERE name = %s AND user_id = %s", (organization_name, user_id))
            org_result = cur.fetchone()
            if org_result is None:
                return 1  
            organization_id = org_result[0]

            cur.execute(
                "SELECT 1 FROM namespaces WHERE name = %s AND user_id = %s AND organization_id = %s",
                (namespace_name, user_id, organization_id)
            )
            namespace_result = cur.fetchone()

            if namespace_result is None:
                return 1  
            else:
                return 0  

    def create_operation(
            self,
            request_type: str,
            user_name: str,
            organization_name: str,
            namespace_name: str,
            user_id: int,
            organization_id: int,
            namespace_id: int,
            category: str,
            pageids_info: List[dict],
            storage_size: int,
        ):
        """Handle create operations."""
        if request_type.lower() != 'create':
            raise ValueError("Invalid request type. Expected 'create'.")

        self.add_user(user_id, user_name)
        self.add_organization(organization_id, user_id, organization_name)
        self.add_namespace(namespace_id, user_id, organization_id, namespace_name, category, pageids_info, storage_size)

    def update_operation(
            self,
            request_type: str,
            perform: str,
            user_id: int,
            organization_id: int,
            namespace_id: int,
            category: str,
            pageids_info: dict,
            storage_size,
        ) -> Optional[str]:
        """Update the pageids_info for a specific namespace."""
        if request_type.lower() != 'update':
            raise ValueError("Invalid request type. Expected 'update'.")

        if perform == "ADD":
            with self.conn.cursor() as cur:
                cur.execute("SELECT pageids_info, storage_size FROM namespaces WHERE namespace_id = %s;", (namespace_id,))
                result = cur.fetchone()
                
                if result is None:
                    raise Exception(f"Namespace not found in update_operation: {namespace_id}")
                
                existing_pageids_info = result[0]  
                existing_pageids_info.update(pageids_info)

                cur.execute(
                    "UPDATE namespaces SET pageids_info = %s WHERE namespace_id = %s;",
                    (json.dumps(existing_pageids_info), namespace_id) 
                )

                self.conn.commit() 

    def update_operation(
            self,
            request_type: str,
            perform: str,
            user_id: int,
            organization_id: int,
            namespace_id: int,
            category: str,
            pageids_info: dict,
            storage_size: int,
        ) -> Optional[str]:
        """Update the pageids_info and storage_size for a specific namespace."""
        if request_type.lower() != 'update':
            raise ValueError("Invalid request type. Expected 'update'.")

        if perform == "ADD":
            with self.conn.cursor() as cur:
                cur.execute("SELECT pageids_info, storage_size FROM namespaces WHERE namespace_id = %s;", (namespace_id,))
                result = cur.fetchone()

                if result is None:
                    raise Exception(f"Namespace not found in update_operation: {namespace_id}")

                existing_pageids_info = result[0]  
                existing_storage_size = result[1]  

                existing_pageids_info.update(pageids_info)
                new_storage_size = existing_storage_size + storage_size

                cur.execute(
                    "UPDATE namespaces SET pageids_info = %s, storage_size = %s WHERE namespace_id = %s;",
                    (json.dumps(existing_pageids_info), new_storage_size, namespace_id)
                )

                self.conn.commit()  

    def delete_operation(
            self,
            request_type: str,
            user_id: int,
            organization_id: int,
            namespace_id: int,
        ):
        """Delete a namespace row based on the namespace_id."""
        
        with self.conn.cursor() as cur:
            cur.execute("SELECT * FROM namespaces WHERE namespace_id = %s;", (namespace_id,))
            result = cur.fetchone()
            
            if result is None:
                raise Exception(f"Namespace not found in delete operation: {namespace_id}")
            
            cur.execute(
                "DELETE FROM namespaces WHERE namespace_id = %s;",
                (namespace_id,)
            )
            
            self.conn.commit()  
        
    def get_total_storage_size(self) -> int:
        """Fetch the total storage size across all rows in the namespaces table."""
        
        with self.conn.cursor() as cur:
            cur.execute("SELECT SUM(storage_size) FROM namespaces;")
            result = cur.fetchone()
            
            return result[0] if result[0] is not None else 0  
            

    def close_connection(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()

class CountManager:
    def __init__(self):
        self.db_name = "count_synapses"
        self.conn = psycopg2.connect(dbname='postgres', user=db_user_name, password=password, host='localhost', port=db_port)
        # self.conn.autocommit = True
        self.init_count_synapse()
        
    def ensure_database_exists(self) -> bool:
        """Ensure the database exists, create if not."""
        conn = psycopg2.connect(dbname='postgres', user=db_user_name, password=password, host='localhost', port=db_port)
        conn.autocommit = True
        try:
            with conn.cursor() as cur:
                if isinstance(self.db_name, int):
                    self.db_name = str(self.db_name)
                cur.execute(sql.SQL("SELECT 1 FROM pg_database WHERE datname = %s"), [self.db_name])
                exists = cur.fetchone()

                if not exists:
                    cur.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(self.db_name)))
                    return False
                return True
        finally:
            conn.close()
            
    def connect_to_db(self):
        """Connect to the specified database."""
        self.conn = psycopg2.connect(dbname=self.db_name, user=db_user_name, password=password, host='localhost', port=db_port)
        bt.logging.debug("Correctly connected to CounterManager.")
        
    def init_count_synapse(self):
        self.ensure_database_exists()
        self.connect_to_db()

        with self.conn.cursor() as cur:
            cur.execute('''
                CREATE TABLE IF NOT EXISTS count_synapse (
                    miner_uid SERIAL PRIMARY KEY,
                    count INTEGER DEFAULT 0
                )
            ''')

            cur.execute('SELECT COUNT(*) FROM count_synapse')
            row_count = cur.fetchone()[0]

            if row_count == 0:
                for uid in range(256):
                    cur.execute('''
                        INSERT INTO count_synapse (miner_uid, count) VALUES (%s, %s)
                        ON CONFLICT (miner_uid) DO NOTHING
                    ''', (uid, 0))

            self.conn.commit()
        bt.logging.info("Created Counter database and table correctly")

    def add_count(self, uid):
        with self.conn.cursor() as cur:
            cur.execute('''
                UPDATE count_synapse SET count = count + 1 WHERE miner_uid = %s
            ''', (uid,))
            self.conn.commit()

    def read_count(self, uid):
        with self.conn.cursor() as cur:
            cur.execute('''
                SELECT count FROM count_synapse WHERE miner_uid = %s
            ''', (uid,))
            result = cur.fetchone()
            return result[0] if result else None

    def close(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()


    
