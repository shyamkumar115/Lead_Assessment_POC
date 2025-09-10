"""
Data Generator for Lead Assessment POC
Generates realistic sample data for testing the ML models and dashboard
"""

import pandas as pd
import numpy as np
from faker import Faker
import random
from datetime import datetime, timedelta
import os

fake = Faker()

# Set random seed for reproducibility
np.random.seed(42)
random.seed(42)

# Industry categories with realistic New Relic adoption rates
INDUSTRIES = [
    "Technology", "Financial Services", "Healthcare", "E-commerce", 
    "SaaS", "Gaming", "Media & Entertainment", "Education Technology",
    "Fintech", "Edtech", "Healthtech", "Retail Technology"
]

# Industry-specific New Relic adoption likelihood (0-1)
INDUSTRY_ADOPTION_RATES = {
    "Technology": 0.85, "Financial Services": 0.75, "Healthcare": 0.65,
    "E-commerce": 0.80, "SaaS": 0.90, "Gaming": 0.70, "Media & Entertainment": 0.75,
    "Education Technology": 0.60, "Fintech": 0.85, "Edtech": 0.70, "Healthtech": 0.75,
    "Retail Technology": 0.70
}

# Job titles by seniority
JOB_TITLES = {
    "Senior": ["VP of Engineering", "Director of IT", "Head of Platform Engineering", "CTO"],
    "Mid": ["Engineering Manager", "DevOps Lead", "Site Reliability Engineer", "Platform Engineer"],
    "Junior": ["Software Engineer", "DevOps Engineer", "System Administrator", "Junior Developer"]
}

# Technology stacks with New Relic focus and realistic adoption patterns
TECH_STACKS = [
    "AWS", "Azure", "GCP", "Docker", "Kubernetes", "Jenkins", "GitLab", "GitHub",
    "Datadog", "Splunk", "Dynatrace", "AppDynamics", "Elastic Stack", "Prometheus", "Grafana", 
    "Jaeger", "Zipkin", "OpenTelemetry", "Python", "Java", "Node.js", "React", "Angular", "Vue.js",
    "Microservices", "Serverless", "Cloud Native", "CI/CD", "Infrastructure as Code"
]

# Current monitoring tools (competitors)
CURRENT_MONITORING_TOOLS = {
    "Datadog": 0.25, "Splunk": 0.20, "Dynatrace": 0.15, "AppDynamics": 0.10,
    "Elastic Stack": 0.15, "Prometheus": 0.10, "Custom Solutions": 0.05
}

# New Relic product adoption likelihood by company size
NR_ADOPTION_BY_SIZE = {
    "startup": 0.30,      # 1-50 employees
    "small": 0.50,        # 51-200 employees  
    "medium": 0.70,       # 201-1000 employees
    "large": 0.85,        # 1001-5000 employees
    "enterprise": 0.90    # 5000+ employees
}

# New Relic competitors and alternatives
COMPETITORS = ["Datadog", "Splunk", "Dynatrace", "AppDynamics", "Sumo Logic", "Elastic Stack", "Prometheus"]

# New Relic product tiers
NR_PRODUCT_TIERS = ["Free", "Standard", "Pro", "Enterprise", "Full-Stack"]

# New Relic value propositions
NR_VALUE_PROPS = [
    "Full-Stack Observability", "Real-time Performance Monitoring", "Application Security", 
    "Infrastructure Monitoring", "Synthetic Monitoring", "Log Management", "Error Tracking",
    "Distributed Tracing", "APM", "Browser Monitoring", "Mobile Monitoring"
]

def calculate_nr_fit_score(tech_stack, employee_count, revenue):
    """Calculate New Relic fit score based on tech stack and company characteristics"""
    score = 50  # Base score
    
    # Tech stack scoring
    cloud_tech = ["AWS", "Azure", "GCP", "Docker", "Kubernetes", "Microservices", "Serverless"]
    monitoring_tech = ["Datadog", "Splunk", "Dynatrace", "AppDynamics", "Prometheus", "Grafana"]
    modern_tech = ["OpenTelemetry", "Jaeger", "Zipkin", "CI/CD", "Infrastructure as Code"]
    
    for tech in tech_stack:
        if tech in cloud_tech:
            score += 10
        elif tech in monitoring_tech:
            score += 15  # Higher score for existing monitoring tools (migration opportunity)
        elif tech in modern_tech:
            score += 8
    
    # Company size scoring
    if employee_count > 1000:
        score += 15
    elif employee_count > 500:
        score += 10
    elif employee_count > 100:
        score += 5
    
    # Revenue scoring
    if revenue > 100_000_000:  # $100M+
        score += 10
    elif revenue > 10_000_000:  # $10M+
        score += 5
    
    return min(100, max(0, score))

