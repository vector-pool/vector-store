# import psycopg2
# import json

# class DatabaseManager:
#     def __init__(self, dbname, user, password, host='localhost', port='5432'):
#         self.connection = psycopg2.connect(
#             dbname=dbname,
#             user=user,
#             password=password,
#             host=host,
#             port=port
#         )
#         self.cursor = self.connection.cursor()
#         self._create_tables()

#     def _create_tables(self):
#         """Create tables for organizations, namespaces, and vectors."""
#         self.cursor.execute('''
#         CREATE TABLE IF NOT EXISTS Organizations (
#             id SERIAL PRIMARY KEY,
#             name TEXT NOT NULL
#         );
#         ''')

#         self.cursor.execute('''
#         CREATE TABLE IF NOT EXISTS Namespaces (
#             id SERIAL PRIMARY KEY,
#             name TEXT NOT NULL,
#             organization_id INTEGER REFERENCES Organizations(id)
#         );
#         ''')

#         self.cursor.execute('''
#         CREATE TABLE IF NOT EXISTS Vectors (
#             id SERIAL PRIMARY KEY,
#             namespace_id INTEGER REFERENCES Namespaces(id),
#             texts JSONB NOT NULL,
#             embeddings JSONB NOT NULL
#         );
#         ''')
#         self.connection.commit()

#     def create_organization(self, name):
#         """Create a new organization."""
#         self.cursor.execute('INSERT INTO Organizations (name) VALUES (%s) RETURNING id', (name,))
#         self.connection.commit()
#         return self.cursor.fetchone()[0]

#     def create_namespace(self, name, organization_id):
#         """Create a new namespace."""
#         self.cursor.execute('INSERT INTO Namespaces (name, organization_id) VALUES (%s, %s) RETURNING id', (name, organization_id))
#         self.connection.commit()
#         return self.cursor.fetchone()[0]

#     def create_vector(self, namespace_id, texts, embeddings):
#         """Create a new vector entry."""
#         self.cursor.execute('INSERT INTO Vectors (namespace_id, texts, embeddings) VALUES (%s, %s, %s) RETURNING id',
#                             (namespace_id, json.dumps(texts), json.dumps(embeddings)))
#         self.connection.commit()
#         return self.cursor.fetchone()[0]

#     def read_vector(self, vector_id):
#         """Read a vector entry by ID."""
#         self.cursor.execute('SELECT * FROM Vectors WHERE id = %s', (vector_id,))
#         row = self.cursor.fetchone()
#         if row:
#             return {'id': row[0], 'namespace_id': row[1], 'texts': row[2], 'embeddings': row[3]}
#         else:
#             return "Vector not found."

#     def update_vector(self, vector_id, new_texts=None, new_embeddings=None):
#         """Update a vector entry."""
#         if new_texts:
#             self.cursor.execute('UPDATE Vectors SET texts = %s WHERE id = %s', (json.dumps(new_texts), vector_id))
#         if new_embeddings:
#             self.cursor.execute('UPDATE Vectors SET embeddings = %s WHERE id = %s', (json.dumps(new_embeddings), vector_id))
#         self.connection.commit()

#     def delete_vector(self, vector_id):
#         """Delete a vector entry."""
#         self.cursor.execute('DELETE FROM Vectors WHERE id = %s', (vector_id,))
#         self.connection.commit()

#     def close(self):
#         """Close the database connection."""
#         self.cursor.close()
#         self.connection.close()

# # Example usage
# if __name__ == "__main__":
#     db_manager = DatabaseManager('test', 'nesta', 'lucky')

#     # Create an organization
#     org_id = db_manager.create_organization("animal")
    
#     # Create a namespace within that organization
#     namespace_id = db_manager.create_namespace("cat", org_id)
    
#     # Create a vector in that namespace
#     Ba = []
#     for i in range(0, 1000000):
#         Ba.append(i)
#     vector_id = db_manager.create_vector(namespace_id, ["hello", "world"], [Ba, [1, 2, 3]])

    
#     # Read the vector
#     print(db_manager.read_vector(vector_id))
    
#     # Update the vector
#     # db_manager.update_vector(vector_id, new_texts=["hi", "there"], new_embeddings=[4, 5, 6])
    
#     # Read the updated vector
#     print(db_manager.read_vector(vector_id))
    
#     # Delete the vector
#     # db_manager.delete_vector(vector_id)
    
#     # Try to read the deleted vector
#     print(db_manager.read_vector(vector_id))
    
#     # Close the database connection
#     db_manager.close()




import psycopg2
from psycopg2 import sql
from psycopg2.extras import execute_values

# Database connection parameters
DB_PARAMS = {
    'dbname': 'test',
    'user': 'nesta',
    'password': 'lucky',
    'host': 'localhost',
    'port': 5432,
}

