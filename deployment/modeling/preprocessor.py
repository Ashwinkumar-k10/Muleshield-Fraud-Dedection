import pandas as pd
import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin

RAW_CATEGORICAL_COLS = ['F2230', 'F3886', 'F3888', 'F3889', 'F3890', 'F3891', 'F3892', 'F3893']
TARGET_COL = 'F3924'

class MuleShieldPreprocessor(BaseEstimator, TransformerMixin):
    def __init__(self):
        self.high_missing_cols_ = []
        self.medians_ = {}
        self.percentiles_ = {} # (lower, upper)
        self.cat_cols_to_use_ = ['F3886', 'F3889', 'F3890', 'F3891', 'F3892', 'F3893']
        self.feature_columns_ = []
        
    def fit(self, X, y=None):
        X_df = X.copy()
        num_cols = [c for c in X_df.columns if c not in RAW_CATEGORICAL_COLS and c != TARGET_COL]
        
        missing_pct = X_df[num_cols].isnull().mean()
        self.high_missing_cols_ = missing_pct[missing_pct > 0.7].index.tolist()
        
        for c in num_cols:
            if c not in self.high_missing_cols_:
                self.medians_[c] = float(X_df[c].median()) if not pd.isnull(X_df[c].median()) else 0.0
            lower = float(X_df[c].quantile(0.01))
            upper = float(X_df[c].quantile(0.99))
            self.percentiles_[c] = (lower, upper)
            
        transformed_df = self.transform(X_df)
        self.feature_columns_ = transformed_df.columns.tolist()
        return self

    def transform(self, X):
        X_df = X.copy()
        
        for leaked in ['F2230', 'F3888']:
            if leaked in X_df.columns:
                X_df = X_df.drop(columns=[leaked])
                
        num_cols = [c for c in X_df.columns if c not in RAW_CATEGORICAL_COLS and c != TARGET_COL]
        cat_cols = [c for c in X_df.columns if c in self.cat_cols_to_use_]
        
        for c in num_cols:
            if c not in self.high_missing_cols_:
                if c in self.medians_:
                    X_df[f"{c}_ismissing"] = X_df[c].isnull().astype(int)
                    X_df[c] = X_df[c].fillna(self.medians_[c])
            else:
                X_df[c] = X_df[c].fillna(-9999)
                
            if c in self.percentiles_:
                lower, upper = self.percentiles_[c]
                X_df[c] = X_df[c].clip(lower=lower, upper=upper)
                
        if cat_cols:
            X_df = pd.get_dummies(X_df, columns=cat_cols, dummy_na=True, drop_first=True)
            
        if TARGET_COL in X_df.columns:
            X_df = X_df.drop(columns=[TARGET_COL])

        # Drop post-incident resolution flags
        post_inc_base = ['F3898', 'F3899', 'F3912', 'F3913', 'F3914', 'F3915']
        to_drop = [c for c in X_df.columns if any(c.startswith(p) for p in post_inc_base)]
        if to_drop:
            X_df = X_df.drop(columns=to_drop)

        # Domain Feature Engineering
        if 'F2122' in X_df.columns and 'F670' in X_df.columns:
            X_df['BANK_FE_CASH_TO_UPI_RATIO'] = X_df['F2122'] / (X_df['F670'].abs() + 1.0)
        if 'F2582' in X_df.columns and 'F2737' in X_df.columns:
            X_df['BANK_FE_UPI_TO_TOTAL_DEV_RATIO'] = X_df['F2582'] / (X_df['F2737'].abs() + 1.0)
        if 'F3887' in X_df.columns and 'F3894' in X_df.columns:
            X_df['BANK_FE_TENURE_AGE_RATIO'] = X_df['F3887'] / (X_df['F3894'].abs() + 1.0)
            
        if self.feature_columns_:
            X_df = X_df.reindex(columns=self.feature_columns_, fill_value=0)
            
        if '' in X_df.columns:
            X_df = X_df.drop(columns=[''])
            
        return X_df
