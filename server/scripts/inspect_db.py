import sqlite3
import sys

def inspect_db(db_path: str):
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()

        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = cursor.fetchall()

        if not tables:
            print("No tables found.")
            return

        for (table_name,) in tables:
            print(f"\n{'='*50}")
            print(f" TABLE: {table_name}")
            print(f"{'='*50}")

            # Get column info
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            print(f"{'Col':<5} {'Name':<20} {'Type':<15} {'Nullable':<10} {'Default':<15} {'PK'}")
            print("-" * 75)
            for col in columns:
                cid, name, col_type, notnull, default, pk = col
                print(f"{cid:<5} {name:<20} {col_type:<15} {str(not notnull):<10} {str(default):<15} {bool(pk)}")

            # Get row count
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"\nTotal rows: {count}")

            # Preview first 3 rows
            if count > 0:
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 5")
                rows = cursor.fetchall()
                col_names = [desc[0] for desc in cursor.description]
                print(f"\nPreview:")
                print("  " + " | ".join(f"{c:<15}" for c in col_names))
                print("  " + "-" * (18 * len(col_names)))
                for row in rows:
                    print("  " + " | ".join(f"{str(v):<15}" for v in row))

if __name__ == "__main__":
    db_path = sys.argv[1] if len(sys.argv) > 1 else "app.db"
    inspect_db(db_path)