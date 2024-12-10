import psycopg2
from psycopg2 import sql
from typing import List, Tuple, Optional
import bittensor as bt
from dotenv import load_dotenv
import os

load_dotenv()
db_user_name = os.getenv("POSTGRESQL_MINER_USER_NAME")
password = os.getenv("MINER_DB_PASSWORD")
db_port = os.getenv("DB_PORT")


class MinerDBManager:
    def __init__(self, validator_hotkey: str):
        """Initialize MinerDBManager with a validator hotkey."""
        self.db_name = validator_hotkey
        self.conn = None

    def ensure_database_exists(self) -> bool:
        """Ensure the database exists, create if not."""
        # Create the connection
        conn = psycopg2.connect(dbname='postgres', user=db_user_name, password=password, host='localhost', port=db_port)
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
        self.conn = psycopg2.connect(dbname=self.db_name, user=db_user_name, password=password, host='localhost', port=db_port)
        self.conn.autocommit = True  # Ensure autocommit is enabled

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
                original_text TEXT NOT NULL,
                text TEXT NOT NULL,
                embedding FLOAT[] NOT NULL,
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

    # def add_user(self, name: str) -> int:
    #     """Add a new user if not exists, return user ID."""
    #     user_id = self.get_user_id(name)
    #     if user_id is None:
    #         with self.conn.cursor() as cur:
    #             cur.execute("INSERT INTO users (name) VALUES (%s) RETURNING user_id", (name,))
    #             user_id = cur.fetchone()[0]
    #             self.conn.commit()
    #     return user_id
    def add_user(self, name: str) -> int:
        """Add a new user if not exists, return user ID."""
        user_id = self.get_user_id(name)
        if user_id is None:
            try:
                with self.conn.cursor() as cur:
                    cur.execute("INSERT INTO users (name) VALUES (%s) RETURNING user_id", (name,))
                    user_id = cur.fetchone()[0]
                    self.conn.commit()
            except Exception as e:
                bt.logging.error(f"Error adding user: {e}")
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

    def add_vectors(self, user_id: int, organization_id: int, namespace_id: int, vectors: List[dict]) -> List[int]:
        """Add vectors to the database and return the list of newly added vector IDs."""
        vector_ids = []  # List to store the IDs of newly added vectors
        with self.conn.cursor() as cur:
            for vector in vectors:
                bt.logging.debug(vector['original_text'], vector['text'], vector['embedding'], user_id, organization_id, namespace_id)
                cur.execute(
                    "INSERT INTO vectors (text, embedding, user_id, organization_id, namespace_id, original_text) VALUES (%s, %s, %s, %s, %s, %s) RETURNING vector_id",
                    (vector['text'], vector['embedding'], user_id, organization_id, namespace_id, vector['original_text'])
                )
                vector_id = cur.fetchone()[0]  # Fetch the newly created vector_id
                vector_ids.append(vector_id)  # Add it to the list
            self.conn.commit()
        bt.logging.debug("success creating vectors")
        return vector_ids  # Return the list of vector IDs


    def create_operation(self, request_type: str, user_name: str, organization_name: str, namespace_name: str, texts: List[str], embeddings: List[List[float]], original_texts: List[str]):
        """Handle create operations."""
        if request_type.lower() != 'create':
            raise ValueError("Invalid request type. Expected 'create'.")

        self.ensure_database_exists()
        self.connect_to_db()
        self.create_tables()

        user_id = self.add_user(user_name)
        organization_id = self.add_organization(user_id, organization_name)
        namespace_id = self.add_namespace(user_id, organization_id, namespace_name)

        vectors = [
            {'original_text': original_text, 'text': text, 'embedding': embedding}
            for original_text, text, embedding in zip(original_texts, texts, embeddings)
        ]
        vector_ids = self.add_vectors(user_id, organization_id, namespace_id, vectors)
        bt.logging.debug("Success Create Operation.")
        return user_id, organization_id, namespace_id, vector_ids

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
                SELECT original_text, text, embedding, vector_id
                FROM vectors
                WHERE namespace_id = %s
            """, (namespace_id,))
            
            rows = cur.fetchall()
            
            vectors = [
                {'original_text': row[0], 'text': row[1], 'embedding': row[2], 'vector_id': row[3]}
                for row in rows
            ]
            bt.logging.debug("Success Read Operation.")
            return user_id, organization_id, namespace_id, vectors


    def update_operation(self, request_type: str, perform: str, user_name: str, organization_name: str, namespace_name: str, texts: List[str], embeddings: List[List[float]], original_texts):
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

        vectors = [
            {'original_text': original_text, 'text': text, 'embedding': embedding}
            for original_text, text, embedding in zip(original_texts, texts, embeddings)
        ]
        
        if perform == 'replace':
            # cur.execute("DELETE FROM vectors WHERE namespace_id = %s", (namespace_id,))
            # self.conn.commit()
            pass
        
        vector_ids = self.add_vectors(user_id, organization_id, namespace_id, vectors)
        bt.logging.debug("Success Update Operation.")
        
        return user_id, organization_id, namespace_id, vector_ids

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
            
        bt.logging.debug("Success Delete Operation")
        return user_id, organization_id, namespace_id

    def close_connection(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()
