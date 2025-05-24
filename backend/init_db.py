# backend/init_db.py
from database import create_db_tables, engine
from sqlalchemy import text

if __name__ == "__main__":
    print("Creating database tables...")
    create_db_tables()
    # Optional: Add the gen_random_uuid extension if not already present
    with engine.connect() as connection:
        connection.execute(text('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";'))
        connection.commit()
    print("Database tables created successfully!")
