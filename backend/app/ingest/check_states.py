from sqlalchemy import text
from app.database import engine


def main():
    with engine.begin() as conn:
        res = conn.execute(text("SELECT recipient_state, COUNT(*) FROM awards WHERE latitude IS NULL GROUP BY recipient_state LIMIT 5")).fetchall()
        for row in res:
            print(row[0], row[1])


if __name__ == '__main__':
    main()

