import time
import os
import sys

start_time = time.time()
print("Starting cold-start initialization measurement...", flush=True)

sys.path.append(os.path.abspath('.'))
from backend.db import MuleDatabase

db = MuleDatabase()
cases = db.cases_db

elapsed = time.time() - start_time
print(f"Cold-Start Database & Model Load Time: {elapsed:.2f} seconds.")
print(f"Loaded {len(cases)} cases into memory successfully.")
