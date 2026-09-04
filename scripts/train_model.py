import pandas as pd
import lightgbm as lgb
from sklearn.model_selection import train_test_split
import joblib
import os
import argparse

FEATURES = [
    'item_category',
    'payment_method',
    'order_value',
    'account_age_days',
    'past_orders',
    'past_returns',
    'return_rate',
    'address_use_count'
]
TARGET = 'is_returned'
CATEGORICAL_FEATURES = ['item_category', 'payment_method']

def train(data_path, model_path):
    print(f"Loading data from {data_path}...")
    df = pd.read_csv(data_path)
    
    # Convert categorical to category type for LightGBM
    for col in CATEGORICAL_FEATURES:
        df[col] = df[col].astype('category')
        
    X = df[FEATURES]
    y = df[TARGET]
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Save test set for evaluation
    test_df = X_test.copy()
    test_df[TARGET] = y_test
    test_path = data_path.replace('.csv', '_test.csv')
    test_df.to_csv(test_path, index=False)
    print(f"Saved test set to {test_path}")
    
    print("Training LightGBM model...")
    model = lgb.LGBMClassifier(
        n_estimators=100,
        learning_rate=0.05,
        max_depth=5,
        random_state=42,
        class_weight='balanced' # Handle imbalance
    )
    
    model.fit(
        X_train, y_train,
        eval_set=[(X_test, y_test)],
        eval_metric='auc',
        callbacks=[lgb.early_stopping(10), lgb.log_evaluation(10)]
    )
    
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    joblib.dump(model, model_path)
    print(f"Model saved to {model_path}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--data', type=str, default='data/synthetic_orders.csv')
    parser.add_argument('--output', type=str, default='models/lgbm_model.pkl')
    args = parser.parse_args()
    
    train(args.data, args.output)
