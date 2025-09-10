from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import numpy as np
import joblib
import os
import json
from dotenv import load_dotenv

def convert_numpy_types(obj):
    """Convert numpy types to native Python types for JSON serialization"""
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        # Handle NaN and infinity values
        if np.isnan(obj) or np.isinf(obj):
            return 0.0
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {key: convert_numpy_types(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(item) for item in obj]
    else:
        return obj
from typing import List, Dict, Optional, Any
import uvicorn
from datetime import datetime, timedelta
import random
try:
    import google.generativeai as genai  # type: ignore
except Exception:  # pragma: no cover
    genai = None  # type: ignore

app = FastAPI(title="Lead Assessment POC API", version="1.0.0") 

# Load environment variables early
load_dotenv(override=False)

# Configure Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
model_name = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
if genai is not None and GEMINI_API_KEY:
    try:
        genai.configure(api_key=GEMINI_API_KEY)  # type: ignore
        model = genai.GenerativeModel(model_name)  # type: ignore
        print(f"Gemini model '{model_name}' initialized")
    except Exception as e:  # pragma: no cover
        print(f"Failed to initialize Gemini model: {e}")
        model = None
else:
    print("Gemini AI not configured (missing module or GEMINI_API_KEY)")
    model = None

# Function to generate executive summary using Gemini AI
from typing import Optional as _Optional

async def generate_executive_summary(data_type: str, filtered_data: pd.DataFrame, filters: Dict[str, Any], overview_data: _Optional[Dict[str, Any]] = None) -> str:
    """Generate executive summary using Gemini AI based on filtered data"""
    if not model:
        return "AI summary unavailable - Gemini API key not configured"

    try:
        # Prepare data summary
        data_summary = {
            "total_records": len(filtered_data),
            "filters_applied": filters,
            "data_type": data_type
        }
        
        # Add specific metrics based on data type
        if data_type == "sourcing":
            if not filtered_data.empty:
                data_summary.update({
                    "avg_sourcing_score": filtered_data['sourcing_score'].mean(),
                    "high_potential_leads": len(filtered_data[filtered_data['sourcing_score'] > 0.7]),
                    "top_industries": filtered_data['industry'].value_counts().head(3).to_dict(),
                    "avg_employee_count": filtered_data['employee_count'].mean()
                })
        elif data_type == "scoring":
            if not filtered_data.empty:
                data_summary.update({
                    "avg_conversion_probability": filtered_data['conversion_probability'].mean(),
                    "avg_engagement_score": filtered_data['engagement_score'].mean(),
                    "avg_composite_score": filtered_data['composite_score'].mean(),
                    "high_priority_leads": len(filtered_data[filtered_data['composite_score'] > 0.8])
                })
        elif data_type == "contract-value":
            if not filtered_data.empty:
                data_summary.update({
                    "avg_contract_value": filtered_data['estimated_contract_value'].mean(),
                    "total_potential_value": filtered_data['estimated_contract_value'].sum(),
                    "avg_upsell_potential": filtered_data['upsell_potential'].mean(),
                    "enterprise_leads": len(filtered_data[filtered_data['value_tier'] == 'Enterprise'])
                })
        elif data_type == "gtm-overview":
            if overview_data:
                data_summary.update(overview_data)
            else:
                data_summary.update({
                    "total_leads": len(filtered_data),
                    "avg_conversion_probability": filtered_data['conversion_probability'].mean() if 'conversion_probability' in filtered_data.columns else 0,
                    "avg_contract_value": filtered_data['contract_value'].mean() if 'contract_value' in filtered_data.columns else 0,
                    "high_quality_leads": len(filtered_data[filtered_data['nr_fit_score'] > 0.7]) if 'nr_fit_score' in filtered_data.columns else 0
                })
        elif data_type == "pipeline-health":
            if overview_data:
                data_summary.update(overview_data)
        elif data_type == "industry-analysis":
            if overview_data:
                data_summary.update(overview_data)
        elif data_type == "competitive-landscape":
            if overview_data:
                data_summary.update(overview_data)
        
        # Convert numpy types to native Python types for JSON serialization
        data_summary = convert_numpy_types(data_summary)
        
        # Create prompt for Gemini
        total_records = len(filtered_data)
        filters_text = json.dumps(filters)
        metrics_json = json.dumps(data_summary, indent=2)
        if data_type == "gtm-overview":
            prompt = (
                "You are a New Relic GTM Intelligence analyst. Produce a 4-5 sentence executive summary for the GTM overview. "
                f"Data Type: {data_type}. Records: {total_records}. Filters: {filters_text}. "
                "Focus on: pipeline health, industry & size opportunities, competitive signals, revenue optimization, priority actions. "
                "Context: New Relic vs Datadog, Splunk, Dynatrace, AppDynamics in full-stack observability. Use concrete numbers from metrics where helpful.\n"
                f"Metrics:\n{metrics_json}\n" 
                "Keep it concise, strategic, data-driven."
            )
        elif data_type == "pipeline-health":
            prompt = (
                "New Relic pipeline health summary (2-3 sentences). "
                f"Records: {total_records}. Filters: {filters_text}. Metrics:\n{metrics_json}\n"
                "Highlight conversion momentum, pipeline value, and immediate optimization lever."
            )
        elif data_type == "industry-analysis":
            prompt = (
                "Industry analysis summary (2-3 sentences) for New Relic observability adoption. "
                f"Records: {total_records}. Filters: {filters_text}. Metrics:\n{metrics_json}\n"
                "Call out top performing industries and strategic campaigns."
            )
        elif data_type == "competitive-landscape":
            prompt = (
                "Competitive landscape summary (2-3 sentences) for New Relic. "
                f"Records: {total_records}. Filters: {filters_text}. Metrics:\n{metrics_json}\n"
                "Mention switching opportunities & positioning."
            )
        else:
            prompt = (
                "Executive summary (2-3 sentences) for filtered dataset. "
                f"Type: {data_type}. Records: {total_records}. Filters: {filters_text}. Metrics:\n{metrics_json}\n"
                "Give key findings, implications, next step."
            )
        
        response = model.generate_content(prompt)  # type: ignore
        return getattr(response, 'text', 'No AI response text available')
    except Exception as e:  # pragma: no cover
        return f"Error generating summary: {str(e)}"

# Helper function to clean data for JSON serialization
def clean_data_for_json(data):
    """Clean data to ensure JSON serialization compatibility"""
    if isinstance(data, dict):
        return {k: clean_data_for_json(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [clean_data_for_json(item) for item in data]
    elif isinstance(data, (np.integer, np.floating)):
        if np.isnan(data):
            return None
        return data.item() if hasattr(data, 'item') else data
    elif pd.isna(data):
        return None
    elif isinstance(data, (int, float)):
        if np.isnan(data):
            return None
        return data
    else:
        return data

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:3002", "http://localhost:3003", "http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class LeadData(BaseModel):
    company_name: str
    industry: str
    employee_count: int
    revenue: float
    job_title: str
    seniority_level: str
    pages_visited: int
    time_on_site: int
    email_opens: int
    content_downloads: int
    hiring_velocity: int
    tech_stack: List[str]
    has_competitor: bool
    competitor_tool: Optional[str] = None
    nr_fit_score: Optional[float] = None
    nr_tier: Optional[str] = None

class PredictionRequest(BaseModel):
    leads: List[LeadData]

class PredictionResponse(BaseModel):
    predictions: List[Dict]
    summary: Dict

class OutreachRequest(BaseModel):
    company_name: str
    contact_name: str
    job_title: str
    industry: str
    tech_stack: List[str]
    hiring_signals: List[str]

# Global variables for models
propensity_model = None
value_model = None
leads_data = None

@app.on_event("startup")
async def startup_event():
    """Initialize models and data on startup"""
    global propensity_model, value_model, leads_data

    fast_start = os.getenv("FAST_START", "false").lower() in ["1", "true", "yes"]
    
    # Load or create models
    if not fast_start:
        try:
            propensity_model = joblib.load("models/propensity_model.pkl")
            value_model = joblib.load("models/value_model.pkl")
            print("Models loaded successfully")
        except Exception as e:
            print(f"Models not found or failed to load: {e}. Continuing with mock predictions.")
            propensity_model = None
            value_model = None
    else:
        print("FAST_START enabled: skipping model load")
        propensity_model = None
        value_model = None
    
    # Load or generate sample data
    try:
        leads_data = pd.read_csv("data/sample_leads.csv")
        print("Sample data loaded successfully")
    except Exception as e:
        print(f"Sample data not found or failed to load: {e}")
        leads_data = None

@app.get("/")
async def root():
    return {"message": "Lead Assessment POC API", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/api/leads")
async def get_leads(limit: int = 100):
    """Get sample leads data"""
    if leads_data is None:
        raise HTTPException(status_code=404, detail="No leads data available")
    
    # Clean the data to handle NaN values
    clean_data = leads_data.head(limit).copy()
    
    # Replace NaN values with appropriate defaults
    clean_data['nr_fit_score'] = clean_data['nr_fit_score'].fillna(0)
    clean_data['nr_tier'] = clean_data['nr_tier'].fillna('Standard')
    clean_data['contract_value'] = clean_data['contract_value'].fillna(0)
    # For competitor_tool, replace NaN with None
    clean_data['competitor_tool'] = clean_data['competitor_tool'].where(clean_data['competitor_tool'].notna(), None)
    
    # Convert to records and clean for JSON serialization
    records = clean_data.to_dict("records")
    return clean_data_for_json(records)

@app.get("/api/leads/stats")
async def get_lead_stats():
    """Get lead statistics for dashboard"""
    if leads_data is None:
        raise HTTPException(status_code=404, detail="No leads data available")
    
    # Clean data for stats calculation
    clean_data = leads_data.copy()
    clean_data['employee_count'] = clean_data['employee_count'].fillna(0)
    clean_data['revenue'] = clean_data['revenue'].fillna(0)
    clean_data['contract_value'] = clean_data['contract_value'].fillna(0)
    
    stats = {
        "total_leads": len(clean_data),
        "industries": clean_data['industry'].value_counts().to_dict(),
        "avg_employee_count": clean_data['employee_count'].mean(),
        "avg_revenue": clean_data['revenue'].mean(),
        "conversion_rate": random.uniform(0.15, 0.25),  # Simulated
        "avg_deal_size": random.uniform(50000, 200000),  # Simulated
        "total_pipeline_value": clean_data['contract_value'].sum(),
        "lead_quality_score": random.uniform(0.6, 0.9)  # Simulated
    }
    
    return clean_data_for_json(stats)

@app.post("/api/predict", response_model=PredictionResponse)
async def predict_leads(request: PredictionRequest):
    """Predict lead propensity and contract value"""
    if propensity_model is None or value_model is None:
        # Return mock predictions if models not available
        predictions = []
        for lead in request.leads:
            pred = {
                "company_name": lead.company_name,
                "propensity_score": random.uniform(0.1, 0.9),
                "contract_value": random.uniform(10000, 500000),
                "priority_score": random.uniform(0.1, 0.9),
                "confidence": random.uniform(0.7, 0.95)
            }
            predictions.append(pred)
        
        summary = {
            "total_leads": len(predictions),
            "avg_propensity": sum(p["propensity_score"] for p in predictions) / len(predictions),
            "total_potential_value": sum(p["contract_value"] for p in predictions),
            "high_priority_count": len([p for p in predictions if p["priority_score"] > 0.7])
        }
        
        return PredictionResponse(predictions=predictions, summary=summary)
    
    # Real model predictions would go here
    # For now, return mock data
    predictions = []
    for lead in request.leads:
        pred = {
            "company_name": lead.company_name,
            "propensity_score": random.uniform(0.1, 0.9),
            "contract_value": random.uniform(10000, 500000),
            "priority_score": random.uniform(0.1, 0.9),
            "confidence": random.uniform(0.7, 0.95)
        }
        predictions.append(pred)
    
    summary = {
        "total_leads": len(predictions),
        "avg_propensity": sum(p["propensity_score"] for p in predictions) / len(predictions),
        "total_potential_value": sum(p["contract_value"] for p in predictions),
        "high_priority_count": len([p for p in predictions if p["priority_score"] > 0.7])
    }
    
    return PredictionResponse(predictions=predictions, summary=summary)

@app.post("/api/outreach/generate")
async def generate_outreach(request: OutreachRequest):
    """Generate highly personalized outreach using AI analysis"""
    
    # Use Gemini AI to generate personalized outreach
    try:
        # Create a comprehensive prompt for Gemini
        prompt = f"""
        As a New Relic sales expert, create a highly personalized outreach email for:
        
        Company: {request.company_name}
        Contact: {request.contact_name} ({request.job_title})
        Industry: {request.industry}
        Tech Stack: {', '.join(request.tech_stack)}
        Hiring Signals: {', '.join(request.hiring_signals)}
        
        Requirements:
        1. Create a compelling subject line (max 50 characters)
        2. Write a personalized email (150-200 words) that:
           - References specific technologies they're using
           - Connects to their hiring patterns and growth
           - Addresses industry-specific observability challenges
           - Mentions relevant New Relic capabilities
           - Includes a clear, low-pressure call-to-action
        3. Make it sound natural and consultative, not salesy
        4. Include specific value propositions relevant to their tech stack
        
        Format the response as JSON with:
        - subject: the subject line
        - email_body: the email content
        - personalization_insights: why this approach will work
        - suggested_follow_up: next steps if no response
        """
        
        # Call Gemini API
        if os.getenv('GEMINI_API_KEY') and genai:
            genai.configure(api_key=os.getenv('GEMINI_API_KEY'))  # type: ignore
            model = genai.GenerativeModel('gemini-pro')  # type: ignore
            response = model.generate_content(prompt)  # type: ignore
            ai_response = json.loads(response.text)
            
            # Calculate personalization score based on input data richness
            personalization_score = 0.6  # Base score
            if len(request.tech_stack) > 2:
                personalization_score += 0.1
            if len(request.hiring_signals) > 1:
                personalization_score += 0.1
            if request.industry in ['Technology', 'Financial Services', 'Healthcare']:
                personalization_score += 0.1
            if any(tech in request.tech_stack for tech in ['AWS', 'Azure', 'GCP', 'Kubernetes', 'Docker']):
                personalization_score += 0.1
            
            return {
                "outreach_text": f"Subject: {ai_response.get('subject', '')}\n\n{ai_response.get('email_body', '')}",
                "personalization_score": min(personalization_score, 0.95),
                "suggested_follow_up": ai_response.get('suggested_follow_up', 'Follow up in 3-5 business days with additional value proposition'),
                "personalization_insights": ai_response.get('personalization_insights', ''),
                "key_signals_used": {
                    "hiring_signals": request.hiring_signals,
                    "tech_stack": request.tech_stack,
                    "industry": request.industry,
                    "job_title": request.job_title
                }
            }
        else:
            # Fallback to enhanced template if no API key
            return await generate_enhanced_template_outreach(request)
            
    except Exception as e:
        print(f"Error generating AI outreach: {e}")
        # Fallback to enhanced template
        return await generate_enhanced_template_outreach(request)

async def generate_enhanced_template_outreach(request: OutreachRequest):
    """Enhanced template-based outreach when AI is not available"""
    
    # Industry-specific pain points and solutions
    industry_insights = {
        "Technology": {
            "pain_point": "microservices complexity and distributed system monitoring",
            "solution": "distributed tracing and service mesh observability",
            "benefit": "reduce incident resolution time by 60%"
        },
        "Financial Services": {
            "pain_point": "regulatory compliance and transaction monitoring",
            "solution": "comprehensive audit trails and real-time transaction tracking",
            "benefit": "ensure 99.99% uptime for critical financial systems"
        },
        "Healthcare": {
            "pain_point": "patient data security and system reliability",
            "solution": "HIPAA-compliant monitoring and proactive alerting",
            "benefit": "maintain continuous patient care system availability"
        },
        "E-commerce": {
            "pain_point": "peak traffic management and conversion optimization",
            "solution": "real-time performance monitoring and user experience tracking",
            "benefit": "increase conversion rates by 25% during peak periods"
        },
        "Manufacturing": {
            "pain_point": "IoT device monitoring and predictive maintenance",
            "solution": "industrial IoT observability and predictive analytics",
            "benefit": "reduce unplanned downtime by 40%"
        }
    }
    
    # Tech stack specific benefits
    tech_benefits = {
        "AWS": "seamless integration with AWS CloudWatch and native AWS services",
        "Azure": "deep integration with Azure Monitor and Application Insights",
        "GCP": "native Google Cloud monitoring and Kubernetes observability",
        "Kubernetes": "container-native monitoring and service mesh observability",
        "Docker": "container performance monitoring and orchestration insights",
        "Python": "application performance monitoring for Python applications",
        "Java": "JVM monitoring and enterprise application observability",
        "Node.js": "asynchronous application monitoring and performance optimization",
        "React": "frontend performance monitoring and user experience tracking",
        "Datadog": "migration path from Datadog with enhanced AI-powered insights",
        "Splunk": "complementary log analysis with real-time application monitoring",
        "Dynatrace": "enhanced observability with better cost optimization",
        "AppDynamics": "superior distributed tracing and cloud-native monitoring"
    }
    
    # Get industry-specific insights
    industry_info = industry_insights.get(request.industry, industry_insights["Technology"])
    
    # Build tech stack benefits
    relevant_tech_benefits = []
    for tech in request.tech_stack[:3]:  # Limit to top 3
        if tech in tech_benefits:
            relevant_tech_benefits.append(tech_benefits[tech])
    
    tech_benefits_str = ", ".join(relevant_tech_benefits) if relevant_tech_benefits else "modern observability and monitoring"
    
    # Build hiring signals context
    hiring_context = ""
    if "DevOps" in request.hiring_signals or "Site Reliability" in request.hiring_signals:
        hiring_context = "As you're building out your DevOps and SRE capabilities,"
    elif "Director" in request.job_title or "Head" in request.job_title:
        hiring_context = "As a leader scaling your engineering organization,"
    else:
        hiring_context = "As you're growing your engineering team,"
    
    # Generate personalized outreach
    outreach_template = f"""
Subject: {request.company_name} - Observability for {request.industry} Scale

Hi {request.contact_name},

{hiring_context} I noticed {request.company_name} is working with {', '.join(request.tech_stack[:3])} and actively hiring for {', '.join(request.hiring_signals[:2])} roles.

Many {request.industry} companies face challenges with {industry_info['pain_point']}. New Relic helps solve this through {industry_info['solution']}, delivering {industry_info['benefit']}.

Specifically for your tech stack, we offer {tech_benefits_str}.

Would you be open to a brief 15-minute conversation about how we can help {request.company_name} achieve better observability as you scale?

Best regards,
[Your Name]
New Relic Sales Team
    """.strip()
    
    # Calculate personalization score
    personalization_score = 0.7  # Base score
    if len(request.tech_stack) > 2:
        personalization_score += 0.1
    if len(request.hiring_signals) > 1:
        personalization_score += 0.1
    if request.industry in industry_insights:
        personalization_score += 0.1
    
    return {
        "outreach_text": outreach_template,
        "personalization_score": min(personalization_score, 0.95),
        "suggested_follow_up": "Follow up in 3-5 business days with a relevant case study from your industry",
        "personalization_insights": f"Personalized based on {request.industry} industry challenges, {len(request.tech_stack)} technologies, and {len(request.hiring_signals)} hiring signals",
        "key_signals_used": {
            "hiring_signals": request.hiring_signals,
            "tech_stack": request.tech_stack,
            "industry": request.industry,
            "job_title": request.job_title
        }
    }

@app.get("/api/dashboard/metrics")
async def get_dashboard_metrics():
    """Get New Relic observability-focused metrics for dashboard charts"""
    # Generate realistic time series data based on observability trends
    dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='ME')
    
    # Observability adoption trend (growing over time)
    base_conversion = 0.12
    conversion_trend = []
    for i, date in enumerate(dates):
        # Simulate growing adoption of observability tools
        growth_factor = 1 + (i * 0.02)  # 2% growth per month
        seasonal_factor = 1 + 0.1 * np.sin(2 * np.pi * i / 12)  # Seasonal variation
        conversion_rate = base_conversion * growth_factor * seasonal_factor
        conversion_trend.append({
            "date": date.strftime("%Y-%m"), 
            "conversion_rate": round(conversion_rate, 3)
        })
    
    # Lead volume with realistic patterns
    lead_volume = []
    for i, date in enumerate(dates):
        # Higher volume in Q4 (budget season) and Q1 (planning)
        if i in [0, 1, 2, 9, 10, 11]:  # Q1 and Q4
            base_leads = 1200
        else:
            base_leads = 800
        
        # Add some randomness but keep it realistic
        leads = base_leads + random.randint(-200, 300)
        lead_volume.append({
            "date": date.strftime("%Y-%m"), 
            "leads": leads
        })
    
    # Observability market penetration by industry
    observability_adoption = [
        {"industry": "Technology", "adoption_rate": 0.78, "market_size": 4500},
        {"industry": "Financial Services", "adoption_rate": 0.65, "market_size": 3200},
        {"industry": "Healthcare", "adoption_rate": 0.45, "market_size": 2800},
        {"industry": "E-commerce", "adoption_rate": 0.72, "market_size": 2100},
        {"industry": "Manufacturing", "adoption_rate": 0.38, "market_size": 1800},
        {"industry": "Education", "adoption_rate": 0.42, "market_size": 1200}
    ]
    
    # New Relic product tier distribution (realistic)
    product_tiers = [
        {"tier": "Free Tier", "count": 1250, "percentage": 35, "color": "#E5E7EB"},
        {"tier": "Standard", "count": 900, "percentage": 25, "color": "#3B82F6"},
        {"tier": "Pro", "count": 720, "percentage": 20, "color": "#1E3A8A"},
        {"tier": "Enterprise", "count": 540, "percentage": 15, "color": "#00AC69"},
        {"tier": "Full-Stack", "count": 180, "percentage": 5, "color": "#F59E0B"}
    ]
    
    # Observability pain points (what drives New Relic sales)
    pain_points = [
        {"pain_point": "Application Performance Issues", "frequency": 0.68, "severity": "High"},
        {"pain_point": "Infrastructure Monitoring Gaps", "frequency": 0.55, "severity": "High"},
        {"pain_point": "Distributed Tracing Complexity", "frequency": 0.42, "severity": "Medium"},
        {"pain_point": "Log Management Challenges", "frequency": 0.38, "severity": "Medium"},
        {"pain_point": "Alert Fatigue", "frequency": 0.31, "severity": "Low"},
        {"pain_point": "Cost Optimization", "frequency": 0.28, "severity": "Low"}
    ]
    
    # Lead source effectiveness for observability
    lead_sources = [
        {"source": "Website/Demo Requests", "leads": 1200, "conversion_rate": 0.18, "quality": "High"},
        {"source": "Content Marketing", "leads": 800, "conversion_rate": 0.12, "quality": "Medium"},
        {"source": "Partner Referrals", "leads": 600, "conversion_rate": 0.25, "quality": "High"},
        {"source": "Events/Webinars", "leads": 500, "conversion_rate": 0.15, "quality": "Medium"},
        {"source": "Cold Outreach", "leads": 400, "conversion_rate": 0.08, "quality": "Low"},
        {"source": "Social Media", "leads": 300, "conversion_rate": 0.06, "quality": "Low"}
    ]
    
    metrics = {
        "conversion_trend": conversion_trend,
        "lead_volume": lead_volume,
        "observability_adoption": observability_adoption,
        "product_tiers": product_tiers,
        "pain_points": pain_points,
        "lead_sources": lead_sources
    }
    
    return clean_data_for_json(metrics)

@app.get("/api/leads/sourcing")
async def get_lead_sourcing_data(
    limit: int = 100,
    industry: Optional[str] = None,
    min_employee_count: Optional[int] = None,
    max_employee_count: Optional[int] = None,
    min_sourcing_score: Optional[float] = None,
    max_sourcing_score: Optional[float] = None,
    days_since_created_max: Optional[int] = None
):
    """Get leads data filtered for sourcing analysis"""
    if leads_data is None:
        raise HTTPException(status_code=404, detail="No leads data available")
    
    # Filter for sourcing-relevant data (new leads, high potential)
    sourcing_data = leads_data.copy()
    
    # Add sourcing-specific metrics
    # Generate random creation dates for sourcing analysis
    sourcing_data['created_at'] = pd.date_range(start='2024-01-01', end='2024-12-31', periods=len(sourcing_data))
    sourcing_data['days_since_created'] = (pd.Timestamp.now() - pd.to_datetime(sourcing_data['created_at'])).dt.days
    sourcing_data['sourcing_score'] = (
        sourcing_data['nr_fit_score'] * 0.4 + 
        (sourcing_data['employee_count'] / 1000) * 0.3 + 
        (sourcing_data['revenue'] / 1000000) * 0.3
    )
    
    # Apply filters
    filtered_data = sourcing_data.copy()
    
    # Industry filter
    if industry:
        filtered_data = filtered_data[filtered_data['industry'] == industry]
    
    # Employee count filters
    if min_employee_count is not None:
        filtered_data = filtered_data[filtered_data['employee_count'] >= min_employee_count]
    if max_employee_count is not None:
        filtered_data = filtered_data[filtered_data['employee_count'] <= max_employee_count]
    
    # Sourcing score filters
    if min_sourcing_score is not None:
        filtered_data = filtered_data[filtered_data['sourcing_score'] >= min_sourcing_score]
    if max_sourcing_score is not None:
        filtered_data = filtered_data[filtered_data['sourcing_score'] <= max_sourcing_score]
    
    # Days since created filter
    if days_since_created_max is not None:
        filtered_data = filtered_data[filtered_data['days_since_created'] <= days_since_created_max]
    
    # Default high-potential filter if no sourcing score filters applied
    if min_sourcing_score is None and max_sourcing_score is None:
        filtered_data = filtered_data[filtered_data['sourcing_score'] > 0.6]
    
    # Sort by sourcing score and limit
    filtered_data = filtered_data.sort_values('sourcing_score', ascending=False).head(limit)
    
    # Clean the data
    clean_data = filtered_data.copy()
    clean_data['nr_fit_score'] = clean_data['nr_fit_score'].fillna(0)
    clean_data['nr_tier'] = clean_data['nr_tier'].fillna('Standard')
    clean_data['contract_value'] = clean_data['contract_value'].fillna(0)
    clean_data['competitor_tool'] = clean_data['competitor_tool'].where(clean_data['competitor_tool'].notna(), None)
    clean_data['sourcing_score'] = clean_data['sourcing_score'].fillna(0)
    clean_data['days_since_created'] = clean_data['days_since_created'].fillna(0)
    
    records = clean_data.to_dict("records")
    return clean_data_for_json(records)

@app.get("/api/leads/scoring")
async def get_lead_scoring_data(
    limit: int = 100,
    industry: Optional[str] = None,
    min_conversion_probability: Optional[float] = None,
    max_conversion_probability: Optional[float] = None,
    min_engagement_score: Optional[float] = None,
    max_engagement_score: Optional[float] = None,
    min_urgency_score: Optional[float] = None,
    max_urgency_score: Optional[float] = None,
    min_composite_score: Optional[float] = None,
    max_composite_score: Optional[float] = None
):
    """Get leads data filtered for scoring analysis"""
    if leads_data is None:
        raise HTTPException(status_code=404, detail="No leads data available")
    
    # Filter for scoring-relevant data (all leads with scoring metrics)
    scoring_data = leads_data.copy()
    
    # Add scoring-specific metrics
    scoring_data['conversion_probability'] = scoring_data['nr_fit_score'] * 0.7 + random.uniform(0, 0.3)
    scoring_data['engagement_score'] = random.uniform(0, 1)
    scoring_data['urgency_score'] = random.uniform(0, 1)
    
    # Calculate composite score
    scoring_data['composite_score'] = (
        scoring_data['conversion_probability'] * 0.5 +
        scoring_data['engagement_score'] * 0.3 +
        scoring_data['urgency_score'] * 0.2
    )
    
    # Apply filters
    filtered_data = scoring_data.copy()
    
    # Industry filter
    if industry:
        filtered_data = filtered_data[filtered_data['industry'] == industry]
    
    # Conversion probability filters
    if min_conversion_probability is not None:
        filtered_data = filtered_data[filtered_data['conversion_probability'] >= min_conversion_probability]
    if max_conversion_probability is not None:
        filtered_data = filtered_data[filtered_data['conversion_probability'] <= max_conversion_probability]
    
    # Engagement score filters
    if min_engagement_score is not None:
        filtered_data = filtered_data[filtered_data['engagement_score'] >= min_engagement_score]
    if max_engagement_score is not None:
        filtered_data = filtered_data[filtered_data['engagement_score'] <= max_engagement_score]
    
    # Urgency score filters
    if min_urgency_score is not None:
        filtered_data = filtered_data[filtered_data['urgency_score'] >= min_urgency_score]
    if max_urgency_score is not None:
        filtered_data = filtered_data[filtered_data['urgency_score'] <= max_urgency_score]
    
    # Composite score filters
    if min_composite_score is not None:
        filtered_data = filtered_data[filtered_data['composite_score'] >= min_composite_score]
    if max_composite_score is not None:
        filtered_data = filtered_data[filtered_data['composite_score'] <= max_composite_score]
    
    # Sort by composite score and limit
    filtered_data = filtered_data.sort_values('composite_score', ascending=False).head(limit)
    
    # Clean the data
    clean_data = filtered_data.copy()
    clean_data['nr_fit_score'] = clean_data['nr_fit_score'].fillna(0)
    clean_data['nr_tier'] = clean_data['nr_tier'].fillna('Standard')
    clean_data['contract_value'] = clean_data['contract_value'].fillna(0)
    clean_data['competitor_tool'] = clean_data['competitor_tool'].where(clean_data['competitor_tool'].notna(), None)
    clean_data['conversion_probability'] = clean_data['conversion_probability'].fillna(0)
    clean_data['engagement_score'] = clean_data['engagement_score'].fillna(0)
    clean_data['urgency_score'] = clean_data['urgency_score'].fillna(0)
    clean_data['composite_score'] = clean_data['composite_score'].fillna(0)
    
    records = clean_data.to_dict("records")
    return clean_data_for_json(records)

@app.get("/api/leads/contract-value")
async def get_contract_value_data(
    limit: int = 100,
    industry: Optional[str] = None,
    value_tier: Optional[str] = None,
    min_contract_value: Optional[float] = None,
    max_contract_value: Optional[float] = None,
    min_upsell_potential: Optional[float] = None,
    max_upsell_potential: Optional[float] = None,
    min_renewal_probability: Optional[float] = None,
    max_renewal_probability: Optional[float] = None
):
    """Get leads data filtered for contract value analysis"""
    if leads_data is None:
        raise HTTPException(status_code=404, detail="No leads data available")
    
    # Filter for contract value analysis (leads with revenue potential)
    contract_data = leads_data.copy()
    
    # Add contract value specific metrics
    contract_data['estimated_contract_value'] = (
        contract_data['revenue'] * 0.02 +  # 2% of revenue
        contract_data['employee_count'] * 100 +  # $100 per employee
        random.uniform(10000, 50000)  # Base value
    )
    
    contract_data['value_tier'] = pd.cut(
        contract_data['estimated_contract_value'],
        bins=[0, 50000, 150000, 500000, float('inf')],
        labels=['Standard', 'Professional', 'Enterprise', 'Strategic']
    )
    
    contract_data['upsell_potential'] = random.uniform(0, 1)
    contract_data['renewal_probability'] = random.uniform(0.6, 0.95)
    
    # Apply filters
    filtered_data = contract_data.copy()
    
    # Industry filter
    if industry:
        filtered_data = filtered_data[filtered_data['industry'] == industry]
    
    # Value tier filter
    if value_tier:
        filtered_data = filtered_data[filtered_data['value_tier'] == value_tier]
    
    # Contract value filters
    if min_contract_value is not None:
        filtered_data = filtered_data[filtered_data['estimated_contract_value'] >= min_contract_value]
    if max_contract_value is not None:
        filtered_data = filtered_data[filtered_data['estimated_contract_value'] <= max_contract_value]
    
    # Upsell potential filters
    if min_upsell_potential is not None:
        filtered_data = filtered_data[filtered_data['upsell_potential'] >= min_upsell_potential]
    if max_upsell_potential is not None:
        filtered_data = filtered_data[filtered_data['upsell_potential'] <= max_upsell_potential]
    
    # Renewal probability filters
    if min_renewal_probability is not None:
        filtered_data = filtered_data[filtered_data['renewal_probability'] >= min_renewal_probability]
    if max_renewal_probability is not None:
        filtered_data = filtered_data[filtered_data['renewal_probability'] <= max_renewal_probability]
    
    # Sort by estimated contract value and limit
    filtered_data = filtered_data.sort_values('estimated_contract_value', ascending=False).head(limit)
    
    # Clean the data
    clean_data = filtered_data.copy()
    clean_data['nr_fit_score'] = clean_data['nr_fit_score'].fillna(0)
    clean_data['nr_tier'] = clean_data['nr_tier'].fillna('Standard')
    clean_data['contract_value'] = clean_data['contract_value'].fillna(0)
    clean_data['competitor_tool'] = clean_data['competitor_tool'].where(clean_data['competitor_tool'].notna(), None)
    clean_data['estimated_contract_value'] = clean_data['estimated_contract_value'].fillna(0)
    clean_data['upsell_potential'] = clean_data['upsell_potential'].fillna(0)
    clean_data['renewal_probability'] = clean_data['renewal_probability'].fillna(0)
    
    records = clean_data.to_dict("records")
    return clean_data_for_json(records)

# AI Summary endpoints
@app.get("/api/summary/sourcing")
async def get_sourcing_summary(
    industry: Optional[str] = None,
    min_employee_count: Optional[int] = None,
    max_employee_count: Optional[int] = None,
    min_sourcing_score: Optional[float] = None,
    max_sourcing_score: Optional[float] = None,
    days_since_created_max: Optional[int] = None
):
    """Generate AI executive summary for sourcing data"""
    if leads_data is None:
        raise HTTPException(status_code=404, detail="No leads data available")
    
    # Apply same filtering logic as sourcing endpoint
    sourcing_data = leads_data.copy()
    sourcing_data['sourcing_score'] = (
        sourcing_data['nr_fit_score'] * 0.4 + 
        (sourcing_data['employee_count'] / 1000) * 0.3 + 
        (sourcing_data['revenue'] / 1000000) * 0.3
    )
    
    # Apply filters
    filtered_data = sourcing_data.copy()
    if industry:
        filtered_data = filtered_data[filtered_data['industry'] == industry]
    if min_employee_count is not None:
        filtered_data = filtered_data[filtered_data['employee_count'] >= min_employee_count]
    if max_employee_count is not None:
        filtered_data = filtered_data[filtered_data['employee_count'] <= max_employee_count]
    if min_sourcing_score is not None:
        filtered_data = filtered_data[filtered_data['sourcing_score'] >= min_sourcing_score]
    if max_sourcing_score is not None:
        filtered_data = filtered_data[filtered_data['sourcing_score'] <= max_sourcing_score]
    if days_since_created_max is not None:
        filtered_data['created_at'] = pd.date_range(start='2024-01-01', end='2024-12-31', periods=len(filtered_data))
        filtered_data['days_since_created'] = (pd.Timestamp.now() - pd.to_datetime(filtered_data['created_at'])).dt.days
        filtered_data = filtered_data[filtered_data['days_since_created'] <= days_since_created_max]
    
    # Default high-potential filter if no sourcing score filters applied
    if min_sourcing_score is None and max_sourcing_score is None:
        filtered_data = filtered_data[filtered_data['sourcing_score'] > 0.6]
    
    filters = {
        "industry": industry,
        "min_employee_count": min_employee_count,
        "max_employee_count": max_employee_count,
        "min_sourcing_score": min_sourcing_score,
        "max_sourcing_score": max_sourcing_score,
        "days_since_created_max": days_since_created_max
    }
    
    summary = await generate_executive_summary("sourcing", filtered_data, filters)
    return {"summary": summary, "record_count": len(filtered_data)}

@app.get("/api/summary/scoring")
async def get_scoring_summary(
    industry: Optional[str] = None,
    min_conversion_probability: Optional[float] = None,
    max_conversion_probability: Optional[float] = None,
    min_engagement_score: Optional[float] = None,
    max_engagement_score: Optional[float] = None,
    min_urgency_score: Optional[float] = None,
    max_urgency_score: Optional[float] = None,
    min_composite_score: Optional[float] = None,
    max_composite_score: Optional[float] = None
):
    """Generate AI executive summary for scoring data"""
    if leads_data is None:
        raise HTTPException(status_code=404, detail="No leads data available")
    
    # Apply same filtering logic as scoring endpoint
    scoring_data = leads_data.copy()
    scoring_data['conversion_probability'] = np.random.uniform(0.1, 0.9, len(scoring_data))
    scoring_data['engagement_score'] = np.random.uniform(0.2, 0.95, len(scoring_data))
    scoring_data['urgency_score'] = np.random.uniform(0.1, 0.8, len(scoring_data))
    scoring_data['composite_score'] = (
        scoring_data['conversion_probability'] * 0.5 +
        scoring_data['engagement_score'] * 0.3 +
        scoring_data['urgency_score'] * 0.2
    )
    
    # Apply filters
    filtered_data = scoring_data.copy()
    if industry:
        filtered_data = filtered_data[filtered_data['industry'] == industry]
    if min_conversion_probability is not None:
        filtered_data = filtered_data[filtered_data['conversion_probability'] >= min_conversion_probability]
    if max_conversion_probability is not None:
        filtered_data = filtered_data[filtered_data['conversion_probability'] <= max_conversion_probability]
    if min_engagement_score is not None:
        filtered_data = filtered_data[filtered_data['engagement_score'] >= min_engagement_score]
    if max_engagement_score is not None:
        filtered_data = filtered_data[filtered_data['engagement_score'] <= max_engagement_score]
    if min_urgency_score is not None:
        filtered_data = filtered_data[filtered_data['urgency_score'] >= min_urgency_score]
    if max_urgency_score is not None:
        filtered_data = filtered_data[filtered_data['urgency_score'] <= max_urgency_score]
    if min_composite_score is not None:
        filtered_data = filtered_data[filtered_data['composite_score'] >= min_composite_score]
    if max_composite_score is not None:
        filtered_data = filtered_data[filtered_data['composite_score'] <= max_composite_score]
    
    filters = {
        "industry": industry,
        "min_conversion_probability": min_conversion_probability,
        "max_conversion_probability": max_conversion_probability,
        "min_engagement_score": min_engagement_score,
        "max_engagement_score": max_engagement_score,
        "min_urgency_score": min_urgency_score,
        "max_urgency_score": max_urgency_score,
        "min_composite_score": min_composite_score,
        "max_composite_score": max_composite_score
    }
    
    summary = await generate_executive_summary("scoring", filtered_data, filters)
    return {"summary": summary, "record_count": len(filtered_data)}

@app.get("/api/summary/contract-value")
async def get_contract_value_summary(
    industry: Optional[str] = None,
    value_tier: Optional[str] = None,
    min_contract_value: Optional[float] = None,
    max_contract_value: Optional[float] = None,
    min_upsell_potential: Optional[float] = None,
    max_upsell_potential: Optional[float] = None,
    min_renewal_probability: Optional[float] = None,
    max_renewal_probability: Optional[float] = None
):
    """Generate AI executive summary for contract value data"""
    if leads_data is None:
        raise HTTPException(status_code=404, detail="No leads data available")
    
    # Apply same filtering logic as contract-value endpoint
    contract_data = leads_data.copy()
    contract_data['estimated_contract_value'] = (
        contract_data['revenue'] * 0.02 + 
        contract_data['employee_count'] * 50 + 
        np.random.uniform(10000, 500000, len(contract_data))
    )
    
    contract_data['value_tier'] = pd.cut(
        contract_data['estimated_contract_value'],
        bins=[0, 50000, 150000, 500000, float('inf')],
        labels=['Standard', 'Professional', 'Enterprise', 'Strategic']
    )
    
    contract_data['upsell_potential'] = np.random.uniform(0, 1, len(contract_data))
    contract_data['renewal_probability'] = np.random.uniform(0.6, 0.95, len(contract_data))
    
    # Apply filters
    filtered_data = contract_data.copy()
    if industry:
        filtered_data = filtered_data[filtered_data['industry'] == industry]
    if value_tier:
        filtered_data = filtered_data[filtered_data['value_tier'] == value_tier]
    if min_contract_value is not None:
        filtered_data = filtered_data[filtered_data['estimated_contract_value'] >= min_contract_value]
    if max_contract_value is not None:
        filtered_data = filtered_data[filtered_data['estimated_contract_value'] <= max_contract_value]
    if min_upsell_potential is not None:
        filtered_data = filtered_data[filtered_data['upsell_potential'] >= min_upsell_potential]
    if max_upsell_potential is not None:
        filtered_data = filtered_data[filtered_data['upsell_potential'] <= max_upsell_potential]
    if min_renewal_probability is not None:
        filtered_data = filtered_data[filtered_data['renewal_probability'] >= min_renewal_probability]
    if max_renewal_probability is not None:
        filtered_data = filtered_data[filtered_data['renewal_probability'] <= max_renewal_probability]
    
    filters = {
        "industry": industry,
        "value_tier": value_tier,
        "min_contract_value": min_contract_value,
        "max_contract_value": max_contract_value,
        "min_upsell_potential": min_upsell_potential,
        "max_upsell_potential": max_upsell_potential,
        "min_renewal_probability": min_renewal_probability,
        "max_renewal_probability": max_renewal_probability
    }
    
    summary = await generate_executive_summary("contract-value", filtered_data, filters)
    return {"summary": summary, "record_count": len(filtered_data)}

@app.get("/api/summary/gtm-overview")
async def get_gtm_overview_summary(
    industry: Optional[str] = None,
    company_size: Optional[str] = None
):
    """Generate AI executive summary for GTM overview dashboard"""
    if leads_data is None:
        raise HTTPException(status_code=404, detail="No leads data available")
    
    # Apply filters for overview analysis
    filtered_data = leads_data.copy()
    
    if industry:
        filtered_data = filtered_data[filtered_data['industry'] == industry]
    
    if company_size:
        if company_size == "startup":
            filtered_data = filtered_data[filtered_data['employee_count'] <= 50]
        elif company_size == "small":
            filtered_data = filtered_data[(filtered_data['employee_count'] > 50) & (filtered_data['employee_count'] <= 200)]
        elif company_size == "medium":
            filtered_data = filtered_data[(filtered_data['employee_count'] > 200) & (filtered_data['employee_count'] <= 1000)]
        elif company_size == "large":
            filtered_data = filtered_data[filtered_data['employee_count'] > 1000]
    
    # Calculate comprehensive overview metrics for better LLM analysis
    total_leads = len(filtered_data)
    
    # Conversion metrics
    avg_conversion_prob = filtered_data['conversion_probability'].mean() if 'conversion_probability' in filtered_data.columns else 0
    conversion_rate = (filtered_data['converted'] == True).sum() / total_leads if total_leads > 0 else 0
    
    # Contract value metrics
    avg_contract_value = filtered_data['contract_value'].mean() if 'contract_value' in filtered_data.columns else 0
    total_pipeline_value = filtered_data['contract_value'].sum() if 'contract_value' in filtered_data.columns else 0
    high_value_leads = len(filtered_data[filtered_data['contract_value'] > 100000]) if 'contract_value' in filtered_data.columns else 0
    
    # Quality metrics
    high_quality_leads = len(filtered_data[filtered_data['nr_fit_score'] > 0.7]) if 'nr_fit_score' in filtered_data.columns else 0
    avg_fit_score = filtered_data['nr_fit_score'].mean() if 'nr_fit_score' in filtered_data.columns else 0
    
    # Industry distribution
    industry_dist = filtered_data['industry'].value_counts().head(5).to_dict() if 'industry' in filtered_data.columns else {}
    
    # Company size distribution
    size_dist = {
        "startup": len(filtered_data[filtered_data['employee_count'] <= 50]),
        "small": len(filtered_data[(filtered_data['employee_count'] > 50) & (filtered_data['employee_count'] <= 200)]),
        "medium": len(filtered_data[(filtered_data['employee_count'] > 200) & (filtered_data['employee_count'] <= 1000)]),
        "large": len(filtered_data[filtered_data['employee_count'] > 1000])
    }
    
    # Competitor analysis
    competitor_dist = filtered_data['competitor_tool'].value_counts().head(5).to_dict() if 'competitor_tool' in filtered_data.columns else {}
    
    # Engagement metrics
    avg_engagement = filtered_data['pages_visited'].mean() if 'pages_visited' in filtered_data.columns else 0
    high_engagement_leads = len(filtered_data[filtered_data['pages_visited'] > 20]) if 'pages_visited' in filtered_data.columns else 0
    
    # Industry breakdown
    industry_breakdown = filtered_data['industry'].value_counts().head(3).to_dict() if 'industry' in filtered_data.columns else {}
    
    filters = {
        "industry": industry,
        "company_size": company_size
    }
    
    # Create a comprehensive overview summary
    overview_data = {
        "total_leads": total_leads,
        "conversion_rate": conversion_rate,
        "avg_conversion_probability": avg_conversion_prob,
        "avg_contract_value": avg_contract_value,
        "total_pipeline_value": total_pipeline_value,
        "high_value_leads": high_value_leads,
        "high_quality_leads": high_quality_leads,
        "avg_fit_score": avg_fit_score,
        "industry_distribution": industry_dist,
        "company_size_distribution": size_dist,
        "competitor_distribution": competitor_dist,
        "avg_engagement": avg_engagement,
        "high_engagement_leads": high_engagement_leads
    }
    
    summary = await generate_executive_summary("gtm-overview", filtered_data, filters, overview_data)
    return {"summary": summary, "record_count": int(total_leads), "overview_metrics": convert_numpy_types(overview_data)}

@app.get("/api/summary/pipeline-health")
async def get_pipeline_health_summary(
    industry: Optional[str] = None,
    company_size: Optional[str] = None
):
    """Generate AI summary for pipeline health chart"""
    if leads_data is None:
        raise HTTPException(status_code=404, detail="No leads data available")
    
    # Apply same filtering logic as GTM overview
    filtered_data = leads_data.copy()
    
    if industry:
        filtered_data = filtered_data[filtered_data['industry'] == industry]
    
    if company_size:
        if company_size == "startup":
            filtered_data = filtered_data[filtered_data['employee_count'] <= 50]
        elif company_size == "small":
            filtered_data = filtered_data[(filtered_data['employee_count'] > 50) & (filtered_data['employee_count'] <= 200)]
        elif company_size == "medium":
            filtered_data = filtered_data[(filtered_data['employee_count'] > 200) & (filtered_data['employee_count'] <= 1000)]
        elif company_size == "large":
            filtered_data = filtered_data[filtered_data['employee_count'] > 1000]
    
    # Pipeline health specific metrics
    total_leads = len(filtered_data)
    conversion_rate = (filtered_data['converted'] == True).sum() / total_leads if total_leads > 0 else 0
    avg_conversion_prob = filtered_data['conversion_probability'].mean() if 'conversion_probability' in filtered_data.columns else 0
    total_pipeline_value = filtered_data['contract_value'].sum() if 'contract_value' in filtered_data.columns else 0
    
    filters = {"industry": industry, "company_size": company_size}
    
    pipeline_data = {
        "total_leads": total_leads,
        "conversion_rate": conversion_rate,
        "avg_conversion_probability": avg_conversion_prob,
        "total_pipeline_value": total_pipeline_value
    }
    
    summary = await generate_executive_summary("pipeline-health", filtered_data, filters, pipeline_data)
    return {"summary": summary, "record_count": int(total_leads), "pipeline_metrics": convert_numpy_types(pipeline_data)}

@app.get("/api/summary/industry-analysis")
async def get_industry_analysis_summary(
    industry: Optional[str] = None,
    company_size: Optional[str] = None
):
    """Generate AI summary for industry analysis chart"""
    if leads_data is None:
        raise HTTPException(status_code=404, detail="No leads data available")
    
    # Apply same filtering logic
    filtered_data = leads_data.copy()
    
    if industry:
        filtered_data = filtered_data[filtered_data['industry'] == industry]
    
    if company_size:
        if company_size == "startup":
            filtered_data = filtered_data[filtered_data['employee_count'] <= 50]
        elif company_size == "small":
            filtered_data = filtered_data[(filtered_data['employee_count'] > 50) & (filtered_data['employee_count'] <= 200)]
        elif company_size == "medium":
            filtered_data = filtered_data[(filtered_data['employee_count'] > 200) & (filtered_data['employee_count'] <= 1000)]
        elif company_size == "large":
            filtered_data = filtered_data[filtered_data['employee_count'] > 1000]
    
    # Industry analysis specific metrics
    industry_dist = filtered_data['industry'].value_counts().head(5).to_dict() if 'industry' in filtered_data.columns else {}
    industry_conversion = filtered_data.groupby('industry')['converted'].mean().to_dict() if 'converted' in filtered_data.columns else {}
    industry_value = filtered_data.groupby('industry')['contract_value'].mean().to_dict() if 'contract_value' in filtered_data.columns else {}
    
    filters = {"industry": industry, "company_size": company_size}
    
    industry_data = {
        "industry_distribution": industry_dist,
        "industry_conversion_rates": industry_conversion,
        "industry_avg_contract_values": industry_value
    }
    
    summary = await generate_executive_summary("industry-analysis", filtered_data, filters, industry_data)
    return {"summary": summary, "record_count": len(filtered_data), "industry_metrics": industry_data}

@app.get("/api/summary/competitive-landscape")
async def get_competitive_landscape_summary(
    industry: Optional[str] = None,
    company_size: Optional[str] = None
):
    """Generate AI summary for competitive landscape chart"""
    if leads_data is None:
        raise HTTPException(status_code=404, detail="No leads data available")
    
    # Apply same filtering logic
    filtered_data = leads_data.copy()
    
    if industry:
        filtered_data = filtered_data[filtered_data['industry'] == industry]
    
    if company_size:
        if company_size == "startup":
            filtered_data = filtered_data[filtered_data['employee_count'] <= 50]
        elif company_size == "small":
            filtered_data = filtered_data[(filtered_data['employee_count'] > 50) & (filtered_data['employee_count'] <= 200)]
        elif company_size == "medium":
            filtered_data = filtered_data[(filtered_data['employee_count'] > 200) & (filtered_data['employee_count'] <= 1000)]
        elif company_size == "large":
            filtered_data = filtered_data[filtered_data['employee_count'] > 1000]
    
    # Competitive landscape specific metrics
    competitor_dist = filtered_data['competitor_tool'].value_counts().head(5).to_dict() if 'competitor_tool' in filtered_data.columns else {}
    competitor_conversion = filtered_data.groupby('competitor_tool')['converted'].mean().to_dict() if 'converted' in filtered_data.columns else {}
    switching_opportunities = len(filtered_data[filtered_data['competitor_tool'].isin(['Datadog', 'Splunk', 'Dynatrace'])])
    
    filters = {"industry": industry, "company_size": company_size}
    
    competitive_data = {
        "competitor_distribution": competitor_dist,
        "competitor_conversion_rates": competitor_conversion,
        "switching_opportunities": switching_opportunities
    }
    
    summary = await generate_executive_summary("competitive-landscape", filtered_data, filters, competitive_data)
    return {"summary": summary, "record_count": len(filtered_data), "competitive_metrics": competitive_data}

@app.get("/api/summary/product-tiers")
async def get_product_tier_summary(
    industry: Optional[str] = None,
    company_size: Optional[str] = None
):
    """Generate AI executive summary for product tier distribution"""
    if leads_data is None:
        raise HTTPException(status_code=404, detail="No leads data available")
    
    # Apply filters
    filtered_data = leads_data.copy()
    
    if industry:
        filtered_data = filtered_data[filtered_data['industry'] == industry]
    
    if company_size:
        if company_size == "startup":
            filtered_data = filtered_data[filtered_data['employee_count'] <= 50]
        elif company_size == "small":
            filtered_data = filtered_data[(filtered_data['employee_count'] > 50) & (filtered_data['employee_count'] <= 200)]
        elif company_size == "medium":
            filtered_data = filtered_data[(filtered_data['employee_count'] > 200) & (filtered_data['employee_count'] <= 1000)]
        elif company_size == "large":
            filtered_data = filtered_data[filtered_data['employee_count'] > 1000]
    
    filters = {
        "industry": industry,
        "company_size": company_size
    }
    
    summary = await generate_executive_summary("product-tiers", filtered_data, filters)
    return {"summary": summary, "record_count": len(filtered_data)}

@app.get("/api/summary/lead-sources")
async def get_lead_source_summary(
    industry: Optional[str] = None,
    company_size: Optional[str] = None
):
    """Generate AI executive summary for lead source effectiveness"""
    if leads_data is None:
        raise HTTPException(status_code=404, detail="No leads data available")
    
    # Apply filters
    filtered_data = leads_data.copy()
    
    if industry:
        filtered_data = filtered_data[filtered_data['industry'] == industry]
    
    if company_size:
        if company_size == "startup":
            filtered_data = filtered_data[filtered_data['employee_count'] <= 50]
        elif company_size == "small":
            filtered_data = filtered_data[(filtered_data['employee_count'] > 50) & (filtered_data['employee_count'] <= 200)]
        elif company_size == "medium":
            filtered_data = filtered_data[(filtered_data['employee_count'] > 200) & (filtered_data['employee_count'] <= 1000)]
        elif company_size == "large":
            filtered_data = filtered_data[filtered_data['employee_count'] > 1000]
    
    filters = {
        "industry": industry,
        "company_size": company_size
    }
    
    summary = await generate_executive_summary("lead-sources", filtered_data, filters)
    return {"summary": summary, "record_count": len(filtered_data)}

@app.get("/api/summary/observability-adoption")
async def get_observability_adoption_summary(
    industry: Optional[str] = None,
    company_size: Optional[str] = None
):
    """Generate AI executive summary for observability adoption trends"""
    if leads_data is None:
        raise HTTPException(status_code=404, detail="No leads data available")
    
    # Apply filters
    filtered_data = leads_data.copy()
    
    if industry:
        filtered_data = filtered_data[filtered_data['industry'] == industry]
    
    if company_size:
        if company_size == "startup":
            filtered_data = filtered_data[filtered_data['employee_count'] <= 50]
        elif company_size == "small":
            filtered_data = filtered_data[(filtered_data['employee_count'] > 50) & (filtered_data['employee_count'] <= 200)]
        elif company_size == "medium":
            filtered_data = filtered_data[(filtered_data['employee_count'] > 200) & (filtered_data['employee_count'] <= 1000)]
        elif company_size == "large":
            filtered_data = filtered_data[filtered_data['employee_count'] > 1000]
    
    filters = {
        "industry": industry,
        "company_size": company_size
    }
    
    summary = await generate_executive_summary("observability-adoption", filtered_data, filters)
    return {"summary": summary, "record_count": len(filtered_data)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
