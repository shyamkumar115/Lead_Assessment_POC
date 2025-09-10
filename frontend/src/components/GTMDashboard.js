import React, { useState } from 'react';
import { useQuery } from 'react-query';
import { Card, Row, Col, Spin, Alert, Tag, Typography, Select, Space, Statistic, Progress } from 'antd';
import {
  DollarOutlined,
  TrophyOutlined,
  RiseOutlined,
  GlobalOutlined,
  RocketOutlined,
  MessageOutlined,
  ArrowUpOutlined,
  UserOutlined,
  EyeOutlined,
  CheckCircleOutlined
} from '@ant-design/icons';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, PieChart, Pie, Cell, AreaChart, Area } from 'recharts';
import { apiService } from '../services/api';
import ExecutiveSummary from './ExecutiveSummary';

const { Title, Text } = Typography;
const { Option } = Select;

const GTMDashboard = () => {
  const [dashboardFilters, setDashboardFilters] = useState({});
  const [summaryFilters, setSummaryFilters] = useState({});

  // Test API connection first
  const { data: healthCheck } = useQuery(
    'healthCheck',
    async () => {
      const response = await apiService.healthCheck();
      return response.data;
    },
    { 
      retry: false,
      onSuccess: (data) => {
        console.log('Health check successful:', data);
      },
      onError: (error) => {
        console.error('Health check failed:', error);
      }
    }
  );

  const { data: stats, isLoading: statsLoading, error: statsError } = useQuery(
    'leadStats',
    async () => {
      const response = await apiService.getLeadStats();
      return response.data;
    },
    { 
      refetchInterval: 30000,
      onSuccess: (data) => {
        console.log('Stats data received:', data);
      },
      onError: (error) => {
        console.error('Stats API error:', error);
      }
    }
  );

  const { data: metrics, isLoading: metricsLoading, error: metricsError } = useQuery(
    'dashboardMetrics',
    async () => {
      const response = await apiService.getDashboardMetrics();
      return response.data;
    },
    { 
      refetchInterval: 30000,
      onSuccess: (data) => {
        console.log('Metrics data received:', data);
        console.log('Observability adoption data:', data?.observability_adoption);
      },
      onError: (error) => {
        console.error('Metrics API error:', error);
      }
    }
  );

  // GTM Overview Summary Query
  const { data: overviewSummary, isLoading: summaryLoading, error: summaryError } = useQuery(
    ['gtmOverviewSummary', summaryFilters],
    async () => {
      const response = await apiService.getGTMOverviewSummary(summaryFilters);
      return response.data;
    },
    {
      enabled: Object.keys(summaryFilters).length > 0,
      retry: false,
      refetchOnWindowFocus: false
    }
  );

  // Chart-specific summary queries
  const { data: pipelineSummary, isLoading: pipelineSummaryLoading } = useQuery(
    ['pipelineHealthSummary', summaryFilters],
    async () => {
      const response = await apiService.getPipelineHealthSummary(summaryFilters);
      return response.data;
    },
    {
      enabled: Object.keys(summaryFilters).length > 0,
      retry: false,
      refetchOnWindowFocus: false
    }
  );

  const { data: industrySummary, isLoading: industrySummaryLoading } = useQuery(
    ['industryAnalysisSummary', summaryFilters],
    async () => {
      const response = await apiService.getIndustryAnalysisSummary(summaryFilters);
      return response.data;
    },
    {
      enabled: Object.keys(summaryFilters).length > 0,
      retry: false,
      refetchOnWindowFocus: false
    }
  );

  const { data: competitiveSummary, isLoading: competitiveSummaryLoading } = useQuery(
    ['competitiveLandscapeSummary', summaryFilters],
    async () => {
      const response = await apiService.getCompetitiveLandscapeSummary(summaryFilters);
      return response.data;
    },
    {
      enabled: Object.keys(summaryFilters).length > 0,
      retry: false,
      refetchOnWindowFocus: false
    }
  );

  // Product Tier Summary Query
  const { data: productTierSummary, isLoading: productTierSummaryLoading } = useQuery(
    ['productTierSummary', summaryFilters],
    async () => {
      const response = await apiService.getProductTierSummary(summaryFilters);
      return response.data;
    },
    {
      enabled: Object.keys(summaryFilters).length > 0,
      retry: false,
      refetchOnWindowFocus: false
    }
  );

  // Lead Source Summary Query
  const { data: leadSourceSummary, isLoading: leadSourceSummaryLoading } = useQuery(
    ['leadSourceSummary', summaryFilters],
    async () => {
      const response = await apiService.getLeadSourceSummary(summaryFilters);
      return response.data;
    },
    {
      enabled: Object.keys(summaryFilters).length > 0,
      retry: false,
      refetchOnWindowFocus: false
    }
  );


  // Handler for filter changes that trigger summary
  const handleFilterChange = (key, value) => {
    const newFilters = { ...dashboardFilters, [key]: value };
    setDashboardFilters(newFilters);
    
    // Trigger summary when filters change
    if (value) {
      setSummaryFilters(newFilters);
    } else {
      setSummaryFilters({});
    }
  };

  if (statsLoading || metricsLoading) {
    return (
      <div className="loading-spinner">
        <Spin size="large" />
      </div>
    );
  }

  if (statsError || metricsError) {
    return (
      <Alert
        message="Error Loading GTM Dashboard"
        description={`Failed to load dashboard data. Stats Error: ${statsError?.message || 'None'}, Metrics Error: ${metricsError?.message || 'None'}`}
        type="error"
        showIcon
      />
    );
  }


  // Enhanced New Relic GTM Metrics
  const gtmMetrics = [
    {
      title: 'Total Pipeline Value',
      value: stats?.total_pipeline_value || 0,
      prefix: <DollarOutlined style={{ color: '#00AC69' }} />,
      suffix: 'M',
      color: '#00AC69',
      change: '+12.5%',
      changeType: 'positive',
      description: 'Total value of all opportunities',
      icon: <ArrowUpOutlined />
    },
    {
      title: 'Lead Quality Score',
      value: stats?.lead_quality_score || 0,
      prefix: <TrophyOutlined style={{ color: '#1E3A8A' }} />,
      suffix: '%',
      color: '#1E3A8A',
      change: '+8.2%',
      changeType: 'positive',
      description: 'Average lead quality rating',
      icon: <CheckCircleOutlined />
    },
    {
      title: 'Conversion Rate',
      value: (stats?.conversion_rate * 100) || 0,
      prefix: <RiseOutlined style={{ color: '#F59E0B' }} />,
      suffix: '%',
      color: '#F59E0B',
      change: '+3.1%',
      changeType: 'positive',
      description: 'Lead to opportunity conversion',
      icon: <UserOutlined />
    },
    {
      title: 'Avg Deal Size',
      value: (stats?.avg_deal_size / 1000) || 0,
      prefix: <DollarOutlined style={{ color: '#EF4444' }} />,
      suffix: 'K',
      color: '#EF4444',
      change: '+15.7%',
      changeType: 'positive',
      description: 'Average contract value',
      icon: <EyeOutlined />
    }
  ];

  // Transform API data to chart format with enhanced colors
  const productTiers = metrics?.product_tiers?.map(tier => ({
    name: tier.tier,
    value: tier.percentage,
    color: tier.color
  })) || [
    { name: 'Free Tier', value: 35, color: '#E5E7EB' },
    { name: 'Standard', value: 25, color: '#3B82F6' },
    { name: 'Pro', value: 20, color: '#1E3A8A' },
    { name: 'Enterprise', value: 15, color: '#00AC69' },
    { name: 'Full-Stack', value: 5, color: '#F59E0B' }
  ];

  // Transform lead sources data to chart format with enhanced colors
  const leadSources = metrics?.lead_sources?.map(source => ({
    name: source.source,
    value: source.leads,
    color: source.quality === 'High' ? '#00AC69' : source.quality === 'Medium' ? '#F59E0B' : '#EF4444'
  })) || [
    { name: 'Website', value: 40, color: '#00AC69' },
    { name: 'Content Marketing', value: 25, color: '#1E3A8A' },
    { name: 'Events', value: 15, color: '#F59E0B' },
    { name: 'Partners', value: 12, color: '#EF4444' },
    { name: 'Referrals', value: 8, color: '#10B981' }
  ];

  return (
    <div style={{ marginTop: '20px' }} className="fade-in-up">
      {healthCheck && (
        <div style={{ 
          marginBottom: 16, 
          padding: 12, 
          background: 'linear-gradient(135deg, #f6ffed 0%, #e6f7f0 100%)', 
          border: '1px solid #b7eb8f', 
          borderRadius: 8,
          boxShadow: '0 2px 8px rgba(0, 172, 105, 0.1)'
        }} className="slide-in-left">
          <strong>API Status:</strong> Connected ✅ (Backend: {healthCheck.status})
        </div>
      )}

      <div style={{ marginBottom: 32 }} className="fade-in-up">
        <Title level={2} style={{ 
          margin: 0, 
          color: 'var(--nr-gray-900)',
          background: 'var(--nr-primary-gradient)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
          backgroundClip: 'text'
        }}>
          New Relic GTM Intelligence Dashboard
        </Title>
        <Text type="secondary" style={{ fontSize: '16px', color: 'var(--nr-gray-600)' }}>
          Comprehensive lead assessment and revenue optimization platform
        </Text>
      </div>

      {/* Quick Filters */}
      <Card size="small" style={{ marginBottom: 24 }}>
        <Space>
          <span style={{ fontWeight: 500 }}>Quick Filters:</span>
          <Select
            placeholder="Industry"
            style={{ width: 150 }}
            value={dashboardFilters.industry}
            onChange={(value) => handleFilterChange('industry', value)}
            allowClear
          >
            <Option value="Technology">Technology</Option>
            <Option value="Healthcare">Healthcare</Option>
            <Option value="Financial Services">Financial Services</Option>
            <Option value="Manufacturing">Manufacturing</Option>
            <Option value="Retail">Retail</Option>
          </Select>
          <Select
            placeholder="Company Size"
            style={{ width: 150 }}
            value={dashboardFilters.company_size}
            onChange={(value) => handleFilterChange('company_size', value)}
            allowClear
          >
            <Option value="startup">Startup (1-50)</Option>
            <Option value="small">Small (51-200)</Option>
            <Option value="medium">Medium (201-1000)</Option>
            <Option value="large">Large (1000+)</Option>
          </Select>
        </Space>
      </Card>

      {/* AI Executive Summary */}
      <ExecutiveSummary
        summary={overviewSummary?.summary}
        isLoading={summaryLoading}
        error={summaryError?.message}
        recordCount={overviewSummary?.record_count}
        dataType="gtm-overview"
      />

      {/* GTM Strategy Overview Cards */}
      <Row gutter={[24, 24]} style={{ marginBottom: 32 }}>
        <Col span={6}>
          <Card className="gtm-sourcing-card" style={{ height: '100%' }}>
            <div style={{ textAlign: 'center', color: 'white' }}>
              <GlobalOutlined style={{ fontSize: '32px', marginBottom: '12px' }} />
              <Title level={4} style={{ color: 'white', margin: 0 }}>Lead Sourcing</Title>
              <Text style={{ color: 'white', opacity: 0.9 }}>
                Multi-channel attribution and quality assessment
              </Text>
            </div>
          </Card>
        </Col>
        <Col span={6}>
          <Card className="gtm-quality-card" style={{ height: '100%' }}>
            <div style={{ textAlign: 'center', color: 'white' }}>
              <RocketOutlined style={{ fontSize: '32px', marginBottom: '12px' }} />
              <Title level={4} style={{ color: 'white', margin: 0 }}>Lead Scoring</Title>
              <Text style={{ color: 'white', opacity: 0.9 }}>
                AI-powered propensity and engagement scoring
              </Text>
            </div>
          </Card>
        </Col>
        <Col span={6}>
          <Card className="gtm-value-card" style={{ height: '100%' }}>
            <div style={{ textAlign: 'center', color: 'white' }}>
              <DollarOutlined style={{ fontSize: '32px', marginBottom: '12px' }} />
              <Title level={4} style={{ color: 'white', margin: 0 }}>Contract Value</Title>
              <Text style={{ color: 'white', opacity: 0.9 }}>
                Revenue forecasting and deal sizing
              </Text>
            </div>
          </Card>
        </Col>
        <Col span={6}>
          <Card className="gtm-communication-card" style={{ height: '100%' }}>
            <div style={{ textAlign: 'center', color: 'white' }}>
              <MessageOutlined style={{ fontSize: '32px', marginBottom: '12px' }} />
              <Title level={4} style={{ color: 'white', margin: 0 }}>Personalized Outreach</Title>
              <Text style={{ color: 'white', opacity: 0.9 }}>
                AI-generated custom messaging
              </Text>
            </div>
          </Card>
        </Col>
      </Row>

      {/* Key Metrics */}
      <Row gutter={[24, 24]} style={{ marginBottom: 32 }}>
        {gtmMetrics.map((metric, index) => (
          <Col span={6} key={index}>
            <Card className="nr-metric-card fade-in-up" style={{ 
              height: '160px',
              animationDelay: `${index * 0.1}s`
            }}>
              <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
                  <div style={{ color: 'var(--nr-gray-600)', fontSize: '14px', fontWeight: '500' }}>
                    {metric.title}
                  </div>
                  <div style={{ color: metric.color, fontSize: '20px' }}>
                    {metric.icon}
                  </div>
                </div>
                
                <div style={{ flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
                  <div style={{ display: 'flex', alignItems: 'baseline', gap: '8px', marginBottom: '8px' }}>
                    <span style={{ color: metric.color, fontSize: '36px', fontWeight: '700', lineHeight: 1 }}>
                      {metric.value.toLocaleString()}
                    </span>
                    <span style={{ color: 'var(--nr-gray-500)', fontSize: '18px', fontWeight: '500' }}>
                      {metric.suffix}
                    </span>
                  </div>
                  
                  <div style={{ fontSize: '12px', color: 'var(--nr-gray-500)', marginBottom: '8px' }}>
                    {metric.description}
                  </div>
                  
                  <div className={`nr-metric-change ${metric.changeType}`} style={{ 
                    fontSize: '13px', 
                    fontWeight: '600',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '4px'
                  }}>
                    <ArrowUpOutlined style={{ fontSize: '12px' }} />
                    {metric.change} vs last month
                  </div>
                </div>
              </div>
            </Card>
          </Col>
        ))}
      </Row>

      {/* Charts Section */}
      <Row gutter={[24, 24]}>
        <Col span={12}>
          <Card className="nr-card">
            <div className="nr-card-header">
              <Title level={4} className="nr-card-title">Pipeline Growth Trend</Title>
            </div>
            <div className="nr-card-body">
              {/* Pipeline Health Summary */}
              <ExecutiveSummary
                summary={pipelineSummary?.summary}
                isLoading={pipelineSummaryLoading}
                error={null}
                recordCount={pipelineSummary?.record_count}
                dataType="pipeline-health"
              />
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={metrics?.conversion_trend || []}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                  <XAxis dataKey="date" stroke="#666" />
                  <YAxis stroke="#666" />
                  <Tooltip 
                    contentStyle={{ 
                      backgroundColor: 'white', 
                      border: '1px solid #e5e7eb',
                      borderRadius: '8px',
                      boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
                    }} 
                  />
                  <Line 
                    type="monotone" 
                    dataKey="conversion_rate" 
                    stroke="url(#conversionGradient)" 
                    strokeWidth={3}
                    dot={{ fill: '#00AC69', strokeWidth: 2, r: 5 }}
                    activeDot={{ r: 6, stroke: '#00AC69', strokeWidth: 2 }}
                  />
                  <defs>
                    <linearGradient id="conversionGradient" x1="0" y1="0" x2="1" y2="0">
                      <stop offset="0%" stopColor="#00AC69" />
                      <stop offset="100%" stopColor="#00D084" />
                    </linearGradient>
                  </defs>
                </LineChart>
              </ResponsiveContainer>
            </div>
          </Card>
        </Col>
        
        <Col span={12}>
          <Card className="nr-card">
            <div className="nr-card-header">
              <Title level={4} className="nr-card-title">Lead Volume by Source</Title>
            </div>
            <div className="nr-card-body">
              {/* Industry Analysis Summary */}
              <ExecutiveSummary
                summary={industrySummary?.summary}
                isLoading={industrySummaryLoading}
                error={null}
                recordCount={industrySummary?.record_count}
                dataType="industry-analysis"
              />
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={metrics?.lead_volume || []}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                  <XAxis dataKey="date" stroke="#666" />
                  <YAxis stroke="#666" />
                  <Tooltip 
                    contentStyle={{ 
                      backgroundColor: 'white', 
                      border: '1px solid #e5e7eb',
                      borderRadius: '8px',
                      boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
                    }} 
                  />
                  <Bar dataKey="leads" fill="url(#leadGradient)" radius={[4, 4, 0, 0]} />
                  <defs>
                    <linearGradient id="leadGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor="#00D084" />
                      <stop offset="100%" stopColor="#00AC69" />
                    </linearGradient>
                  </defs>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </Card>
        </Col>
      </Row>

      <Row gutter={[24, 24]} style={{ marginTop: 24 }}>
        <Col span={12}>
          <Card className="nr-card">
            <div className="nr-card-header">
              <Title level={4} className="nr-card-title">New Relic Product Tier Distribution</Title>
            </div>
            <div className="nr-card-body">
              {/* Product Tier Summary */}
              <ExecutiveSummary
                summary={productTierSummary?.summary}
                isLoading={productTierSummaryLoading}
                error={null}
                recordCount={productTierSummary?.record_count}
                dataType="product-tiers"
              />
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={productTiers}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {productTiers.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip 
                    contentStyle={{ 
                      backgroundColor: 'white', 
                      border: '1px solid #e5e7eb',
                      borderRadius: '8px',
                      boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
                    }} 
                  />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </Card>
        </Col>
        
        <Col span={12}>
          <Card className="nr-card">
            <div className="nr-card-header">
              <Title level={4} className="nr-card-title">Lead Source Attribution</Title>
            </div>
            <div className="nr-card-body">
              {/* Lead Source Summary */}
              <ExecutiveSummary
                summary={leadSourceSummary?.summary}
                isLoading={leadSourceSummaryLoading}
                error={null}
                recordCount={leadSourceSummary?.record_count}
                dataType="lead-sources"
              />
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={leadSources}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {leadSources.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip 
                    contentStyle={{ 
                      backgroundColor: 'white', 
                      border: '1px solid #e5e7eb',
                      borderRadius: '8px',
                      boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
                    }} 
                  />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </Card>
        </Col>
      </Row>

      {/* New Observability-Focused Charts */}
      <Row gutter={[24, 24]} style={{ marginTop: 24 }}>
        <Col span={12}>
          <Card className="nr-card">
            <div className="nr-card-header">
              <Title level={4} className="nr-card-title">Observability Adoption by Industry</Title>
            </div>
            <div className="nr-card-body">
              <div style={{ height: 300, width: '100%' }}>
                {metrics?.observability_adoption && metrics.observability_adoption.length > 0 ? (
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart 
                      data={metrics.observability_adoption} 
                      margin={{ top: 20, right: 30, left: 20, bottom: 60 }}
                    >
                      <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                      <XAxis 
                        dataKey="industry" 
                        angle={-45} 
                        textAnchor="end" 
                        height={80}
                        tick={{ fontSize: 11 }}
                        interval={0}
                      />
                      <YAxis 
                        domain={[0, 1]} 
                        tickFormatter={(value) => `${(value * 100).toFixed(0)}%`}
                        label={{ value: 'Adoption Rate (%)', angle: -90, position: 'insideLeft' }}
                      />
                      <Tooltip 
                        contentStyle={{ 
                          backgroundColor: 'white', 
                          border: '1px solid #e5e7eb',
                          borderRadius: '8px',
                          boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
                        }}
                        formatter={(value) => [`${(value * 100).toFixed(1)}%`, 'Adoption Rate']}
                        labelFormatter={(label) => `Industry: ${label}`}
                      />
                      <Bar 
                        dataKey="adoption_rate" 
                        fill="url(#adoptionGradient)" 
                        radius={[4, 4, 0, 0]}
                        name="Adoption Rate"
                      />
                      <defs>
                        <linearGradient id="adoptionGradient" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="0%" stopColor="#00D084" />
                          <stop offset="100%" stopColor="#00AC69" />
                        </linearGradient>
                      </defs>
                    </BarChart>
                  </ResponsiveContainer>
                ) : (
                  <div style={{ 
                    height: '100%', 
                    display: 'flex', 
                    alignItems: 'center', 
                    justifyContent: 'center',
                    color: '#666',
                    fontSize: '14px'
                  }}>
                    {metricsLoading ? 'Loading observability data...' : 'No observability adoption data available'}
                  </div>
                )}
              </div>
            </div>
          </Card>
        </Col>
        
        <Col span={12}>
          <Card className="nr-card">
            <div className="nr-card-header">
              <Title level={4} className="nr-card-title">Observability Pain Points</Title>
            </div>
            <div className="nr-card-body">
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={metrics?.pain_points || []}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                  <XAxis dataKey="pain_point" angle={-45} textAnchor="end" height={100} />
                  <YAxis domain={[0, 1]} tickFormatter={(value) => `${(value * 100).toFixed(0)}%`} />
                  <Tooltip 
                    contentStyle={{ 
                      backgroundColor: 'white', 
                      border: '1px solid #e5e7eb',
                      borderRadius: '8px',
                      boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
                    }}
                    formatter={(value) => [`${(value * 100).toFixed(1)}%`, 'Frequency']}
                  />
                  <Bar dataKey="frequency" fill="#F59E0B" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </Card>
        </Col>
      </Row>

      {/* New Relic Value Props */}
      <Row gutter={[24, 24]} style={{ marginTop: 32 }}>
        <Col span={24}>
          <Card className="nr-card">
            <div className="nr-card-header">
              <Title level={4} className="nr-card-title">New Relic Value Proposition Alignment</Title>
            </div>
            <div className="nr-card-body">
              <Row gutter={[16, 16]}>
                <Col span={8}>
                  <div style={{ textAlign: 'center', padding: '16px' }}>
                    <div style={{ fontSize: '24px', marginBottom: '8px' }}>🔍</div>
                    <Title level={5}>Observability</Title>
                    <Text type="secondary">
                      Full-stack observability for modern applications
                    </Text>
                    <div style={{ marginTop: '12px' }}>
                      <Tag color="green">High Interest: 68%</Tag>
                    </div>
                  </div>
                </Col>
                <Col span={8}>
                  <div style={{ textAlign: 'center', padding: '16px' }}>
                    <div style={{ fontSize: '24px', marginBottom: '8px' }}>⚡</div>
                    <Title level={5}>Performance</Title>
                    <Text type="secondary">
                      Real-time performance monitoring and optimization
                    </Text>
                    <div style={{ marginTop: '12px' }}>
                      <Tag color="blue">Medium Interest: 45%</Tag>
                    </div>
                  </div>
                </Col>
                <Col span={8}>
                  <div style={{ textAlign: 'center', padding: '16px' }}>
                    <div style={{ fontSize: '24px', marginBottom: '8px' }}>🛡️</div>
                    <Title level={5}>Security</Title>
                    <Text type="secondary">
                      Application security and compliance monitoring
                    </Text>
                    <div style={{ marginTop: '12px' }}>
                      <Tag color="orange">Growing Interest: 32%</Tag>
                    </div>
                  </div>
                </Col>
              </Row>
            </div>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default GTMDashboard;
