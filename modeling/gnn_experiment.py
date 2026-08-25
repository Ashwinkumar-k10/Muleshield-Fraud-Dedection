import os
import json
import sys
import time
import joblib
import pandas as pd
import numpy as np
import xgboost as xgb
import torch
import torch.nn as nn
import torch.nn.functional as F
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, normalize
from sklearn.metrics import precision_score, recall_score, f1_score, precision_recall_curve, auc
from sklearn.metrics.pairwise import cosine_similarity
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import connected_components

sys.path.append('.')
from modeling.preprocessor import MuleShieldPreprocessor

def compute_pr_auc(y_true, y_scores):
    precision, recall, _ = precision_recall_curve(y_true, y_scores)
    return auc(recall, precision)

# PyTorch GraphSAGE Model
class GraphSAGELayer(nn.Module):
    def __init__(self, in_features, out_features):
        super().__init__()
        self.linear_self = nn.Linear(in_features, out_features, bias=False)
        self.linear_neigh = nn.Linear(in_features, out_features, bias=False)
        self.bias = nn.Parameter(torch.zeros(out_features))

    def forward(self, x, adj_norm):
        h_self = self.linear_self(x)
        h_neigh = self.linear_neigh(torch.matmul(adj_norm, x))
        return h_self + h_neigh + self.bias

class GraphSAGEModel(nn.Module):
    def __init__(self, in_features, hidden_features, out_features=1):
        super().__init__()
        self.conv1 = GraphSAGELayer(in_features, hidden_features)
        self.conv2 = GraphSAGELayer(hidden_features, hidden_features)
        self.fc = nn.Linear(hidden_features, out_features)

    def forward(self, x, adj_norm):
        # Layer 1
        h1 = F.relu(self.conv1(x, adj_norm))
        h1 = F.dropout(h1, p=0.2, training=self.training)
        # Layer 2
        h2 = F.relu(self.conv2(h1, adj_norm))
        # Logits output
        logits = self.fc(h2)
        return logits, h2 # Returns logits and node embeddings

