import psycopg2
from psycopg2 import sql
import os
from dotenv import load_dotenv

load_dotenv()

def delete_all_databases(db_user_name, password, db_port):
    """Delete all non-system databases."""
    conn = psycopg2.connect(dbname='postgres', user=db_user_name, password=password, host='localhost', port=db_port)
    conn.autocommit = True
    try:
        with conn.cursor() as cur:
            # Fetch all non-template databases
            cur.execute("""
                SELECT datname 
                FROM pg_database 
                WHERE datistemplate = false AND datname != 'postgres';
            """)
            databases = cur.fetchall()
            # Drop each database
            for db in databases:
                db_name = db[0]
                print(f"Dropping database: {db_name}")

                # Terminate active connections before dropping the database
                cur.execute(sql.SQL("""
                    SELECT pg_terminate_backend(pg_stat_activity.pid)
                    FROM pg_stat_activity
                    WHERE pg_stat_activity.datname = %s AND pid <> pg_backend_pid();
                """), [db_name])

                # Drop the database
                cur.execute(sql.SQL("DROP DATABASE {}").format(sql.Identifier(db_name)))

            print("All databases have been dropped.")
    finally:
        conn.close()

if __name__ == "__main__":
    
    db_user_name = os.getenv("POSTGRESQL_USER_NAME")
    password = os.getenv("POSTGRES_PASSWORD")
    db_port = os.getenv("DB_PORT")
    
    delete_all_databases(db_user_name, password, db_port)