class DBManager:
    def __init__(self):
        self.conn = psycopg2.connect(**DB_PARAMS)
        self.create_tables()

    def create_tables(self):
        commands = (
            """
            CREATE TABLE IF NOT EXISTS validators (
                validator_id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS organizations (
                organization_id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                validator_id INTEGER REFERENCES validators(validator_id)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS namespaces (
                namespace_id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                organization_id INTEGER REFERENCES organizations(organization_id)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS vectors (
                vector_id SERIAL PRIMARY KEY,
                original_text_id INTEGER NOT NULL,
                original_text TEXT NOT NULL,
                embedding FLOAT[] NOT NULL,
                namespace_id INTEGER REFERENCES namespaces(namespace_id)
            )
            """
        )
        cur = self.conn.cursor()
        for command in commands:
            cur.execute(command)
        self.conn.commit()
        cur.close()

    # Validator operations
    def add_validator(self, name):
        cur = self.conn.cursor()
        cur.execute("INSERT INTO validators (name) VALUES (%s) RETURNING validator_id", (name,))
        validator_id = cur.fetchone()[0]
        self.conn.commit()
        cur.close()
        return validator_id

    def get_validator(self, validator_id):
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM validators WHERE validator_id = %s", (validator_id,))
        validator = cur.fetchone()
        cur.close()
        return validator

    def update_validator(self, validator_id, new_name):
        cur = self.conn.cursor()
        cur.execute("UPDATE validators SET name = %s WHERE validator_id = %s", (new_name, validator_id))
        self.conn.commit()
        cur.close()

    def delete_validator(self, validator_id):
        cur = self.conn.cursor()
        cur.execute("DELETE FROM validators WHERE validator_id = %s", (validator_id,))
        self.conn.commit()
        cur.close()

    # Organization operations
    def add_organization(self, validator_id, name):
        cur = self.conn.cursor()
        cur.execute("INSERT INTO organizations (name, validator_id) VALUES (%s, %s) RETURNING organization_id", (name, validator_id))
        organization_id = cur.fetchone()[0]
        self.conn.commit()
        cur.close()
        return organization_id

    def get_organization(self, organization_id):
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM organizations WHERE organization_id = %s", (organization_id,))
        organization = cur.fetchone()
        cur.close()
        return organization

    def update_organization(self, organization_id, new_name):
        cur = self.conn.cursor()
        cur.execute("UPDATE organizations SET name = %s WHERE organization_id = %s", (new_name, organization_id))
        self.conn.commit()
        cur.close()

    def delete_organization(self, organization_id):
        cur = self.conn.cursor()
        cur.execute("DELETE FROM organizations WHERE organization_id = %s", (organization_id,))
        self.conn.commit()
        cur.close()

    # Namespace operations
    def add_namespace(self, organization_id, name):
        cur = self.conn.cursor()
        cur.execute("INSERT INTO namespaces (name, organization_id) VALUES (%s, %s) RETURNING namespace_id", (name, organization_id))
        namespace_id = cur.fetchone()[0]
        self.conn.commit()
        cur.close()
        return namespace_id

    def get_namespace(self, namespace_id):
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM namespaces WHERE namespace_id = %s", (namespace_id,))
        namespace = cur.fetchone()
        cur.close()
        return namespace

    def update_namespace(self, namespace_id, new_name):
        cur = self.conn.cursor()
        cur.execute("UPDATE namespaces SET name = %s WHERE namespace_id = %s", (new_name, namespace_id))
        self.conn.commit()
        cur.close()

    def delete_namespace(self, namespace_id):
        cur = self.conn.cursor()
        cur.execute("DELETE FROM namespaces WHERE namespace_id = %s", (namespace_id,))
        self.conn.commit()
        cur.close()

    # Vector operations
    def add_vector(self, original_text_id, original_text, embedding, namespace_id):
        cur = self.conn.cursor()
        cur.execute(
            "INSERT INTO vectors (original_text_id, original_text, embedding, namespace_id) VALUES (%s, %s, %s, %s) RETURNING vector_id",
            (original_text_id, original_text, embedding, namespace_id)
        )
        vector_id = cur.fetchone()[0]
        self.conn.commit()
        cur.close()
        return vector_id

    def get_vector(self, vector_id):
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM vectors WHERE vector_id = %s", (vector_id,))
        vector = cur.fetchone()
        cur.close()
        return vector

    def delete_vector(self, vector_id):
        cur = self.conn.cursor()
        cur.execute("DELETE FROM vectors WHERE vector_id = %s", (vector_id,))
        self.conn.commit()
        cur.close()

    def close_connection(self):
        self.conn.close()

# Example Usage
if __name__ == '__main__':
    db_manager = DBManager()

    # Add a validator
    validator_id = db_manager.add_validator('taostats')
    print(f"Added validator with ID: {validator_id}")

    # Get a validator
    validator = db_manager.get_validator(validator_id)
    print(f"Retrieved validator: {validator}")

    # Update a validator
    db_manager.update_validator(validator_id, 'new_taostats')
    print(f"Updated validator with ID: {validator_id}")

    # Delete a validator
    db_manager.delete_validator(validator_id)
    print(f"Deleted validator with ID: {validator_id}")

    # Close the database connection
    db_manager.close_connection()

