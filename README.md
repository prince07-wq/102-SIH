# 🇮🇳 MPLAD — Intelligent Public Development Monitoring Platform

> **An AI-powered platform for transparent, data-driven monitoring and anomaly detection of MPLADS development projects.**

MPLAD is a full-stack web application designed to improve the **transparency, monitoring, and analysis of development projects** implemented under the **Members of Parliament Local Area Development Scheme (MPLADS)**.

The platform brings together **project management, financial data, interactive dashboards, authentication, analytics, and machine learning-based anomaly detection** into a single system.

---

## 🚀 Key Features

### 📊 Interactive Dashboard

* Overview of MPLADS projects and expenditure
* Project statistics and KPIs
* Fund utilization analysis
* Project status monitoring
* District/constituency-level insights
* Interactive charts and visualizations

### 🤖 AI/ML-Based Anomaly Detection

The platform uses machine learning to identify potentially unusual or suspicious project records.

Current ML pipeline includes:

* **Isolation Forest** for unsupervised anomaly detection
* Anomaly/risk scoring
* Project-level ML eligibility
* ML status classification
* Raw anomaly scores
* Detection of unusual expenditure/project patterns

The system can help authorities identify projects that may require **additional verification or human review**.

### 🔐 Authentication & Authorization

* Secure login system
* Session-based authentication
* Logout functionality
* Protected dashboard routes
* User authentication through the backend

### 🏗️ Project Monitoring

Each project can contain information such as:

* Project name
* Project category
* Location
* Constituency
* District
* Sanctioned amount
* Expenditure
* Project status
* Implementation details
* ML-generated risk/anomaly information

### 📈 Data Analytics

The platform provides analytical insights such as:

* Total projects
* Total sanctioned funds
* Total expenditure
* Fund utilization
* Completed vs ongoing projects
* Project distribution
* Potential anomalies
* Risk indicators

### 🏛️ Government-Oriented UI

The interface is designed around a professional government-dashboard experience with:

* Clean information hierarchy
* Responsive design
* Accessible navigation
* Sidebar-based dashboard
* Government-style visual language
* Desktop, tablet, and mobile support

---

# 🧠 AI/ML Pipeline

The ML system is designed to identify **unusual project patterns rather than automatically declaring a project fraudulent**.

### Current Approach

```text
Project Data
     ↓
Data Validation & Preprocessing
     ↓
Feature Engineering
     ↓
ML Eligibility Check
     ↓
Isolation Forest
     ↓
Anomaly Score
     ↓
Risk / ML Status
     ↓
Dashboard Visualization
     ↓
Human Verification
```

### Isolation Forest

Isolation Forest is an **unsupervised machine learning algorithm** used for anomaly detection.

Instead of learning from previously labeled fraudulent projects, it attempts to identify observations that are significantly different from the majority of the dataset.

This makes it useful for MPLADS data where labeled examples of fraud or irregularities may be limited.

### Potential Future Models

The architecture can be extended with additional ML techniques such as:

* **Local Outlier Factor (LOF)** — identifies projects that are unusual compared with their local neighborhood.
* **One-Class SVM** — learns the boundary of normal project behavior and flags observations outside that boundary.
* **Autoencoders** — neural networks that can learn normal data patterns and identify records with high reconstruction error.

These models can eventually be combined into an **ensemble anomaly-detection system** to improve robustness.

---

# 🏗️ System Architecture

```text
                    ┌─────────────────────┐
                    │       User          │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   React Frontend    │
                    │     + Vite           │
                    └──────────┬──────────┘
                               │ REST API
                               ▼
                    ┌─────────────────────┐
                    │   FastAPI Backend   │
                    └───────┬─────┬───────┘
                            │     │
                 ┌──────────┘     └──────────┐
                 ▼                           ▼
       ┌──────────────────┐        ┌──────────────────┐
       │   PostgreSQL     │        │    ML Pipeline   │
       │    Database      │        │ Isolation Forest │
       └──────────────────┘        └────────┬─────────┘
                                            │
                                            ▼
                                   ┌──────────────────┐
                                   │ Risk / Anomaly   │
                                   │     Results      │
                                   └──────────────────┘
```

---

# 🛠️ Tech Stack

## Frontend

