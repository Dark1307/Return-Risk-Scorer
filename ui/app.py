import streamlit as st
import requests
import random
import pandas as pd
import time

st.set_page_config(page_title="Risk Operations Dashboard", page_icon="🛡️", layout="wide")

API_URL = "http://localhost:8001/score"

# ---------------------------------------------------------
# CSS & Styling for Professional Look
# ---------------------------------------------------------
st.markdown("""
<style>
    .metric-container {
        border: 1px solid #333;
        border-radius: 5px;
        padding: 10px;
        text-align: center;
        background-color: #1E1E1E;
    }
    .metric-value {
        font-size: 24px;
        font-weight: bold;
    }
    .metric-label {
        font-size: 12px;
        color: #888;
        text-transform: uppercase;
    }
    .high-risk { color: #ff4b4b; }
    .medium-risk { color: #ffa726; }
    .low-risk { color: #4caf50; }
    
    .risk-score-value {
        font-size: 32px;
        font-weight: 700;
        margin-bottom: 0px;
    }
    .action-header {
        font-size: 14px;
        color: #888;
        margin-bottom: 8px;
    }
    
    /* Hide top padding for cleaner dashboard look */
    .block-container {
        padding-top: 2rem;
    }
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------
# Mock Data Generation
# ---------------------------------------------------------
def get_incoming_orders():
    orders = []
    # Generate some regular orders and some risky ones
    for i in range(15):
        is_risky = random.choice([True, False, False])
        if is_risky:
            orders.append({
                "order_id": random.randint(500000, 599999),
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
                "order_id": random.randint(500000, 599999),
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
    st.session_state.scored_orders = {}

# ---------------------------------------------------------
# Helper Functions
# ---------------------------------------------------------
@st.cache_data(ttl=60)
def score_order(order):
    try:
        response = requests.post(API_URL, json=order, timeout=5)
        if response.status_code == 200:
            return response.json(), None
        return None, f"API Error: {response.text}"
    except requests.exceptions.RequestException as e:
        return None, "Server unavailable. Is FastAPI running?"

def handle_action(order_id, action_name):
    # Mock action handler
    st.session_state.orders = [o for o in st.session_state.orders if o['order_id'] != order_id]
    st.toast(f"Order #{order_id} marked as: {action_name}", icon="✅")

# ---------------------------------------------------------
# Pre-fetch scores for statistics
# ---------------------------------------------------------
with st.spinner("Loading queue data..."):
    for order in st.session_state.orders:
        oid = order['order_id']
        if oid not in st.session_state.scored_orders:
            score_res, err = score_order(order)
            st.session_state.scored_orders[oid] = {"result": score_res, "error": err}

# ---------------------------------------------------------
# Header & Operations Dashboard
# ---------------------------------------------------------
st.markdown("<h1>Risk Operations</h1>", unsafe_allow_html=True)
st.markdown("### Return-Risk Review Queue")

# Calculate stats
pending_count = len(st.session_state.orders)
high_count = sum(1 for o in st.session_state.orders if st.session_state.scored_orders[o['order_id']].get('result') and st.session_state.scored_orders[o['order_id']]['result']['risk_bucket'] == "High Risk")
medium_count = sum(1 for o in st.session_state.orders if st.session_state.scored_orders[o['order_id']].get('result') and st.session_state.scored_orders[o['order_id']]['result']['risk_bucket'] == "Medium Risk")
low_count = sum(1 for o in st.session_state.orders if st.session_state.scored_orders[o['order_id']].get('result') and st.session_state.scored_orders[o['order_id']]['result']['risk_bucket'] == "Low Risk")

mcol1, mcol2, mcol3, mcol4, mcol_space = st.columns([1, 1, 1, 1, 2])
with mcol1:
    st.markdown(f"<div class='metric-container'><div class='metric-value'>{pending_count}</div><div class='metric-label'>Pending Review</div></div>", unsafe_allow_html=True)
with mcol2:
    st.markdown(f"<div class='metric-container'><div class='metric-value high-risk'>{high_count}</div><div class='metric-label'>High Risk</div></div>", unsafe_allow_html=True)
with mcol3:
    st.markdown(f"<div class='metric-container'><div class='metric-value medium-risk'>{medium_count}</div><div class='metric-label'>Medium Risk</div></div>", unsafe_allow_html=True)
with mcol4:
    st.markdown(f"<div class='metric-container'><div class='metric-value low-risk'>{low_count}</div><div class='metric-label'>Low Risk</div></div>", unsafe_allow_html=True)

st.write("") # Spacing

# Controls
ctrl1, ctrl2, ctrl3, ctrl4 = st.columns([2, 2, 2, 1])
with ctrl1:
    search_query = st.text_input("🔍 Search Order or Customer ID", "")
with ctrl2:
    risk_filter = st.selectbox("Risk Filter", ["All", "High Risk", "Medium Risk", "Low Risk"])
with ctrl3:
    sort_by = st.selectbox("Sort By", ["Highest Risk First", "Newest First"])
with ctrl4:
    st.write("") # Alignment
    if st.button("🔄 Refresh Queue", use_container_width=True):
        st.session_state.orders = get_incoming_orders()
        st.session_state.scored_orders = {}
        st.rerun()

st.divider()

# ---------------------------------------------------------
# Filter & Sort Logic
# ---------------------------------------------------------
display_orders = st.session_state.orders.copy()

if search_query:
    display_orders = [o for o in display_orders if str(o['order_id']).startswith(search_query) or str(o['customer_id']).startswith(search_query)]

if risk_filter != "All":
    display_orders = [o for o in display_orders if st.session_state.scored_orders[o['order_id']].get('result') and st.session_state.scored_orders[o['order_id']]['result']['risk_bucket'] == risk_filter]

if sort_by == "Highest Risk First":
    display_orders.sort(key=lambda o: st.session_state.scored_orders[o['order_id']]['result']['risk_score'] if st.session_state.scored_orders[o['order_id']].get('result') else 0, reverse=True)


# ---------------------------------------------------------
# Review Queue View
# ---------------------------------------------------------
if not display_orders:
    st.info("No orders in queue matching your criteria.")
else:
    for order in display_orders:
        oid = order['order_id']
        scored_data = st.session_state.scored_orders[oid]
        result = scored_data.get('result')
        err = scored_data.get('error')

        with st.container():
            if err:
                st.error(f"Order #{oid}: {err}")
                continue
                
            if not result:
                continue

            risk_bucket = result['risk_bucket']
            risk_score = result['risk_score']
            
            risk_color_class = "high-risk" if risk_bucket == "High Risk" else "medium-risk" if risk_bucket == "Medium Risk" else "low-risk"
            
            # --- Main Card ---
            col_id, col_info, col_risk, col_action = st.columns([1.5, 2, 2.5, 2.5])
            
            with col_id:
                st.markdown(f"#### Order #{oid}")
                st.markdown(f"**Customer ID:** {order['customer_id']}")
                st.markdown(f"**Date:** Just now")
                
            with col_info:
                st.markdown(f"**Value:** ₹{order['order_value']:,}")
                st.markdown(f"**Method:** {order['payment_method']}")
                st.markdown(f"**Category:** {order['item_category'].title()}")
                
            with col_risk:
                st.markdown(f"<div class='risk-score-value {risk_color_class}'>{risk_score:.2%}</div>", unsafe_allow_html=True)
                st.markdown(f"<strong class='{risk_color_class}'>{risk_bucket.upper()}</strong>", unsafe_allow_html=True)
                st.progress(risk_score)
                
            with col_action:
                # Recommended action logic
                rec_action = "Approve & Ship"
                if risk_bucket == "High Risk":
                    rec_action = "Hold for Verification"
                elif risk_bucket == "Medium Risk" and order['payment_method'] == "COD":
                    rec_action = "Route to Prepaid"
                
                st.markdown(f"<div class='action-header'>Recommended Action</div>", unsafe_allow_html=True)
                st.markdown(f"**[ {rec_action} ]**")
                
                # Operational actions
                act1, act2, act3 = st.columns(3)
                with act1:
                    st.button("Approve & Ship", key=f"ship_{oid}", on_click=handle_action, args=(oid, "Approve & Ship"), use_container_width=True)
                with act2:
                    st.button("Hold & Verify", key=f"hold_{oid}", on_click=handle_action, args=(oid, "Hold for Verification"), use_container_width=True)
                with act3:
                    st.button("Route to Prepaid", key=f"route_{oid}", on_click=handle_action, args=(oid, "Route to Prepaid"), use_container_width=True, disabled=(order['payment_method'] != "COD"))
            
            # --- Expanded Details ---
            with st.expander("View Order Data & Risk Explanation"):
                tab1, tab2 = st.tabs(["Risk Explanation", "Order Details"])
                
                with tab1:
                    st.markdown("##### Why this order was flagged")
                    if not result['reason_codes']:
                        st.write("No major risk factors detected.")
                    else:
                        for reason in result['reason_codes']:
                            desc = reason['description']
                            feature = reason['feature']
                            
                            # Clean up the description
                            if "increased" in desc.lower():
                                arrow = "↑"
                                color = "#ff4b4b"
                            else:
                                arrow = "↓"
                                color = "#4caf50"
                                
                            st.markdown(f"<span style='color:{color}; font-weight:bold;'>{arrow} {feature.replace('_', ' ').title()}</span>", unsafe_allow_html=True)
                            st.markdown(f"<span style='color:#ccc;'>{desc.capitalize()}</span>", unsafe_allow_html=True)
                            st.write("")
                
                with tab2:
                    dcol1, dcol2, dcol3 = st.columns(3)
                    with dcol1:
                        st.markdown("**Order Information**")
                        st.write(f"- Order Value: ₹{order['order_value']:,}")
                        st.write(f"- Payment: {order['payment_method']}")
                        st.write(f"- Category: {order['item_category'].title()}")
                    with dcol2:
                        st.markdown("**Customer Signals**")
                        st.write(f"- Account Age: {order['account_age_days']} days")
                        st.write(f"- Past Orders: {order['past_orders']}")
                        st.write(f"- Past Returns: {order['past_returns']}")
                    with dcol3:
                        st.markdown("**Risk Signals**")
                        st.write(f"- Address Uses: {order['address_use_count']}")
                        
                    st.divider()
                    st.markdown("**Model Information**")
                    st.caption("Model Version: Future Release • Prediction Time: Real-time • Engine: LightGBM")
                    
            st.markdown("<hr style='margin-top: 10px; margin-bottom: 20px; border-color: #333;'>", unsafe_allow_html=True)
