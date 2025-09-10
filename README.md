# Lead Assessment POC: New Relic GTM Intelligence Platform

> Quick run & lifecycle docs have moved to `RUNNING.md` (includes `start_app.sh`, `stop_all.sh`, `restart.sh`). This README focuses on vision & architecture.

## 🚀 Quick Start

**For Team Members:**
```bash
# 1. Clone the repository
git clone <repository-url>
cd Lead_Assessment_POC

# 2. Run setup script
./setup.sh

# 3. Update environment variables
# Edit .env file with your API keys (especially GEMINI_API_KEY)

# 4. Start the application (dev)
FAST_START=true ./start_app.sh   # Skip heavy model steps on first run

# (New helper scripts)
# Stop:   ./stop_all.sh
# Restart: ./restart.sh

# 5. Open http://localhost:3000
```

## 📋 Project Overview

**Objective:** A comprehensive GTM Intelligence Platform that identifies high-value, high-propensity net new logos using AI-powered lead assessment, personalized outreach generation, and advanced analytics.

## ✨ Key Features

- **🎯 GTM Overview Dashboard** - Real-time metrics and KPIs with AI-powered insights
- **🤖 AI-Powered Outreach** - Personalized email generation using Gemini AI
- **📊 Advanced Analytics** - Interactive charts and data visualizations
- **🎯 Lead Scoring** - ML-powered propensity and value prediction
- **💰 Contract Value Analysis** - Revenue optimization insights
- **🌐 Lead Sourcing** - Comprehensive lead discovery and management
- **📈 Observability Metrics** - Industry-specific adoption tracking

## 🏗️ Architecture

- **Frontend:** React with Ant Design, enhanced New Relic theming
- **Backend:** FastAPI with Python
- **AI Integration:** Google Gemini API for intelligent insights
- **Charts:** Recharts with gradient styling and animations
- **Data:** CSV-based with ML model integration

## 1. Data Requirements and Business Signals

This project requires a consolidated view of a prospect, combining our internal engagement data with external firmographic and strategic intent data.

### 1.1 Internal Data Sources

These sources provide insight into how prospects interact with our brand.

#### Customer Relationship Management (CRM) Data
- **Lead and Contact Records:** Essential fields include Lead Source, Job Title, and Seniority Level
- **Account and Opportunity Records:** Required for model training, providing historical data on Industry, Employee Count, Geographic Region, and final Annual Contract Value (ACV)

#### Marketing and Web Engagement Data
- **Website Analytics:** Data points such as:
  - Pages Visited (specifically pricing, case studies)
  - Time on Site
  - Demo Request form submissions
- **Marketing Automation Platform:** Engagement metrics like:
  - Email Open Rate
  - Click Through Rate
  - History of content downloads (whitepapers, webinars)

### 1.2 External Data Sources

External data is critical for enriching our understanding of a prospect and for building look-alike audiences, especially given our relatively low historical lead conversion data.

#### Firmographic Data
This data describes the company itself.

**Required Signals:**
- Parent Company and Subsidiary relationships
- Global Employee Count
- Global Revenue
- Detailed Industry Classification (NAICS) - crucial for our parent level value modeling

**Example Providers:** Dun & Bradstreet, ZoomInfo, Clearbit

#### Technographic Data
This data reveals the prospect's current technology stack.

**Required Signals:**
- What CRM, Cloud Provider, or other software they use
- Helps gauge technical fit and integration opportunities

**Example Providers:** BuiltWith

#### Strategic Hiring and Intent Data
This is a key proactive signal layer that helps predict future needs.

**Required Signals:** We will analyze public job postings to capture:
- **Role Specific Hiring Velocity:** Notable increase in postings for roles like:
  - DevOps Engineer
  - Site Reliability Engineer (SRE)
  - Security Operations
- **Job Description Keywords:** Presence of terms like:
  - "observability"
  - "APM"
  - "OpenTelemetry"
  - "distributed tracing"
  - Competitor tool names
- **Leadership Hiring:** Postings for senior roles such as:
  - "Director of Observability"
  - "Head of Platform Engineering"
  - Indicates strategic company initiative

**Example Providers:** LinkedIn Talent Solutions, LinkUp

> **Note on Product Usage Data:** Internal product usage metrics (e.g., feature adoption) will not be used as predictive features for new logos. This data will be used exclusively one time to define our ground truth: identifying which of our existing customers constitute a "Golden Cohort" for training the model.

## 2. Modeling Strategy

