import psycopg2
from psycopg2 import sql
from typing import List, Tuple, Optional

class ValidatorDBManager:
    def __init__(self, miner_uid: str):
        """Initialize MinerDBManager with a validator hotkey."""
        self.db_name = miner_uid
        self.conn = None

    def ensure_database_exists(self) -> bool:
        """Ensure the database exists, create if not."""
        # Create the connection
        conn = psycopg2.connect(dbname='postgres', user='validatgor', password='lucky', host='localhost', port=5432)
        # Set autocommit before creating the cursor
        conn.autocommit = True
        try:
            with conn.cursor() as cur:
                # Check if the database exists
                cur.execute(sql.SQL("SELECT 1 FROM pg_database WHERE datname = %s"), [self.db_name])
                exists = cur.fetchone()
                
                # If it doesn't exist, create it
                if not exists:
                    cur.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(self.db_name)))
                    return False
                return True
        finally:
            conn.close()  # Ensure the connection is closed properly

    def connect_to_db(self):
        """Connect to the specified database."""
        self.conn = psycopg2.connect(dbname=self.db_name, user='validator', password='lucky', host='localhost', port=5432)

    def create_tables(self):
        """Create tables if they do not exist."""
        commands = (
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL UNIQUE
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS organizations (
                organization_id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                user_id INTEGER REFERENCES users(user_id),
                UNIQUE(name, user_id)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS namespaces (
                namespace_id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                user_id INTEGER REFERENCES users(user_id),
                organization_id INTEGER REFERENCES organizations(organization_id),
                UNIQUE(name, organization_id)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS vectors (
                vector_id SERIAL PRIMARY KEY,
                pageid INTEGER NOT NULL,
                user_id INTEGER REFERENCES users(user_id),
                organization_id INTEGER REFERENCES organizations(organization_id),
                namespace_id INTEGER REFERENCES namespaces(namespace_id)
            )
            """,
        )
        with self.conn.cursor() as cur:
            for command in commands:
                cur.execute(command)
            self.conn.commit()

    def get_user_id(self, name: str) -> Optional[int]:
        """Retrieve user ID by name."""
        with self.conn.cursor() as cur:
            cur.execute("SELECT user_id FROM users WHERE name = %s", (name,))
            result = cur.fetchone()
            return result[0] if result else None

    def get_organization_id(self, user_id: int, name: str) -> Optional[int]:
        """Retrieve organization ID by user ID and name."""
        with self.conn.cursor() as cur:
            cur.execute("SELECT organization_id FROM organizations WHERE name = %s AND user_id = %s", (name, user_id))
            result = cur.fetchone()
            return result[0] if result else None

    def get_namespace_id(self, user_id: int, organization_id: int, name: str) -> Optional[int]:
        """Retrieve namespace ID by user ID, organization ID, and name."""
        with self.conn.cursor() as cur:
            cur.execute("SELECT namespace_id FROM namespaces WHERE name = %s AND user_id = %s AND organization_id = %s", (name, user_id, organization_id))
            result = cur.fetchone()
            return result[0] if result else None

    def add_user(self, name: str) -> int:
        """Add a new user if not exists, return user ID."""
        user_id = self.get_user_id(name)
        if user_id is None:
            with self.conn.cursor() as cur:
                cur.execute("INSERT INTO users (name) VALUES (%s) RETURNING user_id", (name,))
                user_id = cur.fetchone()[0]
                self.conn.commit()
        return user_id

    def add_organization(self, user_id: int, name: str) -> int:
        """Add a new organization if not exists, return organization ID."""
        organization_id = self.get_organization_id(user_id, name)
        if organization_id is None:
            with self.conn.cursor() as cur:
                cur.execute("INSERT INTO organizations (name, user_id) VALUES (%s, %s) RETURNING organization_id", (name, user_id))
                organization_id = cur.fetchone()[0]
                self.conn.commit()
        return organization_id

    def add_namespace(self, user_id: int, organization_id: int, name: str) -> int:
        """Add a new namespace, return namespace ID."""
        with self.conn.cursor() as cur:
            cur.execute("INSERT INTO namespaces (name, user_id, organization_id) VALUES (%s, %s, %s) RETURNING namespace_id", (name, user_id, organization_id))
            namespace_id = cur.fetchone()[0]
            self.conn.commit()
        return namespace_id

    def add_vectors(self, user_id: int, organization_id: int, namespace_id: int, vectors: List[int]):
        """Add vectors to the database."""
        with self.conn.cursor() as cur:
            for vector in vectors:
                # print(vector['original_text'], vector['text'], vector['embedding'], user_id, organization_id, namespace_id)
                cur.execute(
                    "INSERT INTO vectors (user_id, organization_id, namespace_id, pageid) VALUES (%s, %s, %s, %s)",
                    (user_id, organization_id, namespace_id, vector['pageid'])
                )
            self.conn.commit()
        print("success creating")

    def create_operation(self, request_type: str, user_name: str, organization_name: str, namespace_name: str, pageids: List[int]):
        """Handle create operations."""
        if request_type.lower() != 'create':
            raise ValueError("Invalid request type. Expected 'create'.")

        self.ensure_database_exists()
        self.connect_to_db()
        self.create_tables()

        user_id = self.add_user(user_name)
        organization_id = self.add_organization(user_id, organization_name)
        namespace_id = self.add_namespace(user_id, organization_id, namespace_name)

        vectors = [{'pageid' : pageid} for pageid in pageids        ]
        print(vectors)
        self.add_vectors(user_id, organization_id, namespace_id, vectors)
        return user_id, organization_id, namespace_id

    def read_operation(self, request_type: str, user_name: str, organization_name: str, namespace_name: str) -> List[Tuple]:
        """Handle read operations."""
        if request_type.lower() != 'read':
            raise ValueError("Invalid request type. Expected 'read'.")

        if not self.ensure_database_exists():
            raise Exception(f"Validator '{self.db_name}' has no saved data.")

        self.connect_to_db()

        user_id = self.get_user_id(user_name)
        if user_id is None:
            raise Exception(f"User '{user_name}' does not exist.")

        organization_id = self.get_organization_id(user_id, organization_name)
        if organization_id is None:
            raise Exception(f"Organization '{organization_name}' does not exist for user '{user_name}'.")

        namespace_id = self.get_namespace_id(user_id, organization_id, namespace_name)
        if namespace_id is None:
            raise Exception(f"Namespace '{namespace_name}' does not exist for user '{user_name}' and organization '{organization_name}'.")

        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT pageid
                FROM vectors
                WHERE namespace_id = %s
            """, (namespace_id,))
            
            rows = cur.fetchall()
            
            vectors = [
                {'pageid': row[0]}
                for row in rows
            ]
        return vectors


    def update_operation(self, request_type: str, perform: str, user_name: str, organization_name: str, namespace_name: str, pageids: List[int]):
        """Handle update operations."""
        if request_type.lower() != 'update':
            raise ValueError("Invalid request type. Must be 'update'.")

        if not self.ensure_database_exists():
            raise Exception(f"Validator '{self.db_name}' has no saved data.")

        self.connect_to_db()

        user_id = self.get_user_id(user_name)
        if user_id is None:
            raise Exception(f"User '{user_name}' does not exist.")

        organization_id = self.get_organization_id(user_id, organization_name)
        if organization_id is None:
            raise Exception(f"Organization '{organization_name}' does not exist for user '{user_name}'.")

        namespace_id = self.get_namespace_id(user_id, organization_id, namespace_name)
        if namespace_id is None:
            raise Exception(f"Namespace '{namespace_name}' does not exist for user '{user_name}' and organization '{organization_name}'.")

        with self.conn.cursor() as cur:
            if perform == 'replace':
                cur.execute("DELETE FROM vectors WHERE namespace_id = %s", (namespace_id,))
                self.conn.commit()

            for pageid in pageids:
                cur.execute(
                    "INSERT INTO vectors (user_id, organization_id, namespace_id, pageid) VALUES (%s, %s, %s, %s)",
                    (user_id, organization_id, namespace_id, pageid)
                )
            self.conn.commit()

    def delete_operation(self, request_type: str, perform: str, user_name: Optional[str] = None, organization_name: Optional[str] = None, namespace_name: Optional[str] = None):
        """Handle delete operations."""
        if request_type.lower() != 'delete':
            raise ValueError("Invalid request type. Must be 'delete'.")

        if perform not in {'user', 'organization', 'namespace'}:
            raise ValueError("Invalid perform action. Must be 'user', 'organization', or 'namespace'.")

        if not self.ensure_database_exists():
            raise Exception(f"Validator '{self.db_name}' has no saved data.")

        self.connect_to_db()

        with self.conn.cursor() as cur:
            if perform == 'user':
                if not user_name:
                    raise ValueError("User name is required for user deletion.")
                user_id = self.get_user_id(user_name)
                if user_id is None:
                    raise Exception(f"User '{user_name}' does not exist.")
                cur.execute("DELETE FROM vectors WHERE user_id = %s", (user_id,))
                cur.execute("DELETE FROM namespaces WHERE user_id = %s", (user_id,))
                cur.execute("DELETE FROM organizations WHERE user_id = %s", (user_id,))
                cur.execute("DELETE FROM users WHERE user_id = %s", (user_id,))

            elif perform == 'organization':
                if not user_name or not organization_name:
                    raise ValueError("User and organization names are required for organization deletion.")
                user_id = self.get_user_id(user_name)
                organization_id = self.get_organization_id(user_id, organization_name)
                if organization_id is None:
                    raise Exception(f"Organization '{organization_name}' does not exist for user '{user_name}'.")
                cur.execute("DELETE FROM vectors WHERE organization_id = %s", (organization_id,))
                cur.execute("DELETE FROM namespaces WHERE organization_id = %s", (organization_id,))
                cur.execute("DELETE FROM organizations WHERE organization_id = %s", (organization_id,))

            elif perform == 'namespace':
                if not user_name or not organization_name or not namespace_name:
                    raise ValueError("User, organization, and namespace names are required for namespace deletion.")
                user_id = self.get_user_id(user_name)
                organization_id = self.get_organization_id(user_id, organization_name)
                namespace_id = self.get_namespace_id(user_id, organization_id, namespace_name)
                if namespace_id is None:
                    raise Exception(f"Namespace '{namespace_name}' does not exist for user '{user_name}' and organization '{organization_name}'.")
                cur.execute("DELETE FROM vectors WHERE namespace_id = %s", (namespace_id,))
                cur.execute("DELETE FROM namespaces WHERE namespace_id = %s", (namespace_id,))

            self.conn.commit()

    def close_connection(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()

# Example Usage
if __name__ == '__main__':
    miner_uid = 12
    db_manager = ValidatorDBManager(miner_uid)

    db_manager.create_operation(
        request_type='create',
        user_name='abc3',
        organization_name='pleb',
        namespace_name='name24',
        pageids=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    )

    pageids = db_manager.read_operation(
        request_type='read',
        user_name='abc3',
        organization_name='pleb',
        namespace_name='name24',
    )
    print(pageids)

    db_manager.update_operation(
        request_type='update',
        perform='add',  # this can be 'add'
        user_name='abc3',
        organization_name='pleb',
        namespace_name='name24',
        pageids=[11, 12, 13, 14, 15, 16, 17, 18, 19]
    )

    pageids = db_manager.read_operation(
        request_type='read',
        user_name='abc3',
        organization_name='pleb',
        namespace_name='name24',
    )
    print(pageids)
    
    db_manager.delete_operation(
        request_type='delete',
        perform='user',  # this can be 'organization' or 'namespace'
        user_name='abc3',
        organization_name='pleb',
        namespace_name='name22',
    )

    db_manager.close_connection()
