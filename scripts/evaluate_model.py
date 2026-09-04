import pandas as pd
import joblib
import argparse
from sklearn.metrics import precision_score, recall_score, average_precision_score, confusion_matrix
import numpy as np

def evaluate(test_data_path, model_path):
    print(f"Loading test data from {test_data_path}...")
    df = pd.read_csv(test_data_path)
    
    # Convert categorical to category type
    for col in ['item_category', 'payment_method']:
        df[col] = df[col].astype('category')
        
    X_test = df.drop(columns=['is_returned'])
    y_test = df['is_returned']
    
    model = joblib.load(model_path)
    
    # Get probabilities
    y_prob = model.predict_proba(X_test)[:, 1]
    
    # Evaluate at threshold 0.5 (or could be tuned)
    threshold = 0.5
    y_pred = (y_prob >= threshold).astype(int)
    
    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    pr_auc = average_precision_score(y_test, y_prob)
    cm = confusion_matrix(y_test, y_pred)
    
    print("\n--- Model Evaluation ---")
    print(f"Precision: {precision:.4f}")
    print(f"Recall:    {recall:.4f}")
    print(f"PR-AUC:    {pr_auc:.4f}")
    print("\nConfusion Matrix:")
    print(f"TN: {cm[0][0]} | FP: {cm[0][1]}")
    print(f"FN: {cm[1][0]} | TP: {cm[1][1]}")
    
    # Cost Table calculation
    # Assumptions: 
    # Average margin on a valid order = Rs. 500
    # Average cost of a reverse pickup / return = Rs. 200
    
    avg_margin = 500
    avg_return_cost = 200
    
    # False Positive (Predicted abuse, actually good): We might cancel or add friction, potentially losing the margin.
    # False Negative (Predicted good, actually abuse): We fulfill it and incur the return cost.
    # True Positive (Predicted abuse, actually abuse): We block/add friction and save the return cost.
    
    fp_cost = cm[0][1] * avg_margin
    saved_return_cost = cm[1][1] * avg_return_cost
    net_savings = saved_return_cost - fp_cost
    
    print("\n--- Business Cost Analysis ---")
    print(f"Cost of False Positives (lost margin): Rs. {fp_cost}")
    print(f"Saved Return Costs (from True Positives): Rs. {saved_return_cost}")
    print(f"Net Value Created: Rs. {net_savings}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--test_data', type=str, default='data/synthetic_orders_test.csv')
    parser.add_argument('--model', type=str, default='models/lgbm_model.pkl')
    args = parser.parse_args()
    
    evaluate(args.test_data, args.model)
