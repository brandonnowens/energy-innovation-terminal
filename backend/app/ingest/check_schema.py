from sqlalchemy import text
from app.database import engine


def main():
    with engine.begin() as conn:
        res = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='programs'")).fetchall()
        print("Columns:", [r[0] for r in res])


if __name__ == '__main__':
    main()

