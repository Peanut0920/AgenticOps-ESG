# AgenticOps-ESG

**An Autonomous Multi-Agent System for IT Infrastructure Right-Sizing, Predictive Refresh Cycles, and Regulatory ESG Reporting (Bursa Malaysia, MCMC, GRI, SASB)**

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue.svg" alt="Python Version">
  <img src="https://img.shields.io/badge/FastAPI-0.115+-green.svg" alt="FastAPI">
  <img src="https://img.shields.io/badge/LangGraph-0.2+-orange.svg" alt="LangGraph">
  <img src="https://img.shields.io/badge/Tailwind-CSS-06B6D4.svg" alt="Tailwind">
  <img src="https://img.shields.io/badge/Status-Production_Ready-brightgreen.svg" alt="Status">
</p>

---

## 📋 Overview

**AgenticOps-ESG** is a production-ready, LLM-driven multi-agent system that operationalizes Environmental, Social, and Governance (ESG) principles within enterprise IT infrastructure. 

Unlike static monitoring tools, this system acts as a **"digital sustainability officer"** for your data center. It autonomously:

- **Dynamically resizes** over-provisioned VMs to reduce energy waste (Scope 2).
- **Predicts optimal hardware refresh windows** by comparing operational carbon waste against embodied carbon.
- **Generates audit-ready reports** aligned with **Bursa Malaysia**, **MCMC**, **GRI**, and **SASB** standards—bridging the gap between Site Reliability Engineering (SRE) and corporate sustainability mandates.

---

## 🚀 Key Features

| Feature | Description |
| :--- | :--- |
| **🤖 Autonomous Multi-Agent Pipeline** | 7 specialized agents (Telemetry → RightSizing → Refresh → Compliance → Optimize → Execution → Reporting) chain together to make intelligent infrastructure decisions. |
| **📉 IT Right-Sizing** | Uses ML forecasting to reduce CPU/RAM allocations on underutilized VMs, calculating exact carbon savings per action. |
| **🔄 Predictive Refresh Cycles** | Applies Physics-of-Failure (PoF) algorithms to determine the exact "crossover point" when aging hardware should be replaced vs. repaired, minimizing e-waste and embodied carbon. |
| **⚖️ Regulatory Gatekeeper** | Real-time validation against MCMC data sovereignty laws and Bursa Malaysia climate risk disclosures. Automatically flags or drops non-compliant actions. |
| **🧑‍💼 Human-in-the-Loop** | All high-impact actions (resizes, refreshes) require approval via a modern dashboard, satisfying governance requirements. |
| **📄 Audit-Ready Reporting** | Automatically compiles reports mapped to Bursa Malaysia (TCFD/ISSB), MCMC Technical Codes, GRI 305 (Emissions), and SASB TC-HW/TC-TL. Includes an immutable audit trail. |
| **📊 Live Dashboard** | Real-time telemetry visualization (Chart.js), pending action queue, and ESG report viewer built with Tailwind CSS. |

---

## 🏗️ Architecture

The system is built on a **7‑Agent Sequential Pipeline**:
