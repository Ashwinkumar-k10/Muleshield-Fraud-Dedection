import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.metrics import precision_recall_curve, auc, f1_score, precision_score, recall_score
from sklearn.metrics.pairwise import cosine_similarity
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import connected_components
from imblearn.over_sampling import SMOTE, BorderlineSMOTE, ADASYN
import warnings
import json
import os
import sys

warnings.filterwarnings('ignore')

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from modeling.preprocessor import MuleShieldPreprocessor

def print_p(msg):
    print(msg, flush=True)

def main():
    print_p("==========================================================================")
    print_p(" MULESHIELD PRO — PRODUCTION ML PIPELINE & HYPERPARAMETER OPTIMIZATION")
    print_p("==========================================================================")
    
    # 1. Load Data & Excel Mapping
    raw_csv_path = os.path.join('data', 'data_copy.csv') if os.path.exists(os.path.join('data', 'data_copy.csv')) else 'data_copy.csv'
    excel_path = os.path.join('data', 'Description.xlsx') if os.path.exists(os.path.join('data', 'Description.xlsx')) else 'Description.xlsx'
    
    print_p(f"Loading raw dataset from {raw_csv_path}...")
    df_raw = pd.read_csv(raw_csv_path, engine='pyarrow')
    if 'Unnamed: 0' in df_raw.columns:
        df_raw = df_raw.drop(columns=['Unnamed: 0'])
        
    y_raw = df_raw['F3924'].astype(int)
    X_raw = df_raw.drop(columns=['F3924'])
    
    print_p(f"Loaded dataset: {X_raw.shape[0]} rows, {X_raw.shape[1]} features.")
    print_p(f"Target Distribution: Fraud={sum(y_raw==1)} ({sum(y_raw==1)/len(y_raw):.4%}), Non-Fraud={sum(y_raw==0)}")
    
    # 2. Preprocess & Feature Audit
    preprocessor = MuleShieldPreprocessor()
    X_processed = preprocessor.fit_transform(X_raw)
    
    # Identify and drop post-incident / resolution status columns
    post_incident_base_cols = ['F3898', 'F3899', 'F3912', 'F3913', 'F3914', 'F3915']
    post_inc_cols = [c for c in X_processed.columns if any(c.startswith(p) for p in post_incident_base_cols)]
    
    print_p(f"\n[LEAKAGE SANITIZATION] Dropping {len(post_inc_cols)} post-incident resolution columns:")
    for col in post_inc_cols:
        print_p(f" - Dropped: {col}")
        
    X_clean = X_processed.drop(columns=post_inc_cols)
    
    # 3. Domain Feature Engineering
    print_p("\n[FEATURE ENGINEERING] Adding banking domain ratio features...")
    if 'F2122' in X_clean.columns and 'F670' in X_clean.columns:
        X_clean['BANK_FE_CASH_TO_UPI_RATIO'] = X_clean['F2122'] / (X_clean['F670'].abs() + 1.0)
    if 'F2582' in X_clean.columns and 'F2737' in X_clean.columns:
        X_clean['BANK_FE_UPI_TO_TOTAL_DEV_RATIO'] = X_clean['F2582'] / (X_clean['F2737'].abs() + 1.0)
    if 'F3887' in X_clean.columns and 'F3894' in X_clean.columns:
        X_clean['BANK_FE_TENURE_AGE_RATIO'] = X_clean['F3887'] / (X_clean['F3894'].abs() + 1.0)
        
    print_p(f"Final Sanitize Features Count: {X_clean.shape[1]}")
    
    # 4. Group-Aware Duplicate Clustering (58 Groups)
    print_p("\n[GROUP-AWARE CV] Clustering near-duplicate account profiles (>0.99 similarity)...")
    from sklearn.preprocessing import normalize
    X_norm = normalize(X_clean.fillna(0).values, norm='l2', axis=1)
    sim_matrix = cosine_similarity(X_norm)
    adj_matrix = csr_matrix(sim_matrix > 0.99)
    n_components, groups = connected_components(csgraph=adj_matrix, directed=False, return_labels=True)
    print_p(f"Isolated {len(np.unique(groups))} group clusters across {len(groups)} accounts.")
    
    # 5. Class Imbalance Strategy Benchmark
    print_p("\n==========================================================================")
    print_p(" 1. BENCHMARKING CLASS IMBALANCE HANDLING STRATEGIES (5-Fold Group CV)")
    print_p("==========================================================================")
    
    cv = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=42)
    pos_weight = (len(y_raw) - sum(y_raw)) / sum(y_raw)
    
    imbalance_strategies = {
        'SMOTE + scale_pos_weight': ('smote', pos_weight),
        'Borderline-SMOTE + scale_pos_weight': ('borderline', pos_weight),
        'ADASYN + scale_pos_weight': ('adasyn', pos_weight),
        'Pure scale_pos_weight (No Oversampling)': ('none', pos_weight),
        'Unweighted Baseline': ('none', 1.0)
    }
    
    for strat_name, (resample_type, p_weight) in imbalance_strategies.items():
        print_p(f"Evaluating strategy: {strat_name} ...")
        pr_aucs, f1s, recalls, precisions = [], [], [], []
        
        for train_idx, val_idx in cv.split(X_clean, y_raw, groups=groups):
            X_tr, y_tr = X_clean.iloc[train_idx], y_raw.iloc[train_idx]
            X_va, y_va = X_clean.iloc[val_idx], y_raw.iloc[val_idx]
            
            if resample_type == 'smote':
                sampler = SMOTE(random_state=42)
                X_tr_res, y_tr_res = sampler.fit_resample(X_tr, y_tr)
            elif resample_type == 'borderline':
                sampler = BorderlineSMOTE(random_state=42)
                X_tr_res, y_tr_res = sampler.fit_resample(X_tr, y_tr)
            elif resample_type == 'adasyn':
                sampler = ADASYN(random_state=42)
                X_tr_res, y_tr_res = sampler.fit_resample(X_tr, y_tr)
            else:
                X_tr_res, y_tr_res = X_tr, y_tr
                
            clf = xgb.XGBClassifier(
                tree_method='hist',
                scale_pos_weight=p_weight,
                max_depth=3,
                min_child_weight=3,
                subsample=0.8,
                colsample_bytree=0.8,
                learning_rate=0.05,
                n_estimators=200,
                random_state=42
            )
            clf.fit(X_tr_res, y_tr_res)
            
            y_prob_tr = clf.predict_proba(X_tr)[:, 1]
            y_prob_va = clf.predict_proba(X_va)[:, 1]
            
            p_tr, r_tr, t_tr = precision_recall_curve(y_tr, y_prob_tr)
            f1_tr = 2 * r_tr * p_tr / (r_tr + p_tr + 1e-10)
            best_idx = np.argmax(f1_tr)
            best_thresh = t_tr[best_idx] if best_idx < len(t_tr) else 0.5
            
            p_va, r_va, _ = precision_recall_curve(y_va, y_prob_va)
            pr_auc_val = auc(r_va, p_va)
            y_pred_va = (y_prob_va >= best_thresh).astype(int)
            
            pr_aucs.append(pr_auc_val)
            f1s.append(f1_score(y_va, y_pred_va, zero_division=0))
            recalls.append(recall_score(y_va, y_pred_va, zero_division=0))
            precisions.append(precision_score(y_va, y_pred_va, zero_division=0))
            
        mean_pr_auc, std_pr_auc = np.mean(pr_aucs), np.std(pr_aucs)
        mean_f1 = np.mean(f1s)
        mean_rec = np.mean(recalls)
        mean_prec = np.mean(precisions)
        
        print_p(f" RESULT -> {strat_name:<42} | PR-AUC: {mean_pr_auc:.4f} +/- {std_pr_auc:.4f} | F1: {mean_f1:.4f} | Rec: {mean_rec:.4f} | Prec: {mean_prec:.4f}")

    # 6. Hyperparameter Optimization Search
    print_p("\n==========================================================================")
    print_p(" 2. HYPERPARAMETER SEARCH (REGULARIZATION & GENERALIZATION)")
    print_p("==========================================================================")
    
    param_configs = [
        {'max_depth': 3, 'min_child_weight': 3, 'gamma': 0.1, 'subsample': 0.8, 'colsample_bytree': 0.8, 'reg_alpha': 0.1, 'reg_lambda': 1.0, 'lr': 0.05, 'n_est': 200},
        {'max_depth': 4, 'min_child_weight': 5, 'gamma': 0.2, 'subsample': 0.7, 'colsample_bytree': 0.7, 'reg_alpha': 0.5, 'reg_lambda': 2.0, 'lr': 0.03, 'n_est': 250},
        {'max_depth': 3, 'min_child_weight': 5, 'gamma': 0.5, 'subsample': 0.8, 'colsample_bytree': 0.7, 'reg_alpha': 1.0, 'reg_lambda': 3.0, 'lr': 0.03, 'n_est': 300},
        {'max_depth': 2, 'min_child_weight': 3, 'gamma': 0.0, 'subsample': 0.8, 'colsample_bytree': 0.8, 'reg_alpha': 0.0, 'reg_lambda': 1.0, 'lr': 0.05, 'n_est': 200},
    ]
    
    best_config = None
    best_pr_auc = -1.0
    
    for i, cfg in enumerate(param_configs, 1):
        print_p(f"Testing Config #{i}: max_depth={cfg['max_depth']}, min_child={cfg['min_child_weight']}, gamma={cfg['gamma']}, alpha={cfg['reg_alpha']}, lambda={cfg['reg_lambda']}...")
        pr_aucs = []
        for train_idx, val_idx in cv.split(X_clean, y_raw, groups=groups):
            X_tr, y_tr = X_clean.iloc[train_idx], y_raw.iloc[train_idx]
            X_va, y_va = X_clean.iloc[val_idx], y_raw.iloc[val_idx]
            
            smote = SMOTE(random_state=42)
            X_tr_res, y_tr_res = smote.fit_resample(X_tr, y_tr)
            
            clf = xgb.XGBClassifier(
                tree_method='hist',
                scale_pos_weight=pos_weight,
                max_depth=cfg['max_depth'],
                min_child_weight=cfg['min_child_weight'],
                gamma=cfg['gamma'],
                subsample=cfg['subsample'],
                colsample_bytree=cfg['colsample_bytree'],
                reg_alpha=cfg['reg_alpha'],
                reg_lambda=cfg['reg_lambda'],
                learning_rate=cfg['lr'],
                n_estimators=cfg['n_est'],
                random_state=42
            )
            clf.fit(X_tr_res, y_tr_res)
            
            y_prob_va = clf.predict_proba(X_va)[:, 1]
            p_va, r_va, _ = precision_recall_curve(y_va, y_prob_va)
            pr_aucs.append(auc(r_va, p_va))
            
        m_auc = np.mean(pr_aucs)
        print_p(f" RESULT -> Config #{i} PR-AUC: {m_auc:.4f} +/- {np.std(pr_aucs):.4f}")
        
        if m_auc > best_pr_auc:
            best_pr_auc = m_auc
            best_config = cfg

    print_p(f"\nChampion Hyperparameter Config Selected: {best_config} with Mean PR-AUC: {best_pr_auc:.4f}")
    
    # 7. Train Final Champion Model on 100% Clean Data
    print_p("\n==========================================================================")
    print_p(" 3. FITTING CHAMPION XGBOOST MODEL & SAVING ARTIFACTS")
    print_p("==========================================================================")
    
    smote_final = SMOTE(random_state=42)
    X_res, y_res = smote_final.fit_resample(X_clean, y_raw)
    
    champion_model = xgb.XGBClassifier(
        tree_method='hist',
        scale_pos_weight=pos_weight,
        max_depth=best_config['max_depth'],
        min_child_weight=best_config['min_child_weight'],
        gamma=best_config['gamma'],
        subsample=best_config['subsample'],
        colsample_bytree=best_config['colsample_bytree'],
        reg_alpha=best_config['reg_alpha'],
        reg_lambda=best_config['reg_lambda'],
        learning_rate=best_config['lr'],
        n_estimators=best_config['n_est'],
        random_state=42
    )
    champion_model.fit(X_res, y_res)
    
    y_probs_full = champion_model.predict_proba(X_clean)[:, 1]
    p_f, r_f, t_f = precision_recall_curve(y_raw, y_probs_full)
    f1_scores_f = 2 * r_f * p_f / (r_f + p_f + 1e-10)
    opt_idx = np.argmax(f1_scores_f)
    opt_thresh = float(t_f[opt_idx]) if opt_idx < len(t_f) else 0.9934
    
    print_p(f"Optimal Decision Threshold Calibrated: {opt_thresh:.4f}")
    print_p(f"At Threshold {opt_thresh:.4f}: Precision = {p_f[opt_idx]:.4f}, Recall = {r_f[opt_idx]:.4f}, F1 = {f1_scores_f[opt_idx]:.4f}")
    
    os.makedirs('modeling', exist_ok=True)
    
    model_json_path = 'modeling/mule_shield_model.json'
    champion_model.save_model(model_json_path)
    print_p(f"Saved Champion XGBoost JSON model to: {model_json_path}")
    
    schema_path = 'modeling/feature_schema.json'
    with open(schema_path, 'w') as f:
        json.dump(X_clean.columns.tolist(), f)
    print_p(f"Saved Feature Schema ({len(X_clean.columns)} features) to: {schema_path}")
    
    config_path = 'modeling/model_config.json'
    with open(config_path, 'w') as f:
        json.dump({
            'decision_threshold': opt_thresh,
            'pr_auc_mean': best_pr_auc,
            'pos_weight': pos_weight,
            'hyperparameters': best_config,
            'bank_finalized_vars': 19
        }, f, indent=2)
    print_p(f"Saved Model Configuration to: {config_path}")
    
    print_p("\n==========================================================================")
    print_p(" OPTIMIZATION COMPLETED SUCCESSFULLY! ALL ARTIFACTS UPDATED.")
    print_p("==========================================================================")

if __name__ == '__main__':
    main()
