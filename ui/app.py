import streamlit as st
import requests
import random
import pandas as pd
import time

st.set_page_config(page_title="Ops Review Queue", layout="wide")

st.title("Ops Review Queue: Return-Risk Scorer")
st.markdown("Review high-risk orders before dispatch.")

API_URL = "http://localhost:8001/score"

# Mock function to generate incoming orders
def get_incoming_orders():
    orders = []
    # Generate some regular orders and some risky ones
    for i in range(5):
        is_risky = random.choice([True, False])
        if is_risky:
            orders.append({
                "order_id": random.randint(100000, 999999),
                "customer_id": random.randint(1000, 9999),
                "item_category": "fashion",
                "payment_method": "COD",
                "order_value": random.randint(3000, 10000),
                "account_age_days": random.randint(1, 5),
                "past_orders": random.randint(0, 2),
                "past_returns": random.randint(0, 1),
                "address_use_count": random.randint(4, 10)
            })
        else:
            orders.append({
                "order_id": random.randint(100000, 999999),
                "customer_id": random.randint(1000, 9999),
                "item_category": random.choice(["electronics", "beauty", "home"]),
                "payment_method": "Prepaid",
                "order_value": random.randint(500, 2000),
                "account_age_days": random.randint(100, 500),
                "past_orders": random.randint(5, 20),
                "past_returns": random.randint(0, 1),
                "address_use_count": 1
            })
    return orders

if 'orders' not in st.session_state:
    st.session_state.orders = get_incoming_orders()

if st.button("Fetch New Orders"):
    st.session_state.orders = get_incoming_orders()

for order in st.session_state.orders:
    with st.container():
        st.markdown(f"### Order #{order['order_id']}")
        
        col1, col2 = st.columns([1, 2])
        with col1:
            st.json(order)
            
        with col2:
            try:
                response = requests.post(API_URL, json=order)
                if response.status_code == 200:
                    result = response.json()
                    
                    # Style based on risk
                    color = "red" if result['risk_bucket'] == "High Risk" else "orange" if result['risk_bucket'] == "Medium Risk" else "green"
                    st.markdown(f"**Risk Score:** <span style='color:{color}'>{result['risk_score']:.2%} ({result['risk_bucket']})</span>", unsafe_allow_html=True)
                    
                    st.markdown("**Top Risk Factors:**")
                    for reason in result['reason_codes']:
                        st.markdown(f"- {reason['description']}")
                        
                    # Ops actions
                    action_col1, action_col2, action_col3 = st.columns(3)
                    with action_col1:
                        st.button("Ship (Ignore Risk)", key=f"ship_{order['order_id']}")
                    with action_col2:
                        st.button("Hold for Verification", key=f"hold_{order['order_id']}")
                    with action_col3:
                        st.button("Route to Prepaid", key=f"route_{order['order_id']}")
                        
                else:
                    st.error(f"Error from API: {response.text}")
            except requests.exceptions.ConnectionError:
                st.error("Cannot connect to API. Is FastAPI running on port 8000?")
                
        st.markdown("---")