| Technology    | Purpose                   |
| ------------- | ------------------------- |
| React.js      | Frontend framework        |
| Vite          | Development/build tooling |
| JavaScript    | Application logic         |
| CSS           | Styling & responsive UI   |
| Axios / Fetch | API communication         |

## Backend

| Technology | Purpose                  |
| ---------- | ------------------------ |
| Python     | Backend & ML development |
| FastAPI    | REST API framework       |
| Pydantic   | Data validation          |
| Uvicorn    | ASGI server              |
| Psycopg    | PostgreSQL connectivity  |

## Database

**PostgreSQL**

Used for storing:

* User information
* Project records
* Financial information
* Project status
* ML-related fields
* Other application data

## Artificial Intelligence / Machine Learning

* Scikit-learn
* Isolation Forest
* Feature engineering
* Statistical analysis
* Anomaly scoring

## Development & Deployment

* Git
* GitHub
* Vercel
* Python Virtual Environment
* REST APIs

---

# 📁 Project Structure

```text
MPLAD/
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   ├── assets/
│   │   └── ...
│   │
│   ├── public/
│   ├── package.json
│   ├── vite.config.js
│   └── ...
│
├── backend/
│   ├── api/
│   ├── services/
│   ├── models/
│   ├── ml/
│   ├── scripts/
│   └── ...
│
├── scripts/
│   └── database setup scripts
│
├── .env
├── .gitignore
└── README.md
```

> The exact folder structure may vary depending on the current branch/version of the project.

---

# ⚙️ Installation & Setup

## 1. Clone the Repository

```bash
git clone https://github.com/prince07-wq/102-SIH.git

cd 102-SIH
```

---

# 🐍 Backend Setup

Create a virtual environment:

### Windows

```bash
python -m venv venv
```

Activate it:

```bash
venv\Scripts\activate
```

### Linux / macOS

```bash
python3 -m venv venv
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

# 🗄️ PostgreSQL Setup

Make sure PostgreSQL is installed and running.

Create the required database:

```sql
CREATE DATABASE mplad;
```

Configure your environment variables.

Example:

```env
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/mplad
```

If your project uses separate PostgreSQL variables, configure them according to the backend configuration.

Run the database setup/migration scripts if required:

```bash
psql -U postgres -h localhost -p 5432 -d mplad -f scripts/setup_postgres.sql
```

---

# 🔑 Environment Variables

Create a `.env` file in the backend/project root.

Example:

```env
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/mplad

SECRET_KEY=your_secret_key

HOST=0.0.0.0
PORT=8000
```

> **Never commit `.env` files or production credentials to GitHub.**

---

# ▶️ Running the Backend

Start the FastAPI server:

```bash
uvicorn main:app --reload
```

The API will generally be available at:

```text
http://localhost:8000
```

FastAPI also provides interactive API documentation:

```text
http://localhost:8000/docs
```

---

# ⚛️ Running the Frontend

Navigate to the frontend:

```bash
cd frontend
```

Install dependencies:

```bash
npm install
```

Start the development server:

```bash
npm run dev
```

The Vite development server will provide a local URL, typically:

```text
http://localhost:5173
```

---

# 🔄 Data Flow

The application follows a standard full-stack data flow:

```text
PostgreSQL
    ↓
FastAPI Backend
    ↓
REST API
    ↓
React Frontend
    ↓
Dashboard
```

For ML-enabled records:

```text
PostgreSQL
    ↓
Backend Data Processing
    ↓
Feature Engineering
    ↓
Isolation Forest
    ↓
Anomaly Score
    ↓
ML Status
    ↓
React Dashboard
```

---

# 📡 API Architecture

The backend exposes REST APIs that allow the frontend to retrieve and interact with application data.

Typical flow:

```http
GET /api/projects
```

```text
React
  ↓
API Request
  ↓
FastAPI
  ↓
Database
  ↓
JSON Response
  ↓