def main():
    print("======================================================================")
    print("      MULESHIELD PRO — GRAPH NEURAL NETWORK EXPERIMENTATION PIPELINE  ")
    print("======================================================================\n")

    # 1. Load Data
    data_path = 'data/data_copy.csv'
    if not os.path.exists(data_path):
        print(f"[ERROR] Data path not found: {data_path}")
        return

    df = pd.read_csv(data_path, engine='pyarrow')
    if 'Unnamed: 0' in df.columns:
        df = df.drop(columns=['Unnamed: 0'])

    y = df['F3924'].astype(int).values
    X_raw = df.drop(columns=['F3924'])

    # 2. Preprocess & Feature Engineering (Align with baseline)
    print("[1/6] Preprocessing features and resolving target leakage...")
    preprocessor = MuleShieldPreprocessor()
    X_processed = preprocessor.fit_transform(X_raw)

    post_incident_base_cols = ['F3898', 'F3899', 'F3912', 'F3913', 'F3914', 'F3915']
    post_inc_cols = [c for c in X_processed.columns if any(c.startswith(p) for p in post_incident_base_cols)]
    X_clean = X_processed.drop(columns=post_inc_cols)

    # Adding banking ratios
    if 'F2122' in X_clean.columns and 'F670' in X_clean.columns:
        X_clean['BANK_FE_CASH_TO_UPI_RATIO'] = X_clean['F2122'] / (X_clean['F670'].abs() + 1.0)
    if 'F2582' in X_clean.columns and 'F2737' in X_clean.columns:
        X_clean['BANK_FE_UPI_TO_TOTAL_DEV_RATIO'] = X_clean['F2582'] / (X_clean['F2737'].abs() + 1.0)
    if 'F3887' in X_clean.columns and 'F3894' in X_clean.columns:
        X_clean['BANK_FE_TENURE_AGE_RATIO'] = X_clean['F3887'] / (X_clean['F3894'].abs() + 1.0)

    # Impute missing values with 0
    X_filled = X_clean.fillna(0)
    features_np = X_filled.values
    scaler = StandardScaler()
    features_scaled = scaler.fit_transform(features_np)

    # 3. Construct Similarity-based Graph Adjacency
    print("[2/6] Building similarity-based graph network...")
    X_norm = normalize(features_np, norm='l2', axis=1)
    sim_matrix = cosine_similarity(X_norm)
    
    # Connect nodes with cosine similarity > 0.99
    adj = (sim_matrix > 0.99).astype(float)
    # Clear self-loops temporarily for component clustering
    np.fill_diagonal(adj, 0)
    
    # Find connected components to split train/val/test without graph leakage
    n_components, groups = connected_components(csgraph=csr_matrix(adj), directed=False, return_labels=True)
    print(f" -> Found {n_components} isolated component groups across {len(groups)} nodes.")

    # Restore self-loops for GraphSAGE normalized adjacency
    np.fill_diagonal(adj, 1)
    
    # Normalized Adjacency: D^-1/2 A D^-1/2
    degree = np.sum(adj, axis=1)
    d_inv_sqrt = np.power(degree, -0.5, where=degree>0)
    d_inv_sqrt[degree == 0] = 0.0
    D_inv_sqrt = np.diag(d_inv_sqrt)
    adj_norm = np.dot(np.dot(D_inv_sqrt, adj), D_inv_sqrt)

    # Calculate static graph features (degree, fan-in/fan-out proxy)
    degrees = np.sum(adj > 0, axis=1) - 1 # exclude self-loop
    graph_feats = pd.DataFrame({
        'graph_degree': degrees,
        'graph_centrality': degrees / (len(degrees) - 1)
    })

    # 4. Leakage-Free Stratified Group Splitting (60% Train, 20% Val, 20% Test)
    # Split component groups rather than individual nodes
    unique_groups = np.unique(groups)
    group_targets = []
    for g in unique_groups:
        # Assign group target as the majority target of nodes in that group
        g_y = y[groups == g]
        group_targets.append(1 if np.mean(g_y) >= 0.5 else 0)
    group_targets = np.array(group_targets)

    # First split: 80% train+val, 20% test
    train_val_groups, test_groups, _, _ = train_test_split(
        unique_groups, group_targets, test_size=0.20, random_state=42, stratify=group_targets
    )
    # Second split: split train+val into 75% train (which is 60% of total) and 25% val (20% of total)
    train_val_targets = group_targets[np.isin(unique_groups, train_val_groups)]
    train_groups, val_groups, _, _ = train_test_split(
        train_val_groups, train_val_targets, test_size=0.25, random_state=42, stratify=train_val_targets
    )

    # Map groups back to node indices
    train_idx = np.where(np.isin(groups, train_groups))[0]
    val_idx = np.where(np.isin(groups, val_groups))[0]
    test_idx = np.where(np.isin(groups, test_groups))[0]

    print(f" -> Train nodes: {len(train_idx)}, Validation nodes: {len(val_idx)}, Test nodes: {len(test_idx)}")
    
    # 5. Train GNN (GraphSAGE)
    print("\n[3/6] Initializing and training experimental GraphSAGE model...")
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f" -> Using device: {device}")

    # Convert to torch tensors
    x_tensor = torch.FloatTensor(features_scaled).to(device)
    adj_tensor = torch.FloatTensor(adj_norm).to(device)
    y_tensor = torch.FloatTensor(y).to(device)

    # Initialize model
    in_feats = features_scaled.shape[1]
    hidden_feats = 16
    gnn_model = GraphSAGEModel(in_feats, hidden_feats, 1).to(device)
    optimizer = torch.optim.Adam(gnn_model.parameters(), lr=0.01, weight_decay=1e-4)
    criterion = nn.BCEWithLogitsLoss()

    # Semi-supervised node classification masks
    train_mask = torch.zeros(len(y), dtype=torch.bool).to(device)
    train_mask[train_idx] = True
    val_mask = torch.zeros(len(y), dtype=torch.bool).to(device)
    val_mask[val_idx] = True
    
    best_val_auc = 0.0
    best_model_state = None

    for epoch in range(100):
        gnn_model.train()
        optimizer.zero_grad()
        logits, _ = gnn_model(x_tensor, adj_tensor)
        
        # Calculate loss only on training mask nodes to prevent target leakage
        loss = criterion(logits[train_mask].squeeze(), y_tensor[train_mask])
        loss.backward()
        optimizer.step()

        # Evaluate on validation mask
        gnn_model.eval()
        with torch.no_grad():
            val_logits, _ = gnn_model(x_tensor, adj_tensor)
            val_probs = torch.sigmoid(val_logits[val_mask]).squeeze().cpu().numpy()
            y_val_np = y[val_idx]
            val_auc = compute_pr_auc(y_val_np, val_probs)
            
            if val_auc > best_val_auc:
                best_val_auc = val_auc
                best_model_state = gnn_model.state_dict().copy()

        if (epoch + 1) % 20 == 0:
            print(f"  Epoch {epoch+1}/100 | Loss: {loss.item():.4f} | Val PR-AUC: {val_auc:.4f}")

    # Load best model weight state
    gnn_model.load_state_dict(best_model_state)
    gnn_model.eval()
    
    # Extract GNN embeddings and test predictions
    with torch.no_grad():
        test_logits, full_embeddings = gnn_model(x_tensor, adj_tensor)
        test_probs_gnn = torch.sigmoid(test_logits[test_idx]).squeeze().cpu().numpy()
        embeddings_np = full_embeddings.cpu().numpy()

    # Evaluate pure GraphSAGE on test set
    y_test = y[test_idx]
    gnn_test_pred = (test_probs_gnn >= 0.5).astype(int)
    
    # 6. Benchmarking & Feature Fusion Models
    print("\n[4/6] Benchmarking comparison models on test split...")
    
    # Split features
    X_tr_xgb, X_te_xgb = X_clean.iloc[train_idx], X_clean.iloc[test_idx]
    y_tr_xgb, y_te_xgb = y[train_idx], y[test_idx]
    
    # Model A: Baseline XGBoost (no graph data)
    print(" -> Training Baseline XGBoost Classifier...")
    model_baseline = xgb.XGBClassifier(random_state=42)
    model_baseline.fit(X_tr_xgb, y_tr_xgb)
    probs_baseline = model_baseline.predict_proba(X_te_xgb)[:, 1]
    pred_baseline = (probs_baseline >= 0.5).astype(int)

    # Model B: XGBoost + Graph Features (degree, centrality)
    print(" -> Training XGBoost + Hand-crafted Graph Features...")
    X_clean_graph = pd.concat([X_clean, graph_feats], axis=1)
    X_tr_graph, X_te_graph = X_clean_graph.iloc[train_idx], X_clean_graph.iloc[test_idx]
    
    model_graph = xgb.XGBClassifier(random_state=42)
    model_graph.fit(X_tr_graph, y_tr_xgb)
    probs_graph = model_graph.predict_proba(X_te_graph)[:, 1]
    pred_graph = (probs_graph >= 0.5).astype(int)

    # Model C: XGBoost + GNN Embeddings (GraphSAGE representations)
    print(" -> Training XGBoost + GNN Node Embeddings...")
    gnn_cols = [f'GNN_EMB_{i}' for i in range(embeddings_np.shape[1])]
    df_embeddings = pd.DataFrame(embeddings_np, columns=gnn_cols)
    X_clean_emb = pd.concat([X_clean, df_embeddings], axis=1)
    X_tr_emb, X_te_emb = X_clean_emb.iloc[train_idx], X_clean_emb.iloc[test_idx]

    model_emb = xgb.XGBClassifier(random_state=42)
    model_emb.fit(X_tr_emb, y_tr_xgb)
    probs_emb = model_emb.predict_proba(X_te_emb)[:, 1]
    pred_emb = (probs_emb >= 0.5).astype(int)

    # 7. Metrics Compilation
    print("\n[5/6] Calculating validation metrics...")
    
    comparison_results = []
    
    # Approach 1: XGBoost Baseline
    comparison_results.append({
        'Model': 'XGBoost Baseline',
        'Precision': precision_score(y_te_xgb, pred_baseline),
        'Recall': recall_score(y_te_xgb, pred_baseline),
        'F1': f1_score(y_te_xgb, pred_baseline),
        'PR-AUC': compute_pr_auc(y_te_xgb, probs_baseline)
    })

    # Approach 2: Pure GraphSAGE GNN
    comparison_results.append({
        'Model': 'Pure GraphSAGE GNN',
        'Precision': precision_score(y_test, gnn_test_pred, zero_division=0),
        'Recall': recall_score(y_test, gnn_test_pred),
        'F1': f1_score(y_test, gnn_test_pred),
        'PR-AUC': compute_pr_auc(y_test, test_probs_gnn)
    })

    # Approach 3: XGBoost + Graph Features
    comparison_results.append({
        'Model': 'XGBoost + Graph Features',
        'Precision': precision_score(y_te_xgb, pred_graph),
        'Recall': recall_score(y_te_xgb, pred_graph),
        'F1': f1_score(y_te_xgb, pred_graph),
        'PR-AUC': compute_pr_auc(y_te_xgb, probs_graph)
    })

    # Approach 4: XGBoost + GNN Embeddings
    comparison_results.append({
        'Model': 'XGBoost + GNN Embeddings',
        'Precision': precision_score(y_te_xgb, pred_emb),
        'Recall': recall_score(y_te_xgb, pred_emb),
        'F1': f1_score(y_te_xgb, pred_emb),
        'PR-AUC': compute_pr_auc(y_te_xgb, probs_emb)
    })

    df_metrics = pd.DataFrame(comparison_results)
    
    print("\n======================================================================")
    print("                    EXPERIMENTAL PIPELINE COMPARISONS                 ")
    print("======================================================================")
    print(df_metrics.to_string(index=False))
    print("======================================================================\n")

    # 8. Save Metrics Report Data
    report_dict = {
        "train_size": len(train_idx),
        "val_size": len(val_idx),
        "test_size": len(test_idx),
        "gnn_epochs": 100,
        "metrics_comparison": comparison_results
    }
    
    with open('modeling/gnn_metrics_report.json', 'w') as f:
        json.dump(report_dict, f, indent=4)
    print("[6/6] Saved metrics comparison JSON to modeling/gnn_metrics_report.json.")

if __name__ == '__main__':
    main()
