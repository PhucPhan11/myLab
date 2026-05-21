from datetime import datetime

def generate_sql_timestamp() -> str:
    """Generate a SQL TIMESTAMP literal using the local datetime with nanosecond precision."""
    now = datetime.now()

    # Format: yyyy-mm-dd hh:mm:ss.nnnnnnnnn (nanoseconds = microseconds * 1000)
    nanoseconds = now.microsecond * 1000
    formatted = now.strftime(f"%Y-%m-%d %H:%M:%S.{nanoseconds:09d}")

    return f"TIMESTAMP '{formatted}'"


def generate_sql_script(table: str = "your_table") -> str:
    """Generate a sample SQL script using the local timestamp."""
    ts = generate_sql_timestamp()
    return f"SELECT * FROM {table} WHERE created_at >= {ts};"


if __name__ == "__main__":
    print("Timestamp literal :", generate_sql_timestamp())
    print("Sample SQL script  :", generate_sql_script("orders"))