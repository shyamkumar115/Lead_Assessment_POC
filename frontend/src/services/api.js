import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // Increased from 10s to 30s
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    console.log(`Making ${config.method?.toUpperCase()} request to ${config.baseURL}${config.url}`);
    console.log('Request config:', config);
    return config;
  },
  (error) => {
    console.error('Request interceptor error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => {
    console.log(`API Response: ${response.status} for ${response.config.url}`);
    return response;
  },
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    console.error('Error details:', error);
    return Promise.reject(error);
  }
);

export const apiService = {
  // Health check
  healthCheck: () => api.get('/health'),

  // Lead data
  getLeads: (limit = 100) => api.get(`/api/leads?limit=${limit}`),
  getLeadStats: () => api.get('/api/leads/stats'),
  
  // Specialized lead data for different pages
  getLeadSourcingData: (filters = {}) => {
    const params = new URLSearchParams();
    params.append('limit', filters.limit || 100);
    if (filters.industry) params.append('industry', filters.industry);
    if (filters.min_employee_count) params.append('min_employee_count', filters.min_employee_count);
    if (filters.max_employee_count) params.append('max_employee_count', filters.max_employee_count);
    if (filters.min_sourcing_score) params.append('min_sourcing_score', filters.min_sourcing_score);
    if (filters.max_sourcing_score) params.append('max_sourcing_score', filters.max_sourcing_score);
    if (filters.days_since_created_max) params.append('days_since_created_max', filters.days_since_created_max);
    return api.get(`/api/leads/sourcing?${params.toString()}`);
  },
  
  getLeadScoringData: (filters = {}) => {
    const params = new URLSearchParams();
    params.append('limit', filters.limit || 100);
    if (filters.industry) params.append('industry', filters.industry);
    if (filters.min_conversion_probability) params.append('min_conversion_probability', filters.min_conversion_probability);
    if (filters.max_conversion_probability) params.append('max_conversion_probability', filters.max_conversion_probability);
    if (filters.min_engagement_score) params.append('min_engagement_score', filters.min_engagement_score);
    if (filters.max_engagement_score) params.append('max_engagement_score', filters.max_engagement_score);
    if (filters.min_urgency_score) params.append('min_urgency_score', filters.min_urgency_score);
    if (filters.max_urgency_score) params.append('max_urgency_score', filters.max_urgency_score);
    if (filters.min_composite_score) params.append('min_composite_score', filters.min_composite_score);
    if (filters.max_composite_score) params.append('max_composite_score', filters.max_composite_score);
    return api.get(`/api/leads/scoring?${params.toString()}`);
  },
  
  getContractValueData: (filters = {}) => {
    const params = new URLSearchParams();
    params.append('limit', filters.limit || 100);
    if (filters.industry) params.append('industry', filters.industry);
    if (filters.value_tier) params.append('value_tier', filters.value_tier);
    if (filters.min_contract_value) params.append('min_contract_value', filters.min_contract_value);
    if (filters.max_contract_value) params.append('max_contract_value', filters.max_contract_value);
    if (filters.min_upsell_potential) params.append('min_upsell_potential', filters.min_upsell_potential);
    if (filters.max_upsell_potential) params.append('max_upsell_potential', filters.max_upsell_potential);
    if (filters.min_renewal_probability) params.append('min_renewal_probability', filters.min_renewal_probability);
    if (filters.max_renewal_probability) params.append('max_renewal_probability', filters.max_renewal_probability);
    return api.get(`/api/leads/contract-value?${params.toString()}`);
  },

  // Predictions
  predictLeads: (leads) => api.post('/api/predict', { leads }),

  // Outreach generation
  generateOutreach: (outreachData) => api.post('/api/outreach/generate', outreachData),

  // Dashboard metrics
  getDashboardMetrics: () => api.get('/api/dashboard/metrics'),

  // AI Summary endpoints
  getSourcingSummary: (filters = {}) => {
    const params = new URLSearchParams();
    if (filters.industry) params.append('industry', filters.industry);
    if (filters.min_employee_count) params.append('min_employee_count', filters.min_employee_count);
    if (filters.max_employee_count) params.append('max_employee_count', filters.max_employee_count);
    if (filters.min_sourcing_score) params.append('min_sourcing_score', filters.min_sourcing_score);
    if (filters.max_sourcing_score) params.append('max_sourcing_score', filters.max_sourcing_score);
    if (filters.days_since_created_max) params.append('days_since_created_max', filters.days_since_created_max);
    return api.get(`/api/summary/sourcing?${params.toString()}`);
  },

  getScoringSummary: (filters = {}) => {
    const params = new URLSearchParams();
    if (filters.industry) params.append('industry', filters.industry);
    if (filters.min_conversion_probability) params.append('min_conversion_probability', filters.min_conversion_probability);
    if (filters.max_conversion_probability) params.append('max_conversion_probability', filters.max_conversion_probability);
    if (filters.min_engagement_score) params.append('min_engagement_score', filters.min_engagement_score);
    if (filters.max_engagement_score) params.append('max_engagement_score', filters.max_engagement_score);
    if (filters.min_urgency_score) params.append('min_urgency_score', filters.min_urgency_score);
    if (filters.max_urgency_score) params.append('max_urgency_score', filters.max_urgency_score);
    if (filters.min_composite_score) params.append('min_composite_score', filters.min_composite_score);
    if (filters.max_composite_score) params.append('max_composite_score', filters.max_composite_score);
    return api.get(`/api/summary/scoring?${params.toString()}`);
  },

  getContractValueSummary: (filters = {}) => {
    const params = new URLSearchParams();
    if (filters.industry) params.append('industry', filters.industry);
    if (filters.value_tier) params.append('value_tier', filters.value_tier);
    if (filters.min_contract_value) params.append('min_contract_value', filters.min_contract_value);
    if (filters.max_contract_value) params.append('max_contract_value', filters.max_contract_value);
    if (filters.min_upsell_potential) params.append('min_upsell_potential', filters.min_upsell_potential);
    if (filters.max_upsell_potential) params.append('max_upsell_potential', filters.max_upsell_potential);
    if (filters.min_renewal_probability) params.append('min_renewal_probability', filters.min_renewal_probability);
    if (filters.max_renewal_probability) params.append('max_renewal_probability', filters.max_renewal_probability);
    return api.get(`/api/summary/contract-value?${params.toString()}`);
  },

  // GTM Overview Summary
  getGTMOverviewSummary: (filters = {}) => {
    const params = new URLSearchParams();
    if (filters.industry) params.append('industry', filters.industry);
    if (filters.company_size) params.append('company_size', filters.company_size);
    return api.get(`/api/summary/gtm-overview?${params.toString()}`);
  },

  // Chart-specific summaries
  getPipelineHealthSummary: (filters = {}) => {
    const params = new URLSearchParams();
    if (filters.industry) params.append('industry', filters.industry);
    if (filters.company_size) params.append('company_size', filters.company_size);
    return api.get(`/api/summary/pipeline-health?${params.toString()}`);
  },

  getIndustryAnalysisSummary: (filters = {}) => {
    const params = new URLSearchParams();
    if (filters.industry) params.append('industry', filters.industry);
    if (filters.company_size) params.append('company_size', filters.company_size);
    return api.get(`/api/summary/industry-analysis?${params.toString()}`);
  },

  getCompetitiveLandscapeSummary: (filters = {}) => {
    const params = new URLSearchParams();
    if (filters.industry) params.append('industry', filters.industry);
    if (filters.company_size) params.append('company_size', filters.company_size);
    return api.get(`/api/summary/competitive-landscape?${params.toString()}`);
  },

  getProductTierSummary: (filters = {}) => {
    const params = new URLSearchParams();
    if (filters.industry) params.append('industry', filters.industry);
    if (filters.company_size) params.append('company_size', filters.company_size);
    return api.get(`/api/summary/product-tiers?${params.toString()}`);
  },

  getLeadSourceSummary: (filters = {}) => {
    const params = new URLSearchParams();
    if (filters.industry) params.append('industry', filters.industry);
    if (filters.company_size) params.append('company_size', filters.company_size);
    return api.get(`/api/summary/lead-sources?${params.toString()}`);
  },

  getObservabilityAdoptionSummary: (filters = {}) => {
    const params = new URLSearchParams();
    if (filters.industry) params.append('industry', filters.industry);
    if (filters.company_size) params.append('company_size', filters.company_size);
    return api.get(`/api/summary/observability-adoption?${params.toString()}`);
  },
};

export default api;
