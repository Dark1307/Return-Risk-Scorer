from fastapi import FastAPI, HTTPException
import joblib
import pandas as pd
import shap
import os
from .schemas import OrderPayload, RiskResponse

app = FastAPI(title="Return-Risk Scorer API")

# Global variables for model and explainer
MODEL_PATH = "models/lgbm_model.pkl"
model = None
explainer = None

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
CATEGORICAL_FEATURES = ['item_category', 'payment_method']

@app.on_event("startup")
def load_model():
    global model, explainer
    if os.path.exists(MODEL_PATH):
        model = joblib.load(MODEL_PATH)
        # TreeExplainer is fast enough to initialize on startup
        explainer = shap.TreeExplainer(model)
        print("Model and SHAP explainer loaded successfully.")
    else:
        print(f"Warning: Model not found at {MODEL_PATH}. Please train the model first.")

@app.get("/")
def read_root():
    return {"message": "Return-Risk Scorer API is running"}

@app.post("/score", response_model=RiskResponse)
def score_order(order: OrderPayload):
    if model is None:
        raise HTTPException(status_code=503, detail="Model is not loaded.")
        
    # Feature engineering (replicate training steps)
    return_rate = order.past_returns / (order.past_orders + 1e-5)
    
    data = {
        'item_category': [order.item_category],
        'payment_method': [order.payment_method],
        'order_value': [order.order_value],
        'account_age_days': [order.account_age_days],
        'past_orders': [order.past_orders],
        'past_returns': [order.past_returns],
        'return_rate': [return_rate],
        'address_use_count': [order.address_use_count]
    }
    df = pd.DataFrame(data)[FEATURES]
    
    # Convert categorical variables
    for col in CATEGORICAL_FEATURES:
        df[col] = df[col].astype('category')
        
    # Get probability
    prob = model.predict_proba(df)[0, 1]
    
    # Determine risk bucket
    if prob >= 0.7:
        risk_bucket = "High Risk"
    elif prob >= 0.4:
        risk_bucket = "Medium Risk"
    else:
        risk_bucket = "Low Risk"
        
    # Get SHAP reason codes
    shap_values = explainer.shap_values(df)
    
    # SHAP values for LightGBM binary classification are a list of arrays (one for each class)
    # We want the values for the positive class (index 1)
    # Note: Depending on the shap and lightgbm versions, shap_values might be a single array or a list.
    if isinstance(shap_values, list):
        instance_shap = shap_values[1][0]
    else:
        instance_shap = shap_values[0]
        
    # Get top 3 features by absolute SHAP value
    feature_importance = [
        {"feature": FEATURES[i], "impact": float(instance_shap[i]), "value": str(df.iloc[0, i])}
        for i in range(len(FEATURES))
    ]
    # Sort by absolute impact descending
    feature_importance.sort(key=lambda x: abs(x["impact"]), reverse=True)
    top_reasons = feature_importance[:3]
    
    # Format reason codes for human readability
    formatted_reasons = []
    for reason in top_reasons:
        direction = "increased" if reason["impact"] > 0 else "decreased"
        formatted_reasons.append({
            "feature": reason["feature"],
            "description": f"{reason['feature']} ({reason['value']}) {direction} risk score."
        })
        
    return RiskResponse(
        order_id=order.order_id,
        risk_score=prob,
        risk_bucket=risk_bucket,
        reason_codes=formatted_reasons
    )
