import psycopg2
import json

class DatabaseManager:
    def __init__(self, dbname, user, password, host='localhost', port='5432'):
        self.connection = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port
        )
        self.cursor = self.connection.cursor()
        self._create_tables()

    def _create_tables(self):
        """Create tables for organizations, namespaces, and vectors."""
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS Organizations (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL
        );
        ''')

        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS Namespaces (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            organization_id INTEGER REFERENCES Organizations(id)
        );
        ''')

        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS Vectors (
            id SERIAL PRIMARY KEY,
            namespace_id INTEGER REFERENCES Namespaces(id),
            texts JSONB NOT NULL,
            embeddings JSONB NOT NULL
        );
        ''')
        self.connection.commit()

    def create_organization(self, name):
        """Create a new organization."""
        self.cursor.execute('INSERT INTO Organizations (name) VALUES (%s) RETURNING id', (name,))
        self.connection.commit()
        return self.cursor.fetchone()[0]

    def create_namespace(self, name, organization_id):
        """Create a new namespace."""
        self.cursor.execute('INSERT INTO Namespaces (name, organization_id) VALUES (%s, %s) RETURNING id', (name, organization_id))
        self.connection.commit()
        return self.cursor.fetchone()[0]

    def create_vector(self, namespace_id, texts, embeddings):
        """Create a new vector entry."""
        self.cursor.execute('INSERT INTO Vectors (namespace_id, texts, embeddings) VALUES (%s, %s, %s) RETURNING id',
                            (namespace_id, json.dumps(texts), json.dumps(embeddings)))
        self.connection.commit()
        return self.cursor.fetchone()[0]

    def read_vector(self, vector_id):
        """Read a vector entry by ID."""
        self.cursor.execute('SELECT * FROM Vectors WHERE id = %s', (vector_id,))
        row = self.cursor.fetchone()
        if row:
            return {'id': row[0], 'namespace_id': row[1], 'texts': row[2], 'embeddings': row[3]}
        else:
            return "Vector not found."

    def update_vector(self, vector_id, new_texts=None, new_embeddings=None):
        """Update a vector entry."""
        if new_texts:
            self.cursor.execute('UPDATE Vectors SET texts = %s WHERE id = %s', (json.dumps(new_texts), vector_id))
        if new_embeddings:
            self.cursor.execute('UPDATE Vectors SET embeddings = %s WHERE id = %s', (json.dumps(new_embeddings), vector_id))
        self.connection.commit()

    def delete_vector(self, vector_id):
        """Delete a vector entry."""
        self.cursor.execute('DELETE FROM Vectors WHERE id = %s', (vector_id,))
        self.connection.commit()

    def close(self):
        """Close the database connection."""
        self.cursor.close()
        self.connection.close()

# Example usage
if __name__ == "__main__":
    db_manager = DatabaseManager('test', 'nesta', 'lucky')

    # Create an organization
    org_id = db_manager.create_organization("animal")
    
    # Create a namespace within that organization
    namespace_id = db_manager.create_namespace("cat", org_id)
    
    # Create a vector in that namespace
    vector_id = db_manager.create_vector(namespace_id, ["hello", "world"], [1, 2, 3])
    
    # Read the vector
    print(db_manager.read_vector(vector_id))
    
    # Update the vector
    db_manager.update_vector(vector_id, new_texts=["hi", "there"], new_embeddings=[4, 5, 6])
    
    # Read the updated vector
    print(db_manager.read_vector(vector_id))
    
    # Delete the vector
    db_manager.delete_vector(vector_id)
    
    # Try to read the deleted vector
    print(db_manager.read_vector(vector_id))
    
    # Close the database connection
    db_manager.close()
