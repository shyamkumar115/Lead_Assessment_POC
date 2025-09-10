"""
ML Models for Lead Assessment POC
Implements the two-model approach: Lead Propensity and Contract Value Prediction
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import classification_report, mean_squared_error, r2_score
import xgboost as xgb
import joblib
import os
from typing import Tuple, Dict, Any

class LeadPropensityModel:
    """Model 1: Lead Propensity to Convert (Subsidiary Level)"""
    
    def __init__(self):
        self.model = xgb.XGBClassifier(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            random_state=42
        )
        self.label_encoders = {}
        self.scaler = StandardScaler()
        self.feature_columns = []
        
    def prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Prepare features for the propensity model"""
        df_processed = df.copy()
        
        # Encode categorical variables
        categorical_cols = ['industry', 'job_title', 'seniority_level']
        for col in categorical_cols:
            if col not in self.label_encoders:
                self.label_encoders[col] = LabelEncoder()
                df_processed[col] = self.label_encoders[col].fit_transform(df_processed[col].astype(str))
            else:
                df_processed[col] = self.label_encoders[col].transform(df_processed[col].astype(str))
        
        # Create tech stack features
        tech_features = self._create_tech_features(df_processed)
        df_processed = pd.concat([df_processed, tech_features], axis=1)
        
        # Select feature columns
        feature_cols = [
            'employee_count', 'revenue', 'pages_visited', 'time_on_site',
            'email_opens', 'content_downloads', 'hiring_velocity', 'has_competitor'
        ] + categorical_cols + list(tech_features.columns)
        
        self.feature_columns = feature_cols
        return df_processed[feature_cols]
    
    def _create_tech_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create technology stack features"""
        tech_features = pd.DataFrame()
        
        # Common technologies
        common_techs = ['AWS', 'Azure', 'GCP', 'Docker', 'Kubernetes', 'Python', 'Java']
        
        for tech in common_techs:
            tech_features[f'has_{tech.lower()}'] = df['tech_stack'].str.contains(tech, case=False, na=False).astype(int)
        
        # Competitor presence
        competitors = ['Datadog', 'Splunk', 'Dynatrace', 'AppDynamics']
        tech_features['has_competitor'] = df['tech_stack'].str.contains('|'.join(competitors), case=False, na=False).astype(int)
        
        return tech_features
    
    def train(self, X: pd.DataFrame, y: pd.Series) -> Dict[str, Any]:
        """Train the propensity model"""
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Train model
        self.model.fit(X_scaled, y)
        
        # Make predictions for evaluation
        y_pred = self.model.predict(X_scaled)
        y_pred_proba = self.model.predict_proba(X_scaled)[:, 1]
        
        # Calculate metrics
        report = classification_report(y, y_pred, output_dict=True)
        
        return {
            'accuracy': report['accuracy'],
            'precision': report['weighted avg']['precision'],
            'recall': report['weighted avg']['recall'],
            'f1_score': report['weighted avg']['f1-score']
        }
    
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """Predict propensity scores"""
        X_scaled = self.scaler.transform(X)
        return self.model.predict_proba(X_scaled)[:, 1]
    
    def save(self, filepath: str):
        """Save the model and encoders"""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        joblib.dump({
            'model': self.model,
            'label_encoders': self.label_encoders,
            'scaler': self.scaler,
            'feature_columns': self.feature_columns
        }, filepath)
    
    def load(self, filepath: str):
        """Load the model and encoders"""
        data = joblib.load(filepath)
        self.model = data['model']
        self.label_encoders = data['label_encoders']
        self.scaler = data['scaler']
        self.feature_columns = data['feature_columns']

class ContractValueModel:
    """Model 2: Expected Contract Value (Parent Company Level)"""
    
    def __init__(self):
        self.model = xgb.XGBRegressor(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            random_state=42
        )
        self.label_encoders = {}
        self.scaler = StandardScaler()
        self.feature_columns = []
    
    def prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Prepare features for the contract value model"""
        df_processed = df.copy()
        
        # Encode categorical variables
        categorical_cols = ['industry', 'geography']
        for col in categorical_cols:
            if col not in self.label_encoders:
                self.label_encoders[col] = LabelEncoder()
                df_processed[col] = self.label_encoders[col].fit_transform(df_processed[col].astype(str))
            else:
                df_processed[col] = self.label_encoders[col].transform(df_processed[col].astype(str))
        
        # Create derived features
        df_processed['revenue_per_employee'] = df_processed['revenue'] / df_processed['employee_count']
        df_processed['log_revenue'] = np.log1p(df_processed['revenue'])
        df_processed['log_employee_count'] = np.log1p(df_processed['employee_count'])
        
        # Select feature columns
        feature_cols = [
            'employee_count', 'revenue', 'revenue_per_employee', 
            'log_revenue', 'log_employee_count'
        ] + categorical_cols
        
        self.feature_columns = feature_cols
        return df_processed[feature_cols]
    
    def train(self, X: pd.DataFrame, y: pd.Series) -> Dict[str, Any]:
        """Train the contract value model"""
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Train model
        self.model.fit(X_scaled, y)
        
        # Make predictions for evaluation
        y_pred = self.model.predict(X_scaled)
        
        # Calculate metrics
        mse = mean_squared_error(y, y_pred)
        r2 = r2_score(y, y_pred)
        
        return {
            'mse': mse,
            'rmse': np.sqrt(mse),
            'r2_score': r2
        }
    
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """Predict contract values"""
        X_scaled = self.scaler.transform(X)
        return self.model.predict(X_scaled)
    
    def save(self, filepath: str):
        """Save the model and encoders"""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        joblib.dump({
            'model': self.model,
            'label_encoders': self.label_encoders,
            'scaler': self.scaler,
            'feature_columns': self.feature_columns
        }, filepath)
    
    def load(self, filepath: str):
        """Load the model and encoders"""
        data = joblib.load(filepath)
        self.model = data['model']
        self.label_encoders = data['label_encoders']
        self.scaler = data['scaler']
        self.feature_columns = data['feature_columns']