Our approach uses two distinct models to address two separate questions: "Who should we talk to?" and "How much are they worth?" This respects the common business structure where intent is shown at a subsidiary level but purchasing decisions are made at a parent company level.

### 2.1 Model 1: Lead Propensity to Convert (Subsidiary Level)

**Purpose:** This classification model will predict the likelihood that a lead from a specific subsidiary or domain converts into a high-quality customer.

**Algorithm:** Gradient boosting model like XGBoost due to its high performance on structured data

**Unit of Analysis:** An individual lead or contact associated with a subsidiary domain

**Features:** Granular signals like:
- Job Title
- Web engagement
- Subsidiary-specific hiring trends
- Local technographics

**Output:** A propensity score from 0 to 1 for each subsidiary lead: `P(conversion)sub`

### 2.2 Model 2: Expected Contract Value (Parent Company Level)

**Purpose:** This regression model will predict the potential total deal size for an entire corporate account.

**Algorithm:** XGBoost Regressor

**Unit of Analysis:** The ultimate parent company of the lead

**Features:** High-level firmographic data, including:
- Parent Global Revenue
- Parent Global Employee Count
- Parent Industry

**Output:** A predicted Annual Contract Value: `ACVparent`

### 2.3 Score Reconciliation for Sales Prioritization

To provide a single actionable score, we will roll up the subsidiary scores to the parent account.

**Parent Propensity Score:** We will use a maximum function to capture the strongest buying signal within a large organization:

```
P(conversion)parent = max(P(conversion)sub1, P(conversion)sub2, P(conversion)sub3)
```

**Final Prioritized Account Score:** This unified score will be the product of the parent level propensity and value predictions:

```
Prioritized Account Score = P(conversion)parent × ACVparent
```

This score will be used to rank all potential accounts for the sales team.

## 3. Operationalization and Proof of Concept

The following plan details how the model's output will be integrated into the sales workflow to generate measurable results.



### 3.1 Step 1: Create the Target Contact Repository

1. **Prioritize Accounts:** The model will generate a ranked list of all potential parent companies based on the Prioritized Account Score
2. **Identify Personas:** For the top-tiered accounts, we will use data providers to find contacts that match our ideal buyer personas (e.g., VP of Engineering, Director of IT) within the specific subsidiaries that showed high intent
3. **Compile List:** This enriched list of contacts will be delivered to the sales development team as their primary outreach queue

### 3.2 Step 2: Implement a Personalized Outreach Engine

We will enable the sales team to use the model's insights for hyper-personalized communication at scale.

1. **Develop a Snippet Library:** We will create a library of reusable text snippets, with each snippet corresponding to a specific data signal (e.g., a specific technology in use, a recent hiring trend)
2. **Build Dynamic Templates:** Using an LLM-based approach, we will build email templates dynamically based on the data for each prospect

#### Example of Personalized Outreach:

```
Subject: Regarding {company_name}'s SRE team growth

Hi {first_name},

I noticed your team is hiring several Site Reliability Engineers and mentioned a focus on "distributed tracing" in the job descriptions. As you scale these critical systems, providing your new engineers with a powerful observability platform is essential for success.

Many engineering leaders in the {industry} sector use New Relic to reduce mean time to resolution and improve system reliability.

...
```

### 3.3 Step 3: Measure Success with an A/B Test

We will conduct a controlled experiment to validate the model's business impact.

**Control Group:** A segment of the sales team will use the existing lead generation and prioritization process.

**Treatment Group:** Another segment will exclusively use the prioritized list and personalized templates generated by our model.

**Key Performance Indicators:** Over one sales quarter, we will measure and compare the following for both groups:

- **Primary:** Meetings Booked
- **Secondary:** 
  - Email Reply Rate
  - Lead to Opportunity Conversion Rate

## Project Structure

```
Lead_Assessment_POC/
├── README.md                 # This file
├── data/                     # Data storage directory
├── models/                   # Model artifacts and code
├── notebooks/                # Jupyter notebooks for analysis
├── src/                      # Source code
└── docs/                     # Additional documentation
```

## Getting Started

1. Clone the repository
2. Set up the required data connections
3. Install dependencies
4. Run the model training pipeline
5. Deploy the scoring engine

## Contact

For questions about this project, please contact the project team.

---
Additional Docs:
- Runtime & Ops: `RUNNING.md`
- Deep Dive: `RUNTIME_GUIDE.md`
- Architecture: `ARCHITECTURE.md`
