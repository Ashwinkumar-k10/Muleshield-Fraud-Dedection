# 🕸️ 19 — MULE NETWORK RING TOPOLOGY (ILLUSTRATIVE DEMO)

---

## 1. Important Transparency Disclaimer

> [!NOTE]
> **SIMULATED DEMONSTRATION FEATURE:**  
> The raw dataset (`data_copy.csv`) consists of isolated account profile rows without explicit counterparty transaction linkage columns (sender/receiver account IDs).  
>  
> The **Mule Network Ring Topology** tab (Tab 3) is an **ILLUSTRATIVE SYNTHETIC DEMONSTRATION** designed to show hackathon judges how graph network analytics would visually track multi-hop fund-layering syndicates when counterparty transaction graph data is available in production.

---

## 2. Simulated Network Ring Topology Structure

The interactive canvas uses **Vis.js Network** (`vis-network.min.js`) to render an 8-node directed graph depicting a classic 3-hop fund-layering scheme:

```
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│ Victim #1001    │ ───►  │ Feeder Mule     │ ───►  │ Critical Mules  │ ───►  │ Cash-Out        │ ───►  │ Drain Sinks     │
│ (Phishing Scam) │ ₹600k │ #9001           │ ₹200k │ #9003, #9004,   │ RTGS  │ Aggregator Hub  │ Drain │ ATM-402 &       │
│                 │  UPI  │ (Pass-Through)  │ IMPS  │ #9006           │       │ #9099           │       │ Crypto USDT     │
└─────────────────┘       └─────────────────┘       └─────────────────┘       └─────────────────┘       └─────────────────┘
```

---

## 3. Node & Edge Breakdown

* **Node 1 (`Victim #1001`):** Phishing victim account originating illicit funds ($\xrightarrow{\text{₹600k UPI transfer}}$).
* **Node 2 (`Feeder Mule #9001`):** Primary entry mule splitting funds ($\xrightarrow{\text{₹200k IMPS splits}}$).
* **Nodes 3, 4, 5 (`Critical Mules #9003, #9004, #9006`):** Flagged critical layering accounts ($\xrightarrow{\text{RTGS transfers}}$).
* **Node 6 (`Aggregator Hub #9099`):** Central cash-out pooling account.
* **Nodes 7 & 8 (`ATM Cash Out` & `Crypto USDT`):** Final off-ramp exit sinks.

---

## 4. UI Implementation Details

* **Interactive Controls:** Drag-and-drop node movement, dynamic physics stabilization, zoom controls, and click-to-inspect node tooltips.
* **Warning Badge:** Displays a yellow notification tag:  
  `<span class="badge">Illustrative Example — Simulated Data</span>`
