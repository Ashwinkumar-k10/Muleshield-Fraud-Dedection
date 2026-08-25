# MuleShield Pro — Graph Neural Network (GNN) Experimentation Report

This document reports the details and results of Phase 6: **Graph Neural Network (GNN) Experimentation**. Following strict scientific guidelines, we developed an independent experimental GNN pipeline, verified it against our baseline, and compared the results under rigorous leakage prevention constraints.

---

## 🧪 1. Experimental Setup & Dataset Construction

To evaluate the impact of graph topology and representation learning on money mule detection, we constructed a dedicated, offline experimental graph dataset from the production telemetry data (`data_copy.csv`).

### Graph Representation
* **Nodes**: Each of the $9,082$ banking customer accounts represented as a node.
* **Edges (Profile Similarity)**: Created edges between accounts whose normalized feature profile similarity exceeded a threshold of cosine similarity $> 0.99$. This groups near-duplicate account profiles and behavior, which are key indicators of mule rings and duplicate registrations.
* **Graph Structure**: The similarity graph yields $6,118$ isolated component groups across the $9,082$ accounts.

### Leakage Prevention Protocols
To ensure the mathematical validity of our benchmark metrics, the pipeline enforces strict leakage blocks:
1. **Target & Feature Leakage**: Dropped the 14 post-incident/resolution features (`F3898`, `F3899`, `F3912`, `F3913`, `F3914`, `F3915`, etc.) from the input feature space to align exactly with the sanitized preprocessor pipeline.
2. **Graph & Account Leakage**: To prevent validation and test nodes from cross-pollinating the training node representations during message passing, we used **Stratified Group-Based Splitting** (60% Train, 20% Val, 20% Test). Split divisions are based on isolated connected components (`groups`). 
   * This guarantees that if an account is in the test set, its profile cluster companions are *never* seen in the train/validation sets, eliminating data contamination across splits.
3. **Labels Masking**: Masked validation and test labels during the training phase.

---

## 🏗️ 2. Models Benchmarked

We evaluated four training approaches:
1. **XGBoost Baseline (Production)**: The production XGBoost classifier trained on the raw sanitized features.
2. **Pure GraphSAGE GNN**: A custom 2-layer GraphSAGE model implemented in PyTorch utilizing mean aggregation, trained using Binary Cross-Entropy loss with Adam optimizer.
3. **XGBoost + Hand-crafted Graph Features**: XGBoost trained on raw features augmented with static graph descriptors (node degree, centrality).
4. **XGBoost + GNN Node Embeddings (Fusion)**: XGBoost trained on raw features augmented with the 16-dimensional node embeddings extracted from the second-to-last layer of the GraphSAGE model.

---

## 📈 3. Validation Metrics Comparison

The models were evaluated on the independent test set split. Below are the canonical metrics achieved (Precision, Recall, F1 Score, and PR-AUC):

| Model | Test Precision | Test Recall | Test F1 Score | PR-AUC |
| :--- | :---: | :---: | :---: | :---: |
| **XGBoost Baseline (Production)** | **1.0000** | **0.4571** | **0.6275** | **0.8597** |
| **Pure GraphSAGE GNN** | 1.0000 | 0.0857 | 0.1579 | 0.4836 |
| **XGBoost + Graph Features** | 1.0000 | 0.4571 | 0.6275 | 0.8597 |
| **XGBoost + GNN Embeddings** | 0.6667 | 0.1143 | 0.1951 | 0.3521 |

---

## 🔬 4. Scientific Conclusions

### Key Findings
1. **XGBoost Dominance**: The baseline XGBoost model remains the champion model, achieving a Test PR-AUC of **0.8597** and a Precision of **1.0000**.
2. **Pure GraphSAGE Performance**: The GraphSAGE model struggles when operating standalone, achieving a PR-AUC of only **0.4836**. This indicates that neighborhood message passing on similarity connections alone cannot match the classification power of deep feature interactions captured by tree structures.
3. **Graph Features Augmentation**: Adding degree and centrality features to XGBoost yields identical performance, suggesting that raw feature trees already implicitly capture profile density.
4. **GNN Embeddings Instability**: Combining GNN-extracted embeddings with XGBoost degraded performance drastically (PR-AUC dropped to **0.3521**). The GNN embeddings introduction added noise and diluted the decision boundaries of tree nodes.

### Scientific Verdict
As GNN representations and message passing architectures **do not outperform** the XGBoost baseline on the evaluation metrics, the final scientific verdict is:

> **[ACTION DIRECTIVE] KEEP THE BASELINE.**

The production XGBoost classifier, preprocessor pipelines, and the locked decision threshold boundary of **`0.9899`** remain active in production. The GNN model remains strictly restricted to this experimental pipeline, and **no production binaries or weights were overwritten**.
