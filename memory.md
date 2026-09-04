# Project Memory

## Current State
- **Status:** Initialized project structure and stored PRD.
- **Next Steps:** Review and approve the implementation plan to begin building the components (Data generation, ML training, FastAPI backend, UI).

## Product Requirements Document
**Return-Risk Scorer for E-Commerce Merchants**
**Track:** Razorpay Buildathon — AI Risk Manager
**Author:** [Your Name], Product Manager
**Date:** September 3, 2026
**Status:** Draft for submission

### 1. Problem Statement
Indian e-commerce merchants lose a measurable slice of revenue to returns — not the healthy kind (defective item, wrong size), but the costly kind: wardrobing (wear-and-return), empty-box/item-swap claims, serial returners who order multiple variants and keep one, and COD orders placed with no real intent to accept delivery. Industry return rates for fashion and lifestyle categories on Indian marketplaces commonly run 15-30%, and a meaningful share of that is abuse rather than genuine dissatisfaction.

This matters now for three converging reasons:
*   **COD-heavy checkout mix.** A large share of Indian e-commerce orders are still COD.
*   **AI-enabled abuse is scaling.** Return-abuse patterns are becoming easier to run at volume.
*   **Margin is already thin.** A return-abuse rate of even 3-5% of orders can erase a significant share of net margin.

**Who it hurts:** D2C and marketplace-adjacent merchants processing through Razorpay, and specifically their ops and risk teams, who currently have no systematic, pre-dispatch signal to flag high-risk orders before shipping cost is sunk.

### 2. Goals & Non-Goals

**Goals**
*   Score every incoming order for return risk at or near checkout/order-confirmation time.
*   Surface a transparent, auditable risk score with the top contributing factors (SHAP values).
*   Give merchant ops teams a workflow lever (e.g., route high-risk COD orders to prepaid-only).
*   Report precision, recall, and false-positive cost on a held-out test set.

**Non-Goals**
*   Not a payment-fraud/chargeback detector.
*   Not an auto-decline or auto-cancel system (keeps human-in-the-loop).
*   Not a customer identity/KYC system.
*   Explicitly not offense-capable.

### 3. Target Users & Use Cases
*   **Primary users:** Merchant Ops Analyst, Risk/Trust & Safety Lead, Support Agent.
*   **Scenario A:** COD wardrobing pattern (serial returner). Ops routes to "prepaid-only".
*   **Scenario B:** New-account velocity abuse (shared address). System flags for manual verification.

### 4. Deliverables
*   Evaluation script producing precision, recall, PR-AUC, confusion matrix, and false-positive-cost table.
*   FastAPI scoring endpoint returning risk bucket + top 3 SHAP reason codes.
*   Minimal ops-review UI (single-page order queue).
*   Architecture diagram.
*   5-minute demo video.

**Out of Scope:** Real Razorpay prod data, Prod-grade auth, CI pipeline, Mobile UI.

### 5. Timeline / Milestones (Sept 3 - Sept 5)
*   **Day 1 (Sept 3):** Finalize features, build synthetic data generator, train first LightGBM baseline.
*   **Day 2 (Sept 4 - Today):** Build FastAPI scoring service, minimal ops-review UI, finalize evaluation script.
*   **Day 3 (Sept 5):** Architecture diagram, README, repo cleanup, record demo video, submit.
