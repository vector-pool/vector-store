import psycopg2
from psycopg2 import sql
from typing import List, Optional, Tuple

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
        conn = psycopg2.connect(dbname='postgres', user='vali', password='lucky', host='localhost', port=5432)
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
        self.conn = psycopg2.connect(dbname=self.db_name, user='vali', password='lucky', host='localhost', port=5432)
        print("correctly connected")

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
                pageids INTEGER[] NOT NULL
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

    def add_namespace(self, namespace_id: int, user_id: int, organization_id: int, name: str, category: str, pageids: List[int]) -> int:
        """Add a new namespace, return namespace ID."""
        existing_namespace_id, existing_namespace_name = self.get_namespace(user_id, organization_id, namespace_id)
        if existing_namespace_id is None:
            with self.conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO namespaces (namespace_id, user_id, organization_id, name, category, pageids) VALUES (%s, %s, %s, %s, %s, %s) RETURNING namespace_id",
                    (namespace_id, user_id, organization_id, name, category, pageids)
                )
                self.conn.commit()
        return namespace_id
    
    def get_db_data(self, user_id, organization_id, namespace_id):
        db_user_id, db_user_name = self.get_user(user_id)
        db_organization_id, db_organization_name = self.get_organization(organization_id)
        db_namespace_id, db_namespace_name = self.get_namespace(namespace_id)
        
        return db_user_id, db_user_name, db_organization_id, db_organization_name, db_namespace_id, db_namespace_name

    def get_random_unit_ids(self) -> Optional[Tuple[int, int, int, str, List[int]]]:
        """Retrieve one random row from the namespace table."""
        with self.conn.cursor() as cur:
            cur.execute("SELECT user_id, organization_id, namespace_id, category, pageids FROM namespaces ORDER BY RANDOM() LIMIT 1;")
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
            pageids: List[int]
        ):
        """Handle create operations."""
        if request_type.lower() != 'create':
            raise ValueError("Invalid request type. Expected 'create'.")

        # self.ensure_database_exists()
        # self.connect_to_db()
        # self.create_tables()

        self.add_user(user_id, user_name)
        self.add_organization(organization_id, user_id, organization_name)
        self.add_namespace(namespace_id, user_id, organization_id, namespace_name, category, pageids)

    def update_operation(
            self,
            request_type: str,
            perform: str,
            user_id: int,
            organization_id: int,
            namespace_id: int,
            category: str,
            pageids: List[int],
        ) -> Optional[str]:
        """Update the pageids list for a specific namespace."""
        if request_type.lower() != 'update':
            raise ValueError("Invalid request type. Expected 'update'.")
        if perform == "ADD":
            with self.conn.cursor() as cur:
                # Step 1: Fetch the existing pageids
                cur.execute("SELECT pageids FROM namespaces WHERE namespace_id = %s;", (namespace_id,))
                result = cur.fetchone()
                
                if result is None:
                    raise Exception(f"Namespace not found in update_operation, {namespace_id}")
                existing_pageids = result[0]  # Get the current pageids list
                
                # Step 2: Combine existing pageids with the new ones
                updated_pageids = list(set(existing_pageids + pageids))  # Remove duplicates if necessary
                
                # Step 3: Update the row in the database
                cur.execute(
                    "UPDATE namespaces SET pageids = %s WHERE namespace_id = %s;",
                    (updated_pageids, namespace_id)
                )

                self.conn.commit()  # Commit the changes
        
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
            
    def init_count_synapse_db(self):
        self.ensure_database_exists()
        # Create the count_synapse database and table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS count_synapse (
                miner_uid INTEGER PRIMARY KEY,
                count INTEGER DEFAULT 0
            )
        ''')
        # Fill the table with miner_uid from 0 to 255 and count as 0
        for uid in range(256):
            self.cursor.execute('''
                INSERT OR IGNORE INTO count_synapse (miner_uid, count) VALUES (?, ?)
            ''', (uid, 0))
        self.connection.commit()

    def add_count(self, uid):
        # Increment the count for the specified miner_uid
        self.cursor.execute('''
            UPDATE count_synapse SET count = count + 1 WHERE miner_uid = ?
        ''', (uid,))
        self.connection.commit()

    def read_count(self, uid):
        # Read the count for the specified miner_uid
        self.cursor.execute('''
            SELECT count FROM count_synapse WHERE miner_uid = ?
        ''', (uid,))
        result = self.cursor.fetchone()
        return result[0] if result else None



    def close_connection(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()



# Example Usage
if __name__ == '__main__':
    miner_uid = 17
    db_manager = ValidatorDBManager(miner_uid)

    db_manager.create_operation(
        request_type='create',
        user_name='abc5',
        organization_name='ggp',
        namespace_name='name28',
        user_id=13,
        organization_id=125,
        namespace_id=139,
        category='asdf',
        pageids=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    )

    db_manager.close_connection()

import psycopg2

class CountManager:
    def __init__(self):
        self.db_name = "count_synapses"
        self.connection = psycopg2.connect()
        self.cursor = self.connection.cursor()
        self.init_count_synapse()

    def init_count_synapse(self):
        # Create the count_synapse table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS count_synapse (
                miner_uid SERIAL PRIMARY KEY,
                count INTEGER DEFAULT 0
            )
        ''')
        # Fill the table with miner_uid from 0 to 255 and count as 0
        for uid in range(256):
            self.cursor.execute('''
                INSERT INTO count_synapse (miner_uid, count) VALUES (%s, %s)
                ON CONFLICT (miner_uid) DO NOTHING
            ''', (uid, 0))
        self.connection.commit()

    def add_count(self, uid):
        # Increment the count for the specified miner_uid
        self.cursor.execute('''
            UPDATE count_synapse SET count = count + 1 WHERE miner_uid = %s
        ''', (uid,))
        self.connection.commit()

    def read_count(self, uid):
        # Read the count for the specified miner_uid
        self.cursor.execute('''
            SELECT count FROM count_synapse WHERE miner_uid = %s
        ''', (uid,))
        result = self.cursor.fetchone()
        return result[0] if result else None

    def close(self):
        self.cursor.close()
        self.connection.close()