def recommend_nr_tier(employee_count, revenue, fit_score):
    """Recommend New Relic product tier based on company characteristics"""
    if employee_count > 1000 and revenue > 50_000_000 and fit_score > 80:
        return "Full-Stack"
    elif employee_count > 500 and revenue > 10_000_000 and fit_score > 70:
        return "Enterprise"
    elif employee_count > 100 and revenue > 1_000_000 and fit_score > 60:
        return "Pro"
    elif employee_count > 50 and revenue > 500_000:
        return "Standard"
    else:
        return "Free"

def generate_realistic_tech_stack(employee_count, industry):
    """Generate realistic tech stack based on company size and industry"""
    # Base tech stack that most companies have
    base_tech = ["AWS", "Docker", "Python", "GitHub"]
    
    # Size-based additions
    if employee_count > 500:
        base_tech.extend(["Kubernetes", "Microservices", "CI/CD"])
    if employee_count > 100:
        base_tech.extend(["Jenkins", "Java", "Node.js"])
    
    # Industry-specific additions
    if industry in ["Technology", "SaaS", "Fintech"]:
        base_tech.extend(["React", "Angular", "Serverless", "Cloud Native"])
    elif industry in ["Healthcare", "Financial Services"]:
        base_tech.extend(["Azure", "Java", "Infrastructure as Code"])
    elif industry in ["Gaming", "Media & Entertainment"]:
        base_tech.extend(["GCP", "Vue.js", "OpenTelemetry"])
    
    # Add 1-3 random additional technologies
    additional_tech = random.sample(
        [t for t in TECH_STACKS if t not in base_tech], 
        min(random.randint(1, 3), len([t for t in TECH_STACKS if t not in base_tech]))
    )
    
    return base_tech + additional_tech

def calculate_realistic_nr_fit_score(tech_stack, employee_count, revenue, industry, competitor_tool):
    """Calculate realistic New Relic fit score based on multiple factors"""
    score = 40  # Base score
    
    # Tech stack scoring (more realistic weights)
    cloud_tech = ["AWS", "Azure", "GCP"]
    container_tech = ["Docker", "Kubernetes"]
    modern_tech = ["Microservices", "Serverless", "Cloud Native", "OpenTelemetry"]
    languages = ["Python", "Java", "Node.js", "React", "Angular"]
    
    for tech in tech_stack:
        if tech in cloud_tech:
            score += 6  # Cloud adoption is key
        elif tech in container_tech:
            score += 8  # Container adoption is very important
        elif tech in modern_tech:
            score += 7  # Modern architecture is important
        elif tech in languages:
            score += 3  # Language support
        else:
            score += 1
    
    # Company size scoring (realistic for New Relic)
    if employee_count > 5000:
        score += 20  # Enterprise
    elif employee_count > 1000:
        score += 15  # Large
    elif employee_count > 500:
        score += 10  # Medium
    elif employee_count > 100:
        score += 5   # Small
    
    # Industry scoring
    industry_score = INDUSTRY_ADOPTION_RATES.get(industry, 0.5) * 15
    score += industry_score
    
    # Competitor tool scoring (pain points)
    if competitor_tool in ["Datadog", "Splunk"]:
        score += 8  # High switching potential
    elif competitor_tool in ["Dynatrace", "AppDynamics"]:
        score += 5  # Medium switching potential
    elif competitor_tool == "Custom Solutions":
        score += 10  # High pain point
    
    # Revenue scoring (realistic thresholds)
    if revenue > 100_000_000:
        score += 12  # Enterprise budget
    elif revenue > 50_000_000:
        score += 8   # Large budget
    elif revenue > 10_000_000:
        score += 5   # Medium budget
    
    return min(max(score, 0), 100)

