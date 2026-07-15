# 🌟 Aura ML Analytics Dashboard

Aura ML Analytics is a premium, end-to-end Machine Learning platform built with Django, Scikit-Learn, and Tailwind CSS. It empowers users to upload raw datasets, automatically profile data, and train sophisticated machine learning models entirely from an elegant, glassmorphism-inspired web dashboard—no coding or ML expertise required.

---

## ✨ Key Features

* **🪄 AutoML Pipeline:** Automatically handles missing data imputation, categorical encoding, and algorithm execution for both Classification and Regression tasks.
* **📊 Automated Data Profiling:** Instantly detects dataset schemas, column data types, missing values, and calculates summary statistics upon upload.
* **🔮 Model Performance & Insights:** Generates real-time performance metrics (Accuracy, Precision, Recall, F1) and interactive Plotly.js feature importance charts.
* **💅 Premium Glassmorphism UI:** Features a highly modern, responsive interface utilizing animated mesh gradients, fluid micro-animations, and the 'Outfit' typography suite.
* **⚡ Asynchronous Processing:** Integrates seamlessly with Celery (with eager execution natively configured for local development) to ensure heavy ML tasks don't block the user experience.

---

## 🛠️ Technology Stack

**Backend**
* **Framework:** Django & Django REST Framework (DRF)
* **Database:** PostgreSQL (Production) / SQLite (Local Development)
* **Task Queue:** Celery & Redis
* **Machine Learning:** Scikit-Learn, XGBoost, Pandas, NumPy

**Frontend**
* **Styling:** Tailwind CSS (Vanilla)
* **Interactivity:** Vanilla JavaScript
* **Visualizations:** Plotly.js

---

## 🚀 Quickstart & Installation

The project is configured to run flawlessly on Windows local environments with a single command. `CELERY_TASK_ALWAYS_EAGER` is enabled by default in settings, meaning background tasks will execute synchronously, eliminating the immediate need for a Redis broker during local testing.

### Prerequisites
* Python 3.10+
* Git

### Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/IsharabAhmed/smart-ml-analytics-dashboard.git
   cd smart-ml-analytics-dashboard
   ```

2. **Run the Dashboard (Windows):**
   Simply execute the provided batch script to activate the virtual environment, apply migrations, and start the server.
   ```cmd
   .\run.bat
   ```

3. **Access the Application:**
   Open your browser and navigate to:
   `http://127.0.0.1:8000/`

---

## 📖 Usage Guide

1. **Upload Data:** Click the **Upload Dataset** button on the home page and select a valid CSV file.
2. **Review Profile:** Click on your newly uploaded dataset card to view the automated data profile, including row counts, feature counts, and missing value distributions.
3. **Train a Model:**
   * In the right-hand panel, select your **Task Type** (Classification, Regression, or Clustering).
   * Select your **Target Column**.
   * Choose an **Algorithm** (e.g., Random Forest, XGBoost) or leave it on Auto.
   * Click **Launch Training**.
4. **Analyze Results:** Scroll down to the **Trained Models** section to view your model's performance metrics and the interactive Feature Impact chart.

---

## 🐳 Docker Deployment (Optional)

For production or isolated environments, you can run the entire stack (Django, PostgreSQL, Redis, Celery Worker) using Docker Compose:

```bash
docker-compose up --build -d
```
*Note: Ensure Docker Desktop is installed and running.*
