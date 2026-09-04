import pandas as pd
import numpy as np
import os
import argparse
from datetime import datetime, timedelta

def generate_data(n_samples=10000):
    np.random.seed(42)
    
    # Base features
    customer_ids = np.random.randint(1000, 5000, n_samples)
    order_ids = np.arange(100000, 100000 + n_samples)
    
    start_date = datetime(2026, 1, 1)
    order_dates = [start_date + timedelta(days=np.random.randint(0, 180)) for _ in range(n_samples)]
    
    categories = ['fashion', 'electronics', 'beauty', 'home']
    item_category = np.random.choice(categories, n_samples, p=[0.5, 0.2, 0.2, 0.1])
    
    payment_methods = ['COD', 'Prepaid']
    payment_method = np.random.choice(payment_methods, n_samples, p=[0.6, 0.4])
    
    order_value = np.random.lognormal(mean=7, sigma=1, size=n_samples).astype(int)
    
    account_age_days = np.random.randint(0, 1000, n_samples)
    
    # Historical stats per customer (simplified approximation)
    past_orders = np.random.poisson(lam=3, size=n_samples)
    past_returns = np.random.binomial(past_orders, p=0.1)
    
    address_hashes = np.random.randint(1, 2000, n_samples)
    
    df = pd.DataFrame({
        'order_id': order_ids,
        'customer_id': customer_ids,
        'order_date': order_dates,
        'item_category': item_category,
        'payment_method': payment_method,
        'order_value': order_value,
        'account_age_days': account_age_days,
        'past_orders': past_orders,
        'past_returns': past_returns,
        'shipping_address_hash': address_hashes
    })
    
    # Feature Engineering (what the model will see)
    df['return_rate'] = df['past_returns'] / (df['past_orders'] + 1e-5)
    
    # Base return probability
    base_prob = 0.05
    
    # Inject Abuse Pattern 1: COD Wardrobing
    # High return rate historically, buying fashion, using COD
    is_wardrobing = (df['return_rate'] > 0.5) & (df['item_category'] == 'fashion') & (df['payment_method'] == 'COD')
    
    # Inject Abuse Pattern 2: Velocity / Shared Address Abuse
    # New account, high value, address shared with many others
    addr_counts = df['shipping_address_hash'].value_counts()
    df['address_use_count'] = df['shipping_address_hash'].map(addr_counts)
    
    is_velocity_abuse = (df['account_age_days'] < 7) & (df['order_value'] > 5000) & (df['address_use_count'] > 3)
    
    # Combine probabilities
    prob = np.full(n_samples, base_prob)
    prob[is_wardrobing] = 0.85
    prob[is_velocity_abuse] = 0.75
    
    # Add some legitimate returns
    prob += np.where(df['item_category'] == 'fashion', 0.1, 0)
    
    prob = np.clip(prob, 0, 1)
    
    # Generate labels
    df['is_returned'] = np.random.binomial(1, prob)
    
    return df

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=str, default='data/synthetic_orders.csv')
    parser.add_argument('--samples', type=int, default=20000)
    args = parser.parse_args()
    
    print(f"Generating {args.samples} synthetic orders...")
    df = generate_data(args.samples)
    
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    df.to_csv(args.output, index=False)
    
    print(f"Saved to {args.output}")
    print(f"Overall return rate: {df['is_returned'].mean():.2%}")
    print(df.head())
