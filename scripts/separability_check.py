import pandas as pd
import numpy as np
from sklearn.tree import DecisionTreeClassifier, plot_tree
from sklearn.metrics import accuracy_score

print("Loading data for separability check...")
df = pd.read_parquet('processed_data.parquet')
y = df['F3924']
X = df.drop(columns=['F3924'])

print("\n--- 3. SINGLE-FEATURE / SMALL-COMBO SEPARABILITY CHECK ---")
# Let's train a depth 1 decision tree to find single best feature
dt_depth1 = DecisionTreeClassifier(max_depth=1, random_state=42)
dt_depth1.fit(X, y)

feature_idx = dt_depth1.tree_.feature[0]
threshold = dt_depth1.tree_.threshold[0]
feature_name = X.columns[feature_idx]

preds = dt_depth1.predict(X)
acc = accuracy_score(y, preds)
print(f"Best Single Feature: {feature_name} at threshold {threshold:.4f}")
print(f"Accuracy with just this feature: {acc:.4%}")

# Depth 2 decision tree
dt_depth2 = DecisionTreeClassifier(max_depth=2, random_state=42)
dt_depth2.fit(X, y)
acc_2 = accuracy_score(y, dt_depth2.predict(X))
print(f"Accuracy with max depth 2: {acc_2:.4%}")

print("\nExample rows separated by single feature (threshold):")
left_mask = X[feature_name] <= threshold
right_mask = X[feature_name] > threshold

print(f"\n--- 10 Examples where {feature_name} <= {threshold:.4f} ---")
print(y[left_mask].value_counts())
print(df[left_mask].head(10)[[feature_name, 'F3924']].to_string())

print(f"\n--- 10 Examples where {feature_name} > {threshold:.4f} ---")
print(y[right_mask].value_counts())
print(df[right_mask].head(10)[[feature_name, 'F3924']].to_string())

# Print all feature importances from depth 2 just to see
imps = dt_depth2.feature_importances_
top_idx = np.argsort(imps)[::-1][:3]
print(f"\nTop features from depth 2 tree: {[X.columns[i] for i in top_idx]}")