def calculate_realistic_contract_value(employee_count, revenue, nr_tier, industry):
    """Calculate realistic New Relic contract value based on actual pricing"""
    # Base pricing per employee (realistic New Relic pricing)
    base_price_per_employee = {
        "Free": 0,
        "Standard": 25,      # $25/user/month
        "Pro": 50,           # $50/user/month  
        "Enterprise": 100,   # $100/user/month
        "Full-Stack": 150    # $150/user/month
    }
    
    # Calculate base value
    base_value = employee_count * base_price_per_employee.get(nr_tier, 50) * 12  # Annual
    
    # Industry multipliers (realistic for observability spend)
    industry_multipliers = {
        "Financial Services": 1.5,  # High compliance needs
        "Healthcare": 1.3,          # Regulatory requirements
        "Technology": 1.2,          # High tech adoption
        "SaaS": 1.4,               # Critical for SaaS
        "Fintech": 1.6,            # High security needs
        "Gaming": 1.1,             # Performance critical
        "Media & Entertainment": 1.2,
        "E-commerce": 1.3,         # High availability needs
    }
    
    multiplier = industry_multipliers.get(industry, 1.0)
    contract_value = base_value * multiplier
    
    # Realistic contract value ranges
    if nr_tier == "Free":
        contract_value = 0
    elif nr_tier == "Standard":
        contract_value = max(5000, min(contract_value, 50000))
    elif nr_tier == "Pro":
        contract_value = max(15000, min(contract_value, 150000))
    elif nr_tier == "Enterprise":
        contract_value = max(50000, min(contract_value, 500000))
    elif nr_tier == "Full-Stack":
        contract_value = max(100000, min(contract_value, 1000000))
    
    return int(contract_value)

def generate_company_data(n_companies=1000):
    """Generate company/account data"""
    companies = []
    
    for i in range(n_companies):
        company = {
            "company_id": f"COMP_{i:06d}",
            "company_name": fake.company(),
            "industry": random.choice(INDUSTRIES),
            "employee_count": random.choice([50, 100, 250, 500, 1000, 2500, 5000, 10000]),
            "revenue": random.uniform(1000000, 1000000000),
            "parent_company": fake.company() if random.random() > 0.7 else None,
            "geography": random.choice(["North America", "Europe", "Asia", "Other"]),
            "created_date": fake.date_between(start_date='-2y', end_date='today')
        }
        companies.append(company)
    
    return pd.DataFrame(companies)

def generate_lead_data(n_leads=5000, companies_df=None):
    """Generate lead/contact data"""
    leads = []
    
    for i in range(n_leads):
        # Select a random company
        company = companies_df.sample(1).iloc[0]
        
        # Generate job title based on seniority
        seniority = random.choices(["Senior", "Mid", "Junior"], weights=[0.2, 0.5, 0.3])[0]
        job_title = random.choice(JOB_TITLES[seniority])
        
        # Generate realistic engagement metrics based on company size and industry
        industry_adoption = INDUSTRY_ADOPTION_RATES.get(company["industry"], 0.5)
        company_size_factor = min(company["employee_count"] / 1000, 1.0)
        
        # More realistic engagement based on company characteristics
        base_engagement = industry_adoption * company_size_factor
        pages_visited = int(random.gauss(15 * base_engagement, 5))
        pages_visited = max(1, min(pages_visited, 50))
        
        time_on_site = int(random.gauss(300 * base_engagement, 100))  # seconds
        time_on_site = max(30, min(time_on_site, 1800))
        
        email_opens = int(random.gauss(3 * base_engagement, 2))
        email_opens = max(0, min(email_opens, 15))
        
        content_downloads = int(random.gauss(2 * base_engagement, 1))
        content_downloads = max(0, min(content_downloads, 8))
        
        # Generate hiring velocity based on company growth stage
        if company["employee_count"] < 100:
            hiring_velocity = random.randint(0, 5)  # Early stage
        elif company["employee_count"] < 500:
            hiring_velocity = random.randint(2, 15)  # Growth stage
        else:
            hiring_velocity = random.randint(5, 25)  # Scale stage
        
        # Generate tech stack based on company size and industry
        tech_stack = generate_realistic_tech_stack(company["employee_count"], company["industry"])
        
        # Current monitoring tool based on realistic market share
        competitor_tool = random.choices(
            list(CURRENT_MONITORING_TOOLS.keys()),
            weights=list(CURRENT_MONITORING_TOOLS.values())
        )[0]
        has_competitor = competitor_tool != "Custom Solutions"
        
        # New Relic fit score based on realistic factors
        nr_fit_score = calculate_realistic_nr_fit_score(
            tech_stack, company["employee_count"], company["revenue"], 
            company["industry"], competitor_tool
        )
        
        # New Relic product tier recommendation
        nr_tier = recommend_nr_tier(company["employee_count"], company["revenue"], nr_fit_score)
        
        # Generate conversion outcome based on realistic New Relic conversion rates
        base_conversion = 0.12  # 12% industry average
        industry_boost = industry_adoption * 0.05  # Up to 5% boost for high-adoption industries
        size_boost = company_size_factor * 0.03   # Up to 3% boost for larger companies
        fit_boost = (nr_fit_score / 100) * 0.08   # Up to 8% boost for high fit
        
        conversion_prob = base_conversion + industry_boost + size_boost + fit_boost
        conversion_prob = min(conversion_prob, 0.35)  # Cap at 35%
        converted = random.random() < conversion_prob
        
        # Generate realistic contract value based on New Relic pricing
        if converted:
            contract_value = calculate_realistic_contract_value(
                company["employee_count"], company["revenue"], nr_tier, company["industry"]
            )
        else:
            contract_value = 0
        
        lead = {
            "lead_id": f"LEAD_{i:06d}",
            "company_id": company["company_id"],
            "company_name": company["company_name"],
            "contact_name": fake.name(),
            "email": fake.email(),
            "job_title": job_title,
            "seniority_level": seniority,
            "industry": company["industry"],
            "employee_count": company["employee_count"],
            "revenue": company["revenue"],
            "pages_visited": pages_visited,
            "time_on_site": time_on_site,
            "email_opens": email_opens,
            "content_downloads": content_downloads,
            "hiring_velocity": hiring_velocity,
            "tech_stack": ", ".join(tech_stack),
            "has_competitor": has_competitor,
            "competitor_tool": competitor_tool,
            "nr_fit_score": nr_fit_score,
            "nr_tier": nr_tier,
            "converted": converted,
            "contract_value": contract_value,
            "created_date": fake.date_between(start_date='-1y', end_date='today'),
            "last_activity": fake.date_between(start_date='-30d', end_date='today')
        }
        leads.append(lead)
    
    return pd.DataFrame(leads)

