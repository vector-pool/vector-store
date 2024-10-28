import psycopg2
from psycopg2 import sql

class DBManager:
    def __init__(self, validator_hotkey):
        self.db_name = f"{validator_hotkey}"

    def ensure_database_exists(self):
        # Connect to the default 'postgres' database to check for or create the target database
        conn = psycopg2.connect(dbname='postgres', user='nesta', password='lucky', host='localhost', port=5432)
        conn.autocommit = True
        cur = conn.cursor()

        # Check if the database exists
        cur.execute(sql.SQL("SELECT 1 FROM pg_database WHERE datname = %s"), [self.db_name])
        exists = cur.fetchone()

        # Create the database if it does not exist
        if exists:
            result = 1
        else:
            cur.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(self.db_name)))
            result = 0

        cur.close()
        conn.close()
        return result


    def connect_to_db(self):
        # Connect to the newly created or existing database
        return psycopg2.connect(dbname=self.db_name, user='nesta', password='lucky', host='localhost', port=5432)

    def create_tables(self):
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
                original_text_id INTEGER NOT NULL,
                original_text TEXT NOT NULL,
                embedding FLOAT[] NOT NULL,
                user_id INTEGER REFERENCES users(user_id),
                organization_id INTEGER REFERENCES organizations(organization_id),
                namespace_id INTEGER REFERENCES namespaces(namespace_id)
            )
            """
        )
        cur = self.conn.cursor()
        for command in commands:
            cur.execute(command)
        self.conn.commit()
        cur.close()

    def get_user_id(self, name):
        cur = self.conn.cursor()
        cur.execute("SELECT user_id FROM users WHERE name = %s", (name,))
        result = cur.fetchone()
        cur.close()
        return result[0] if result else None

    def get_organization_id(self, user_id, name):
        cur = self.conn.cursor()
        cur.execute("SELECT organization_id FROM organizations WHERE name = %s AND user_id = %s", (name, user_id))
        result = cur.fetchone()
        cur.close()
        return result[0] if result else None

    def add_user(self, name):
        user_id = self.get_user_id(name)
        if user_id is None:
            print('user id none')
            cur = self.conn.cursor()
            cur.execute("INSERT INTO users (name) VALUES (%s) RETURNING user_id", (name,))
            user_id = cur.fetchone()[0]
            self.conn.commit()
            cur.close()
        return user_id

    def add_organization(self, user_id, name):
        organization_id = self.get_organization_id(user_id, name)
        if organization_id is None:
            cur = self.conn.cursor()
            cur.execute("INSERT INTO organizations (name, user_id) VALUES (%s, %s) RETURNING organization_id", (name, user_id))
            organization_id = cur.fetchone()[0]
            self.conn.commit()
            cur.close()
        return organization_id

    def add_namespace(self, user_id, organization_id, name):
        cur = self.conn.cursor()
        cur.execute("INSERT INTO namespaces (name, user_id, organization_id) VALUES (%s, %s, %s) RETURNING namespace_id", (name, user_id, organization_id))
        namespace_id = cur.fetchone()[0]
        self.conn.commit()
        cur.close()
        return namespace_id

    def add_vectors(self, user_id, organization_id, namespace_id, vectors):
        cur = self.conn.cursor()
        for vector in vectors:
            cur.execute(
                "INSERT INTO vectors (original_text_id, original_text, embedding, user_id, organization_id, namespace_id) VALUES (%s, %s, %s, %s, %s, %s)",
                (vector['original_text_id'], vector['original_text'], vector['embedding'], user_id, organization_id, namespace_id)
            )
        self.conn.commit()
        cur.close()

    def create_operation(self, request_type, validator_hotkey, user_name, organization_name, namespace_name, texts, embeddings):
        if request_type.lower() == 'create':

            self.ensure_database_exists()
            self.conn = self.connect_to_db()
            self.create_tables()

            # Add user if not exists
            user_id = self.add_user(user_name)

            # Add organization if not exists
            organization_id = self.add_organization(user_id, organization_name)

            # Add namespace
            namespace_id = self.add_namespace(user_id, organization_id, namespace_name)

            # Add vectors
            vectors = [
                {'original_text_id': idx + 1, 'original_text': text, 'embedding': embedding}
                for idx, (text, embedding) in enumerate(zip(texts, embeddings))
            ]
            self.add_vectors(user_id, organization_id, namespace_id, vectors)
            
    def read_operation(self, request_type, validator_hotkey, user_name, organization_name, namespace_name):
        if request_type.lower() != 'read':
            raise ValueError("Invalid request type. Expected 'read'.")

        check_validator_exist = self.ensure_database_exists()
        if check_validator_exist == 0:
            raise Exception(f"Validator '{self.db_name}' never saved data")
        self.conn = self.connect_to_db()
        
        
        # Check if the user exists
        user_id = self.get_user_id(user_name)
        if user_id is None:
            raise Exception(f"User '{user_name}' does not exist.")

        # Check if the organization exists
        organization_id = self.get_organization_id(user_id, organization_name)
        if organization_id is None:
            raise Exception(f"Organization '{organization_name}' does not exist for user '{user_name}'.")

        # Check if the namespace exists
        cur = self.conn.cursor()
        cur.execute("SELECT namespace_id FROM namespaces WHERE name = %s AND user_id = %s AND organization_id = %s",
                    (namespace_name, user_id, organization_id))
        namespace_result = cur.fetchone()
        if namespace_result is None:
            raise Exception(f"Namespace '{namespace_name}' does not exist for user '{user_name}' and organization '{organization_name}'.")
        namespace_id = namespace_result[0]

        # Retrieve all vectors for the specified namespace
        cur.execute("""
            SELECT vector_id, original_text_id, original_text, embedding, user_id, organization_id, namespace_id
            FROM vectors
            WHERE namespace_id = %s
        """, (namespace_id,))
        vectors = cur.fetchall()
        cur.close()

        return vectors

    def close_connection(self):
        self.conn.close()

# Example Usage
if __name__ == '__main__':
    validator_hotkey = '5F4tQyWrhfGVcNhoqeiNsR6KjD4wMZ2kfhLj4oHYuyHbZAc4'

    db_manager = DBManager(validator_hotkey)

    # Create request
    db_manager.create_operation(
        request_type='create',
        validator_hotkey=validator_hotkey,
        user_name='abc2',
        organization_name='const',
        namespace_name='gang sign',
        texts=[
            "hi, i like your",
            "beautiful eyes",
            "great, awesome, what is your experience",
            "hey, how are you"
        ],
        embeddings=[
            [1, 0.3, 0.7],
            [1, 0.9, 0.8],
            [1, 1, 0],
            [1, 0.8, 0.1]
        ]
    )
    
    vectors = db_manager.read_operation(
        request_type = 'read',
        validator_hotkey=validator_hotkey,
        user_name='abc2',
        organization_name='const',
        namespace_name='gang sign',
    )
    print(vectors)

    # Close the database connection
    db_manager.close_connection()
