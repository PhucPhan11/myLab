import time
from datetime import datetime

def generate_job_param():
    # 1. Get current Unix timestamp (integer)
    unix_timestamp = int(time.time())
    
    # 2. Get current date for Month abbreviation and Day
    # %b = Short month name (Jan, Feb, etc.)
    # %d = Day of the month (01, 02, etc.)
    now = datetime.now()
    month_day = now.strftime("%b%d").lower()
    
    # 3. Combine into the final format
    job_param = f"{unix_timestamp}_{month_day}"
    
    return job_param

# --- Execution ---
print(f'Generated Param: "{generate_job_param()}"')