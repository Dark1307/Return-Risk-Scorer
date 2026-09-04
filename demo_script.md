# 5-Minute Demo Video Script

**Track:** Razorpay Buildathon — AI Risk Manager
**Project:** Return-Risk Scorer

---

### Segment 1: Problem Framing (0:00 - 0:30)
**Visual:** Slide with problem statement or talking head.
**Narration:** 
"Hi, I'm presenting the Return-Risk Scorer. Indian e-commerce merchants lose massive margins to return abuse—wardrobing, empty-box claims, and serial COD returns. This isn't credit card fraud; it's post-purchase abuse. Because so many orders are Cash-on-Delivery, merchants lack a pre-dispatch signal to catch these bad actors before shipping costs are sunk. Our solution is a machine learning scorer that flags these orders at checkout, keeping a human in the loop."

### Segment 2: Architecture Walkthrough (0:30 - 1:30)
**Visual:** Show the Architecture Diagram (from README.md).
**Narration:**
"Here’s how it works. We built a LightGBM model trained on historical order patterns. When a new order arrives, our FastAPI service scores it in milliseconds. Instead of a black box, it uses SHAP explainers to extract the top three reasons *why* the order is risky. The model doesn’t auto-cancel orders; instead, it routes high and medium-risk orders to a Streamlit-based Ops Review Queue, allowing the Trust & Safety team to verify or route the order to prepaid-only."

### Segment 3: Live Demo (1:30 - 3:30)
**Visual:** Screen recording of the Streamlit UI and the terminal running FastAPI.
**Action:** 
1. Open the Streamlit app. Show the incoming queue of orders.
2. Click on a "Low Risk" order to show what a normal order looks like.
3. Click on a "High Risk" order (e.g., COD Wardrobing).
**Narration:**
"Let's look at the Ops Queue. Here is a live stream of orders being scored. This order was flagged as 'High Risk'. If we look at the SHAP reason codes, the model tells us exactly why: The customer has a historically high return rate, they are ordering in the 'fashion' category, and they chose Cash on Delivery. This is a classic wardrobing pattern. The Ops analyst can now click 'Route to Prepaid' or 'Hold for Verification', saving the merchant Rs. 200 in reverse logistics without falsely banning a legitimate customer."

### Segment 4: Metrics on Held-out Set (3:30 - 5:00)
**Visual:** Terminal showing the output of `python scripts/evaluate_model.py`.
**Narration:**
"Finally, accuracy isn't enough in risk management; we care about cost. On our held-out test set, the model achieved a recall of 73%. More importantly, we built a Business Cost Matrix. By tracking False Positives (where we might add friction to a good customer) versus True Positives (where we save the reverse pickup cost), we can tune the threshold to ensure the model is genuinely creating net-positive value for the merchant. Thank you for watching!"
