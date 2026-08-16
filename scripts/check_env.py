import sys
import xgboost as xgb
import pandas as pd
import numpy as np
import sklearn
import imblearn
import shap
import streamlit as st
import json

print(f"Python version: {sys.version}")
print(f"XGBoost version: {xgb.__version__}")

build_info = xgb.build_info()
print("XGBoost Build Info:")
print(build_info)

try:
    build_info_dict = json.loads(build_info)
    use_cuda = build_info_dict.get('USE_CUDA', False)
    print(f"Parsed USE_CUDA: {use_cuda}")
    if use_cuda not in [True, "ON", "1", "true"]:
        print("WARNING: USE_CUDA is False or missing. Failing loudly!")
        sys.exit(1)
except Exception as e:
    print(f"Could not parse build_info as JSON: {e}")
    if any(x in build_info.upper() for x in ['"USE_CUDA": "ON"', '"USE_CUDA": "1"', '"USE_CUDA": TRUE', 'USE_CUDA: 1', 'USE_CUDA: ON']):
        print("USE_CUDA appears to be True based on string search.")
    else:
        print("WARNING: USE_CUDA not detected in build_info string search. Failing loudly!")
        sys.exit(1)

print("Environment check passed!")
