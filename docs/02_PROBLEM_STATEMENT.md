# 🎯 02 — PROBLEM STATEMENT & SCOPE ALIGNMENT

---

## 1. Official PSB CyberShield Problem Statement

> **Problem Statement:**  
> *"Developing a solution having AI/ML capabilities for detecting suspicious transactions and mule accounts by ingesting financial transactions and/or fraud monitoring solution alerts and/or Transaction Monitoring System alerts and government cyber fraud alerts/tickets and preventing circulation of fraudulent proceeds through mule accounts.*  
>  
> *The solution should consume real-time regulatory inputs/feeds and cross-channel bank data."*

---

## 2. What the Organizers Expect from a Solution

1. **Automated AI/ML Detection:** Replace manual rule-writing with machine learning models capable of identifying complex, non-linear fraud patterns across transaction streams.
2. **Cross-Channel Integration:** Analyze data spanning digital banking (UPI, IMPS, NEFT, RTGS), cash/ATM withdrawals, and account demographic profiles.
3. **Mule Account Identification:** Differentiate between legitimate high-activity accounts and mule accounts used for fund layering and cash-out.
4. **Actionable Risk Mitigation:** Provide real-time risk scores, explainable risk drivers, and mechanisms to prevent circulation of illicit funds.
5. **Generalization to Unseen Data:** Perform reliably on hidden, un-shared validation datasets during hackathon evaluation.

---

## 3. Scope Distinction: Implemented Prototype vs. Production Vision

To maintain strict technical honesty, the project scope is clearly categorized across three tiers:

| Dimension | Problem Statement Requirement | Currently Implemented Prototype (MuleShield PRO) | Future Production Extensions |
| :--- | :--- | :--- | :--- |
| **ML Engine** | AI/ML suspicious transaction & mule detection | **XGBoost Classifier** (`tree_method='hist'`) trained on 6,820 sanitized features ($0.8807$ PR-AUC on 5-Fold Group CV). | Ensemble GNN (Graph Neural Network) for direct graph node classification. |
| **Data Ingestion** | Ingestion of cross-channel bank transaction data | **Batch CSV / REST JSON API** ingesting 9,082 account profiles ($3,924$ raw input features). | Apache Kafka / Spark Streaming pipeline for live microsecond transaction ingestion. |
| **Regulatory Feeds** | Consume real-time regulatory inputs/feeds | **Integrated Regulatory Intelligence Tab** searching account matches against simulated I4C, CERT-In, and RBI databases. | Live webhook integration with I4C (Indian Cyber Crime Coordination Centre) API. |
| **Network Analytics** | Trace multi-hop mule fund layering | **Interactive Vis.js Mule Ring Topology Tab** illustrating a 3-hop simulated fund layering ring. | Neo4j / NetworkX graph engine querying live counterparty transaction edges. |
| **CBS Account Action** | Prevent circulation of proceeds | **Simulated CBS Debit Freeze Action Button** generating audit log (`CBS-FRZ-2026-9003-8492`). | ISO 20022 REST API integration with Core Banking System (Finacle / BaNCS). |
| **STR Filing** | Compliance reporting | **Automated FIU-IND STR Draft Generator** producing formatted legal text filings. | Automated XML export & direct submission to FIU-IND FINnet gateway. |

---

## 4. Evaluation Context Disclaimer

* **Training & Internal CV Dataset:** The dataset supplied (`data_copy.csv` — 9,082 rows) was used for model exploration, leakage sanitization, feature engineering, and 5-Fold Group-Aware Cross-Validation.
* **Hidden Validation Dataset:** The organizers will evaluate submitted models against an **unseen hidden validation dataset**. All ML choices in MuleShield PRO prioritize generalization and zero-leakage to ensure optimal performance on this un-shared test set.
