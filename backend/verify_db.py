from database import engine, Base, SessionLocal
import models
from sqlalchemy import inspect

def verify():
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print(f"Tables found: {tables}")
    
    if "streams" in tables and "sessions" in tables:
        print("SUCCESS: Database tables verified.")
    else:
        print("FAILURE: Tables missing.")

if __name__ == "__main__":
    verify()
