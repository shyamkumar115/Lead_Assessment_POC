import React, { useState } from 'react';
import { useQuery } from 'react-query';
import { Card, Table, Tag, Statistic, Row, Col, Progress, Alert, Spin } from 'antd';
import { TrophyOutlined, FireOutlined, HeartOutlined, StarOutlined } from '@ant-design/icons';
import { apiService } from '../services/api';
import ExecutiveSummary from './ExecutiveSummary';

const LeadScoring = () => {
  const [filters, setFilters] = useState({ limit: 200 });
  const [summaryFilters, setSummaryFilters] = useState({});

  const { data: leads, isLoading, error } = useQuery(
    ['leadScoringData', filters],
    async () => {
      const response = await apiService.getLeadScoringData(filters);
      return response.data;
    },
    { 
      refetchInterval: 30000,
      onSuccess: (data) => {
        console.log('Lead scoring data received:', data);
      },
      onError: (error) => {
        console.error('Lead scoring API error:', error);
      }
    }
  );

  const { data: summaryData, isLoading: summaryLoading, error: summaryError } = useQuery(
    ['scoringSummary', summaryFilters],
    async () => {
      const response = await apiService.getScoringSummary(summaryFilters);
      return response.data;
    },
    {
      enabled: Object.keys(summaryFilters).length > 0,
      retry: false,
      onSuccess: (data) => {
        console.log('Scoring summary received:', data);
      },
      onError: (error) => {
        console.error('Scoring summary API error:', error);
      }
    }
  );


  const getScoreColor = (score) => {
    if (score >= 0.8) return 'green';
    if (score >= 0.6) return 'orange';
    return 'red';
  };

  const getScoreText = (score) => {
    if (score >= 0.8) return 'Hot Lead';
    if (score >= 0.6) return 'Warm Lead';
    return 'Cold Lead';
  };

  const getEngagementColor = (score) => {
    if (score >= 0.7) return 'green';
    if (score >= 0.4) return 'orange';
    return 'red';
  };

  const getUrgencyColor = (score) => {
    if (score >= 0.7) return 'red';
    if (score >= 0.4) return 'orange';
    return 'green';
  };

  const columns = [
    {
      title: 'Company',
      dataIndex: 'company_name',
      key: 'company_name',
      render: (text, record) => (
        <div>
          <div style={{ fontWeight: 'bold' }}>{text}</div>
          <div style={{ fontSize: '12px', color: '#666' }}>{record.industry}</div>
        </div>
      ),
    },
    {
      title: 'Composite Score',
      dataIndex: 'composite_score',
      key: 'composite_score',
      render: (score) => (
        <div>
          <Progress 
            percent={Math.round(score * 100)} 
            size="small" 
            strokeColor={getScoreColor(score)}
            showInfo={false}
          />
          <Tag color={getScoreColor(score)}>
            {getScoreText(score)}
          </Tag>
        </div>
      ),
      sorter: (a, b) => a.composite_score - b.composite_score,
    },
    {
      title: 'Conversion Probability',
      dataIndex: 'conversion_probability',
      key: 'conversion_probability',
      render: (prob) => (
        <div>
          <Progress 
            percent={Math.round(prob * 100)} 
            size="small" 
            strokeColor={getScoreColor(prob)}
            showInfo={false}
          />
          <span style={{ fontSize: '12px' }}>{Math.round(prob * 100)}%</span>
        </div>
      ),
      sorter: (a, b) => a.conversion_probability - b.conversion_probability,
    },
    {
      title: 'Engagement Score',
      dataIndex: 'engagement_score',
      key: 'engagement_score',
      render: (score) => (
        <div>
          <Progress 
            percent={Math.round(score * 100)} 
            size="small" 
            strokeColor={getEngagementColor(score)}
            showInfo={false}
          />
          <Tag color={getEngagementColor(score)}>
            {score >= 0.7 ? 'High' : score >= 0.4 ? 'Medium' : 'Low'}
          </Tag>
        </div>
      ),
      sorter: (a, b) => a.engagement_score - b.engagement_score,
    },
    {
      title: 'Urgency Score',
      dataIndex: 'urgency_score',
      key: 'urgency_score',
      render: (score) => (
        <div>
          <Progress 
            percent={Math.round(score * 100)} 
            size="small" 
            strokeColor={getUrgencyColor(score)}
            showInfo={false}
          />
          <Tag color={getUrgencyColor(score)}>
            {score >= 0.7 ? 'Urgent' : score >= 0.4 ? 'Moderate' : 'Low'}
          </Tag>
        </div>
      ),
      sorter: (a, b) => a.urgency_score - b.urgency_score,
    },
    {
      title: 'NR Fit Score',
      dataIndex: 'nr_fit_score',
      key: 'nr_fit_score',
      render: (score) => (
        <Progress 
          percent={Math.round(score * 100)} 
          size="small" 
          strokeColor={score >= 0.7 ? 'green' : score >= 0.5 ? 'orange' : 'red'}
        />
      ),
      sorter: (a, b) => a.nr_fit_score - b.nr_fit_score,
    },
    {
      title: 'Company Size',
      dataIndex: 'employee_count',
      key: 'employee_count',
      render: (count) => `${count.toLocaleString()} employees`,
      sorter: (a, b) => a.employee_count - b.employee_count,
    },
    {
      title: 'Revenue',
      dataIndex: 'revenue',
      key: 'revenue',
      render: (revenue) => `$${(revenue / 1000000).toFixed(1)}M`,
      sorter: (a, b) => a.revenue - b.revenue,
    },
  ];

  if (isLoading) {
    return (
      <div style={{ textAlign: 'center', padding: '50px 0' }}>
        <Spin size="large" />
        <div style={{ marginTop: 16 }}>Loading lead scoring data...</div>
      </div>
    );
  }

  if (error) {
    return (
      <Alert
        message="Error Loading Lead Scoring Data"
        description="Failed to fetch lead scoring information. Please try again later."
        type="error"
        showIcon
      />
    );
  }

  // Calculate summary statistics
  const totalLeads = leads?.length || 0;
  const hotLeads = leads?.filter(lead => lead.composite_score >= 0.8).length || 0;
  const warmLeads = leads?.filter(lead => lead.composite_score >= 0.6 && lead.composite_score < 0.8).length || 0;
  const avgConversionProb = leads?.reduce((sum, lead) => sum + lead.conversion_probability, 0) / totalLeads || 0;

  return (
    <div style={{ marginTop: '20px' }}>
      <Card title="New Relic Lead Scoring Intelligence" className="nr-card" style={{ marginBottom: 24 }}>
        <div style={{ marginBottom: 16 }}>
          <h3 style={{ margin: 0, color: 'var(--nr-gray-900)' }}>Lead Scoring & Qualification</h3>
          <p style={{ margin: '8px 0 0 0', color: 'var(--nr-gray-600)' }}>
            Advanced lead scoring to prioritize your sales efforts and maximize conversion rates
          </p>
        </div>

        {/* Data Filters - Removed for simplified version */}

        {/* AI Executive Summary */}
        <ExecutiveSummary
          summary={summaryData?.summary}
          isLoading={summaryLoading}
          error={summaryError?.message}
          recordCount={summaryData?.record_count}
          dataType="scoring"
        />

        {/* Summary Statistics */}
        <Row gutter={16} style={{ marginBottom: 24 }}>
          <Col span={6}>
            <Card size="small">
              <Statistic
                title="Total Scored Leads"
                value={totalLeads}
                prefix={<TrophyOutlined />}
                valueStyle={{ color: 'var(--nr-primary)' }}
              />
            </Card>
          </Col>
          <Col span={6}>
            <Card size="small">
              <Statistic
                title="Hot Leads"
                value={hotLeads}
                prefix={<FireOutlined />}
                valueStyle={{ color: 'var(--nr-error)' }}
              />
            </Card>
          </Col>
          <Col span={6}>
            <Card size="small">
              <Statistic
                title="Warm Leads"
                value={warmLeads}
                prefix={<HeartOutlined />}
                valueStyle={{ color: 'var(--nr-warning)' }}
              />
            </Card>
          </Col>
          <Col span={6}>
            <Card size="small">
              <Statistic
                title="Avg Conversion Rate"
                value={Math.round(avgConversionProb * 100)}
                suffix="%"
                prefix={<StarOutlined />}
                valueStyle={{ color: 'var(--nr-success)' }}
              />
            </Card>
          </Col>
        </Row>

        {/* Lead Scoring Table */}
        <Table
          columns={columns}
          dataSource={leads}
          rowKey="id"
          pagination={{
            pageSize: 20,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total, range) => `${range[0]}-${range[1]} of ${total} leads`,
          }}
          scroll={{ x: 1200 }}
          size="middle"
        />
      </Card>
    </div>
  );
};

export default LeadScoring;
