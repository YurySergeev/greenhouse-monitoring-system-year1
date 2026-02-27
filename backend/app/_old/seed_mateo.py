from app.ingest_live import _seed

def main():
    print("✅ main running (seed_mateo)")
    _seed(days=90, snapshot_hour=12)

if __name__ == "__main__":
    main()