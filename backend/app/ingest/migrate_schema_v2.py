"""Migration script for schema v2."""
from sqlalchemy import text
from app.database import engine
from app.models.relationship import OpportunityRelationship
from app.models.opportunity import Opportunity

def migrate():
    print("Starting migration...")
    
    # 3. Create opportunity_relationships if not exists
    Opportunity.metadata.create_all(engine)
    
    with engine.connect() as conn:
        def get_cols(table):
            return {row[1] for row in conn.execute(text(f"PRAGMA table_info({table})")).fetchall()}
            
        opp_cols = get_cols("opportunities")
        opp_new_cols = {
            "org_type": "VARCHAR(30)",
            "funding_type": "VARCHAR(50)",
            "award_min": "FLOAT",
            "award_typical": "FLOAT",
            "performance_period": "VARCHAR(100)",
            "expected_awards": "INTEGER",
            "objectives": "TEXT",
            "allowable_costs": "TEXT",
            "selection_criteria": "TEXT",
            "keywords": "TEXT",
            "raw_source_data": "TEXT",
            "is_historical": "BOOLEAN",
            "open_date": "DATETIME",
            "close_date": "DATETIME",
            "award_date": "DATETIME",
            "year": "INTEGER",
            "target_trl_min": "INTEGER",
            "target_trl_max": "INTEGER",
            "geographic_scope": "VARCHAR(200)",
            "data_provenance": "VARCHAR(50)"
        }
        
        # 1 & 2. Add missing columns
        for col, col_def in opp_new_cols.items():
            if col not in opp_cols:
                conn.execute(text(f"ALTER TABLE opportunities ADD COLUMN {col} {col_def}"))
                print(f"Added {col} to opportunities")
                
        hist_cols = get_cols("historical_opportunities")
        hist_new_cols = {
            "org_type": "VARCHAR(30)",
            "funding_type": "VARCHAR(50)",
            "total_funding": "FLOAT",
            "max_per_award": "FLOAT",
            "objectives": "TEXT",
            "raw_source_data": "TEXT",
            "data_provenance": "VARCHAR(50)"
        }
        
        for col, col_def in hist_new_cols.items():
            if col not in hist_cols:
                conn.execute(text(f"ALTER TABLE historical_opportunities ADD COLUMN {col} {col_def}"))
                print(f"Added {col} to historical_opportunities")
                
        # 4. Backfill default values
        conn.execute(text("UPDATE opportunities SET org_type = 'government' WHERE org_type IS NULL"))
        conn.execute(text("UPDATE opportunities SET is_historical = 0 WHERE is_historical IS NULL"))
        conn.execute(text("UPDATE opportunities SET data_provenance = 'observed' WHERE data_provenance IS NULL"))
        conn.execute(text("UPDATE historical_opportunities SET data_provenance = 'observed' WHERE data_provenance IS NULL"))
        
        # 5. Extract year
        conn.execute(text("UPDATE opportunities SET year = CAST(strftime('%Y', COALESCE(first_seen_at, created_at)) AS INTEGER) WHERE year IS NULL"))
        
        conn.commit()
    print("Migration completed successfully.")

if __name__ == '__main__':
    migrate()