def generate_engagement_data(leads_df, n_events=10000):
    """Generate detailed engagement events"""
    events = []
    
    event_types = ["page_view", "email_open", "email_click", "content_download", "demo_request"]
    pages = ["home", "pricing", "features", "case_studies", "about", "contact"]
    
    for i in range(n_events):
        lead = leads_df.sample(1).iloc[0]
        
        event = {
            "event_id": f"EVENT_{i:06d}",
            "lead_id": lead["lead_id"],
            "company_id": lead["company_id"],
            "event_type": random.choice(event_types),
            "page": random.choice(pages) if random.choice(event_types) == "page_view" else None,
            "timestamp": fake.date_time_between(start_date='-6m', end_date='now'),
            "session_id": f"SESS_{random.randint(100000, 999999)}"
        }
        events.append(event)
    
    return pd.DataFrame(events)

def create_sample_data():
    """Create all sample data files"""
    print("Generating sample data...")
    
    # Create directories
    os.makedirs("data", exist_ok=True)
    os.makedirs("models", exist_ok=True)
    
    # Generate companies
    print("Generating company data...")
    companies_df = generate_company_data(1000)
    companies_df.to_csv("data/companies.csv", index=False)
    
    # Generate leads
    print("Generating lead data...")
    leads_df = generate_lead_data(5000, companies_df)
    leads_df.to_csv("data/sample_leads.csv", index=False)
    
    # Generate engagement events
    print("Generating engagement data...")
    events_df = generate_engagement_data(leads_df, 10000)
    events_df.to_csv("data/engagement_events.csv", index=False)
    
    # Create a summary dataset for the API
    summary_df = leads_df[['company_name', 'industry', 'employee_count', 'revenue', 
                          'job_title', 'seniority_level', 'pages_visited', 'time_on_site',
                          'email_opens', 'content_downloads', 'hiring_velocity', 
                          'tech_stack', 'has_competitor']].copy()
    summary_df.to_csv("data/api_leads.csv", index=False)
    
    print("Sample data generation complete!")
    print(f"Generated {len(companies_df)} companies")
    print(f"Generated {len(leads_df)} leads")
    print(f"Generated {len(events_df)} engagement events")
    
    return companies_df, leads_df, events_df

if __name__ == "__main__":
    create_sample_data()
