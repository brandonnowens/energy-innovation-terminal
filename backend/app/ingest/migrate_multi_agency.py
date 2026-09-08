import sqlite3
from sqlalchemy import text
from app.database import engine

def migrate():
    print("Starting multi-agency migration...")
    
    with engine.begin() as conn:
        # Helper to check if column exists
        def column_exists(table, column):
            result = conn.execute(text(f"PRAGMA table_info({table})"))
            for row in result:
                if row[1] == column:
                    return True
            return False
            
        print("Checking/updating opportunities table...")
        if not column_exists("opportunities", "agency"):
            conn.execute(text("ALTER TABLE opportunities ADD COLUMN agency VARCHAR(100)"))
            conn.execute(text("ALTER TABLE opportunities ADD COLUMN agency_code VARCHAR(50)"))
            conn.execute(text("ALTER TABLE opportunities ADD COLUMN jurisdiction VARCHAR(20)"))
            conn.execute(text("ALTER TABLE opportunities ADD COLUMN external_id VARCHAR(200)"))
            
            conn.execute(text("UPDATE opportunities SET agency = 'NYSERDA', jurisdiction = 'state_ny'"))
            print("Added multi-agency columns to opportunities.")
            
        print("Checking/updating historical_opportunities table...")
        if not column_exists("historical_opportunities", "agency"):
            conn.execute(text("ALTER TABLE historical_opportunities ADD COLUMN agency VARCHAR(100)"))
            conn.execute(text("UPDATE historical_opportunities SET agency = 'NYSERDA'"))
            print("Added agency column to historical_opportunities.")
            
        print("Checking/updating historical_projects table...")
        if not column_exists("historical_projects", "agency"):
            conn.execute(text("ALTER TABLE historical_projects ADD COLUMN agency VARCHAR(100)"))
            conn.execute(text("UPDATE historical_projects SET agency = 'NYSERDA'"))
            print("Added agency column to historical_projects.")
            
        print("Checking/updating project_analyses table...")
        if not column_exists("project_analyses", "target_location"):
            conn.execute(text("ALTER TABLE project_analyses ADD COLUMN target_location VARCHAR(200)"))
            conn.execute(text("ALTER TABLE project_analyses ADD COLUMN target_agencies TEXT"))
            conn.execute(text("UPDATE project_analyses SET target_location = ny_location"))
            print("Updated project_analyses columns.")
            
    print("Migration complete!")

if __name__ == "__main__":
    migrate()
