from pydantic import BaseModel, Field

class OrderPayload(BaseModel):
    order_id: int = Field(..., description="Unique order ID")
    customer_id: int = Field(..., description="Unique customer ID")
    item_category: str = Field(..., description="Category of the item (e.g., fashion, electronics)")
    payment_method: str = Field(..., description="Payment method (COD, Prepaid)")
    order_value: float = Field(..., description="Value of the order")
    account_age_days: int = Field(..., description="Age of the customer account in days")
    past_orders: int = Field(..., description="Number of past orders by the customer")
    past_returns: int = Field(..., description="Number of past returns by the customer")
    address_use_count: int = Field(..., description="Number of times this address has been used across all accounts")

class RiskResponse(BaseModel):
    order_id: int
    risk_score: float = Field(..., description="Probability of return (0.0 to 1.0)")
    risk_bucket: str = Field(..., description="Low, Medium, or High Risk")
    reason_codes: list[dict] = Field(..., description="Top contributing factors based on SHAP")