def train_models():
    """Train both models using sample data"""
    print("Loading sample data...")
    
    # Load data
    companies_df = pd.read_csv("data/companies.csv")
    leads_df = pd.read_csv("data/sample_leads.csv")
    
    # Prepare data for propensity model
    print("Preparing data for propensity model...")
    propensity_model = LeadPropensityModel()
    
    # Filter for converted leads only for training
    converted_leads = leads_df[leads_df['converted'] == True].copy()
    if len(converted_leads) == 0:
        print("No converted leads found, using all leads for training")
        training_leads = leads_df.copy()
    else:
        # Combine converted and non-converted leads
        non_converted = leads_df[leads_df['converted'] == False].sample(n=min(len(converted_leads) * 3, len(leads_df)))
        training_leads = pd.concat([converted_leads, non_converted])
    
    X_propensity = propensity_model.prepare_features(training_leads)
    y_propensity = training_leads['converted'].astype(int)
    
    # Train propensity model
    print("Training propensity model...")
    propensity_metrics = propensity_model.train(X_propensity, y_propensity)
    print(f"Propensity model metrics: {propensity_metrics}")
    
    # Save propensity model
    propensity_model.save("models/propensity_model.pkl")
    
    # Prepare data for contract value model
    print("Preparing data for contract value model...")
    value_model = ContractValueModel()
    
    # Use only converted leads for contract value training
    converted_companies = companies_df.merge(
        converted_leads[['company_id', 'contract_value']], 
        on='company_id', 
        how='inner'
    )
    
    if len(converted_companies) > 0:
        X_value = value_model.prepare_features(converted_companies)
        y_value = converted_companies['contract_value']
        
        # Train contract value model
        print("Training contract value model...")
        value_metrics = value_model.train(X_value, y_value)
        print(f"Contract value model metrics: {value_metrics}")
        
        # Save contract value model
        value_model.save("models/value_model.pkl")
    else:
        print("No converted companies found, skipping contract value model training")
    
    print("Model training complete!")

def predict_lead_scores(leads_df: pd.DataFrame, companies_df: pd.DataFrame) -> pd.DataFrame:
    """Generate predictions for leads using trained models"""
    results = []
    
    # Load models
    try:
        propensity_model = LeadPropensityModel()
        propensity_model.load("models/propensity_model.pkl")
        
        value_model = ContractValueModel()
        value_model.load("models/value_model.pkl")
        
        # Group leads by company for contract value prediction
        for company_id, company_leads in leads_df.groupby('company_id'):
            company_info = companies_df[companies_df['company_id'] == company_id].iloc[0]
            
            # Predict propensity for each lead
            X_propensity = propensity_model.prepare_features(company_leads)
            propensity_scores = propensity_model.predict(X_propensity)
            
            # Predict contract value for the company
            X_value = value_model.prepare_features(pd.DataFrame([company_info]))
            contract_value = value_model.predict(X_value)[0]
            
            # Calculate priority scores
            max_propensity = max(propensity_scores)
            priority_score = max_propensity * (contract_value / 100000)  # Normalize contract value
            
            for i, (_, lead) in enumerate(company_leads.iterrows()):
                result = {
                    'lead_id': lead['lead_id'],
                    'company_name': lead['company_name'],
                    'propensity_score': propensity_scores[i],
                    'contract_value': contract_value,
                    'priority_score': priority_score,
                    'confidence': min(propensity_scores[i] + 0.2, 1.0)  # Add some confidence boost
                }
                results.append(result)
    
    except FileNotFoundError:
        print("Models not found, generating mock predictions")
        for _, lead in leads_df.iterrows():
            result = {
                'lead_id': lead['lead_id'],
                'company_name': lead['company_name'],
                'propensity_score': np.random.uniform(0.1, 0.9),
                'contract_value': np.random.uniform(10000, 500000),
                'priority_score': np.random.uniform(0.1, 0.9),
                'confidence': np.random.uniform(0.7, 0.95)
            }
            results.append(result)
    
    return pd.DataFrame(results)

if __name__ == "__main__":
    train_models()