React Dashboard
```

The backend is responsible for:

* Authentication
* Data validation
* Database operations
* Business logic
* ML processing
* Dashboard aggregation

---

# 📊 Example ML Fields

Each project can carry ML-related information such as:

```json
{
  "mlEligible": true,
  "mlStatus": "ANOMALY",
  "mlRawScore": -0.21
}
```

These fields allow the frontend to display machine-learning insights without exposing the internal ML implementation to the user.

---

# 🎯 Problem Statement

MPLADS involves a large number of development projects distributed across constituencies.

Monitoring such projects manually can make it difficult to quickly identify:

* Unusual expenditure patterns
* Outlier projects
* Abnormal project characteristics
* Potentially high-risk records
* Areas requiring closer inspection

The objective of this project is to provide a **centralized digital monitoring system** that combines conventional project analytics with machine learning-based anomaly detection.

---

# 💡 Proposed Solution

MPLAD provides a unified platform where project data can be:

1. Collected and stored
2. Validated and processed
3. Analyzed through dashboards
4. Evaluated using ML algorithms
5. Assigned anomaly/risk indicators
6. Presented to users for further investigation

The ML system acts as a **decision-support mechanism**, helping authorities prioritize projects for human review.

---

# 🌟 Why This Project Stands Out

### Traditional Dashboard

```text
Data → Charts → Reports
```

### MPLAD

```text
Data
 ↓
Analytics
 ↓
Machine Learning
 ↓
Anomaly Detection
 ↓
Risk Prioritization
 ↓
Human Verification
```

The platform therefore goes beyond simply displaying government data and introduces an **intelligent monitoring layer**.

---

# 🔮 Future Scope

The platform can be extended with:

### 🤖 Advanced AI

* Ensemble anomaly detection
* Autoencoders
* Local Outlier Factor
* One-Class SVM
* Predictive project completion analysis
* Risk prediction
* Natural Language Processing for project descriptions

### 🛰️ Geo-Spatial Intelligence

* Interactive project maps
* Constituency heatmaps
* Geographic anomaly clusters
* Location-based project analysis

### 📄 Document Intelligence

* Automated document verification
* OCR-based invoice extraction
* Document consistency checking
* AI-powered project report analysis

### 📈 Predictive Analytics

* Project completion prediction
* Expenditure forecasting
* Fund utilization prediction
* Delay prediction

### 🔔 Intelligent Alerts

Automatically notify administrators when:

* A project crosses a risk threshold
* Expenditure becomes unusual
* A project is significantly delayed
* Multiple anomalies occur in the same region

---

# 🔐 Security Considerations

The application is designed with security in mind:

* Authentication-protected routes
* Environment-based secrets
* Server-side validation
* Database-backed user management
* No credentials committed to source control

For production deployment, additional security measures should include:

* HTTPS
* Secure cookies
* CSRF protection where applicable
* Rate limiting
* Strong password hashing
* Role-based access control
* Production secret management

---

# 🚀 Deployment

The frontend can be deployed using platforms such as **Vercel**, while the FastAPI backend and PostgreSQL database can be deployed using a suitable cloud infrastructure.

Production architecture:

```text
                    Internet
                       │
          ┌────────────┴────────────┐
          ▼                         ▼
   React / Vite                FastAPI
    Frontend                   Backend
          │                         │
          │                         ▼
          │                    ML Pipeline
          │                         │
          │                         ▼
          └──────────────► PostgreSQL
```

---

# 🧪 Testing

Before deployment, verify:

### Frontend

```bash
npm run build
```

### Backend

```bash
uvicorn main:app
```

### Database

Verify:

* PostgreSQL is running
* Database exists
* Credentials are correct
* Required tables are initialized

### ML

Verify:

* Required features are available
* ML-eligible records are processed
* Anomaly scores are generated
* Results are correctly returned by the API

---

# 👥 Team

Developed as a **Smart India Hackathon (SIH)** project.

### Project

**MPLAD — Intelligent Public Development Monitoring Platform**

### Repository

**102-SIH**

---

# 📜 Disclaimer

The anomaly detection system is intended to support **monitoring and decision-making**.

An ML-generated anomaly or risk score **does not establish fraud, corruption, or wrongdoing**. Flagged projects should be reviewed and verified through appropriate administrative processes.

---

# 📌 Conclusion

MPLAD combines:

**Full-Stack Development + Data Analytics + Machine Learning + Government Technology**

to create a platform capable of transforming raw development-project data into actionable insights.

The ultimate goal is to make public-development monitoring more:

> **Transparent • Intelligent • Data-Driven • Efficient • Accountable**

---

## ⭐ Support

If you find this project useful, consider giving the repository a ⭐ on GitHub.
