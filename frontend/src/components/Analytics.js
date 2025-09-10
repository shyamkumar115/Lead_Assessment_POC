import React from 'react';
import { useQuery } from 'react-query';
import { Card, Row, Col, Statistic, Spin, Alert } from 'antd';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  ScatterChart,
  Scatter
} from 'recharts';
import { apiService } from '../services/api';

const Analytics = () => {
  const { data: metrics, isLoading, error } = useQuery(
    'dashboardMetrics',
    async () => {
      const response = await apiService.getDashboardMetrics();
      return response.data;
    },
    { 
      refetchInterval: 30000,
      onSuccess: (data) => {
        console.log('Analytics metrics data received:', data);
      },
      onError: (error) => {
        console.error('Analytics metrics API error:', error);
      }
    }
  );

  const { data: stats } = useQuery(
    'leadStats',
    async () => {
      const response = await apiService.getLeadStats();
      return response.data;
    },
    {
      onSuccess: (data) => {
        console.log('Analytics stats data received:', data);
      },
      onError: (error) => {
        console.error('Analytics stats API error:', error);
      }
    }
  );

  if (isLoading) {
    return (
      <div style={{ textAlign: 'center', padding: '50px 0' }}>
        <Spin size="large" />
      </div>
    );
  }

  if (error) {
    return (
      <Alert
        message="Error Loading Analytics"
        description="Failed to load analytics data. Please check your connection and try again."
        type="error"
        showIcon
      />
    );
  }

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

  // Create correlation data for scatter plot
  const correlationData = metrics?.conversion_trend?.map((item, index) => ({
    conversion_rate: item.conversion_rate,
    leads: metrics?.lead_volume?.[index]?.leads || 0,
    month: item.date
  })) || [];

  return (
    <div style={{ marginTop: '20px' }}>
      <h2>Advanced Analytics</h2>
      
      {/* Performance Metrics */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={6}>
          <Card>
            <Statistic
              title="Model Accuracy"
              value={87.3}
              suffix="%"
              precision={1}
              valueStyle={{ color: '#3f8600' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="Prediction Confidence"
              value={92.1}
              suffix="%"
              precision={1}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="Outreach Success Rate"
              value={23.7}
              suffix="%"
              precision={1}
              valueStyle={{ color: '#722ed1' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="Response Rate"
              value={15.2}
              suffix="%"
              precision={1}
              valueStyle={{ color: '#fa8c16' }}
            />
          </Card>
        </Col>
      </Row>

      {/* Advanced Charts */}
      <Row gutter={16}>
        <Col span={12}>
          <Card title="Lead Volume vs Conversion Rate Correlation" style={{ marginBottom: 16 }}>
            <ResponsiveContainer width="100%" height={300}>
              <ScatterChart data={correlationData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="leads" 
                  name="Lead Volume"
                  label={{ value: 'Lead Volume', position: 'insideBottom', offset: -5 }}
                />
                <YAxis 
                  dataKey="conversion_rate" 
                  name="Conversion Rate"
                  label={{ value: 'Conversion Rate (%)', angle: -90, position: 'insideLeft' }}
                />
                <Tooltip 
                  cursor={{ strokeDasharray: '3 3' }}
                  formatter={(value, name) => [value, name === 'conversion_rate' ? 'Conversion Rate (%)' : 'Lead Volume']}
                />
                <Scatter dataKey="conversion_rate" fill="#1890ff" />
              </ScatterChart>
            </ResponsiveContainer>
          </Card>
        </Col>
        
        <Col span={12}>
          <Card title="Observability Adoption by Industry" style={{ marginBottom: 16 }}>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={metrics?.observability_adoption || []}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="industry" angle={-45} textAnchor="end" height={100} />
                <YAxis domain={[0, 1]} tickFormatter={(value) => `${(value * 100).toFixed(0)}%`} />
                <Tooltip 
                  formatter={(value) => [`${(value * 100).toFixed(1)}%`, 'Adoption Rate']}
                />
                <Bar dataKey="adoption_rate" fill="#52c41a" />
              </BarChart>
            </ResponsiveContainer>
          </Card>
        </Col>
      </Row>

      <Row gutter={16}>
        <Col span={12}>
          <Card title="Lead Source Effectiveness">
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={metrics?.lead_sources || []}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="source" angle={-45} textAnchor="end" height={100} />
                <YAxis />
                <Tooltip 
                  formatter={(value, name) => [
                    name === 'leads' ? value : `${(value * 100).toFixed(1)}%`, 
                    name === 'leads' ? 'Lead Count' : 'Conversion Rate'
                  ]}
                />
                <Bar dataKey="leads" fill="#722ed1" />
              </BarChart>
            </ResponsiveContainer>
          </Card>
        </Col>
        
        <Col span={12}>
          <Card title="Model Performance Metrics">
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={[
                { name: 'Precision', value: 0.89 },
                { name: 'Recall', value: 0.85 },
                { name: 'F1-Score', value: 0.87 },
                { name: 'Accuracy', value: 0.87 }
              ]}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis domain={[0, 1]} />
                <Tooltip formatter={(value) => [(value * 100).toFixed(1) + '%', 'Score']} />
                <Bar dataKey="value" fill="#1890ff" />
              </BarChart>
            </ResponsiveContainer>
          </Card>
        </Col>
      </Row>

      {/* Model Insights */}
      <Card title="AI Model Insights" style={{ marginTop: 16 }}>
        <Row gutter={16}>
          <Col span={8}>
            <Card size="small" title="Top Conversion Factors">
              <ul style={{ paddingLeft: 20 }}>
                <li>High engagement score (40% impact)</li>
                <li>Seniority level (25% impact)</li>
                <li>Technology stack match (20% impact)</li>
                <li>Company size (15% impact)</li>
              </ul>
            </Card>
          </Col>
          <Col span={8}>
            <Card size="small" title="Best Performing Industries">
              <ul style={{ paddingLeft: 20 }}>
                <li>Technology (23% conversion)</li>
                <li>Financial Services (19% conversion)</li>
                <li>Healthcare (17% conversion)</li>
                <li>Manufacturing (15% conversion)</li>
              </ul>
            </Card>
          </Col>
          <Col span={8}>
            <Card size="small" title="Optimization Recommendations">
              <ul style={{ paddingLeft: 20 }}>
                <li>Focus on high-engagement leads</li>
                <li>Prioritize senior-level contacts</li>
                <li>Target technology companies</li>
                <li>Improve personalization quality</li>
              </ul>
            </Card>
          </Col>
        </Row>
      </Card>
    </div>
  );
};

export default Analytics;
