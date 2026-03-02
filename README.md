# 🛡️ AeonShield: BEC & Phishing Detection Engine

![AeonShield Logo](AeonShiled%20Logo.png)

## 🌟 Overview

AeonShield is an **advanced, 3rd-generation Machine Learning pipeline** for detecting Business Email Compromise (BEC) and phishing attempts. It implements a multi-layered defense system that analyzes technical, linguistic, and structural signals to verify email authenticity.

The system is built upon a **Random Forest Classifier** strategically tuned with class weights to achieve **ultra-high Recall (98.24%+)**, ensuring malicious emails are correctly identified while providing a professional, dark-themed dashboard for monitoring and analysis.

### 🖼️ Dashboard Preview
![Dashboard Working](Dashboard%20Working.png)

---

## 🏗️ 3-Phase Detection Architecture

### **Phase 1: Explainable AI (XAI)**
- **XAI Engine:** Powered by SHAP (SHapley Additive exPlanations).
- **Functionality:** Provides a transparent "reasoning" for every prediction.
- **Features:** Urgency scores, domain similarity, financial keywords, and sender behavior.
- **Output:** Human-readable forensic alerts and feature contribution analysis.

### **Phase 2: Stylometry & ATO Detection**
- **Fingerprinting:** Analyzes the unique writing style (linguistic fingerprint) of senders.
- **ATO Defense:** Detects **Account Takeover (ATO)** by identifying "style drift" (deviations from baseline writing patterns).
- **Features:** 17 stylometric features including sentence structure, vocabulary richness, and formality scores.

### **Phase 3: Organizational Graph Analysis**
- **Graph Engine:** Maps the communication history and structure of the organization.
- **Anomalies:** Identifies structural violations such as hierarchy bypass, first-contact silos, and unusual department crossings.
- **Security:** Detects impersonation by verifying if the communication fits the organizational context.

---

## 🚀 Quick Start Guide

### **1. Set Up Environment**
Ensure you have Python 3.8+ installed. Then install dependencies:
```bash
pip install -r requirements.txt
```

### **2. Generate & Train (Complete Setup)**
Run the simulation and training scripts to build the baseline models and profiles:
```bash
python data_simulator_enhanced.py    # Generate enhanced BEC dataset
python train_model_stylometry.py     # Train Phase 1 & 2 models
python train_phase3.py               # Build Phase 3 Organizational Graph
```

### **3. Launch the Dashboard**
Launch the professional web interface to analyze emails:
```bash
streamlit run dashboard.py
```
Open your browser at `http://localhost:8501`.

---

## 📊 Dashboard Modules

1. **Dashboard Overview:** Real-time metrics on detection rates, threat types, and system health.
2. **Single Email Analysis:** Perform an in-depth, 3-phase check on suspicious emails.
3. **Batch Processing:** Upload CSV files to bulk-process thousands of emails.
4. **Model Analytics:** Deep dive into feature importance, accuracy, and ROC curves.
5. **Baseline Profiles:** Explore the linguistic fingerprint profiles of known senders.
6. **About Section:** Project credits and institutional background.

---

## 📁 Key File Structure

- `dashboard.py`: The main Streamlit web application.
- `xai_explainer.py`: SHAP-based explanation engine.
- `ato_detector.py`: Analysis engine for Account Takeover detection.
- `org_graph_analyzer.py`: Module for mapping organizational communication.
- `feature_engineer.py`: Preprocessing and linguistic feature extraction.
- `stylometry_analyzer.py`: Linguistic fingerprinting engine.
- `predict_email.py`: Command-line interface for single email prediction.

---

## 🎓 Project Recognition

### **Final Year Project**
This project was developed as part of the academic requirement for the final year.

**Project Team Members:**
*   **Akash Basak**: Lead Backend Developer & Integration Architect
*   **Abhiraj Kumar Rajak**: Machine Learning Researcher & Stylometry Expert
*   **Subhamita Mondal**: Security Analyst & UI Designer

**Institution:** Students of **Behala Government Polytechnic**

**Mentorship:**
*   **Sayuj Sur**: Industry Expert & Project Advisor

**Supervision:**
*   **Dr. Partha Sarathi Goswami**: Academic Supervisor

---

## 📜 Project Purpose
This project was developed to address the growing risk of sophisticated BEC attacks where traditional signature-based detection fails. By combining **behavioral analytics**, **linguistic profiling**, and **structural graph analysis**, AeonShield provides a production-grade defense mechanism for modern enterprises.
