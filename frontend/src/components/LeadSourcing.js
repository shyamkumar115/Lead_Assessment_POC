import React, { useState } from 'react';
import { useQuery } from 'react-query';
import { Card, Table, Tag, Statistic, Row, Col, Progress, Alert, Spin } from 'antd';
import { SearchOutlined, UserOutlined, DollarOutlined, CalendarOutlined } from '@ant-design/icons';
import { apiService } from '../services/api';
import ExecutiveSummary from './ExecutiveSummary';

const LeadSourcing = () => {
  const [filters, setFilters] = useState({ limit: 200 });
  const [summaryFilters, setSummaryFilters] = useState({});

  const { data: leads, isLoading, error } = useQuery(
    ['leadSourcingData', filters],
    async () => {
      const response = await apiService.getLeadSourcingData(filters);
      return response.data;
    },
    { 
      refetchInterval: 30000,
      onSuccess: (data) => {
        console.log('Lead sourcing data received:', data);
      },
      onError: (error) => {
        console.error('Lead sourcing API error:', error);
      }
    }
  );

  const { data: summaryData, isLoading: summaryLoading, error: summaryError } = useQuery(
    ['sourcingSummary', summaryFilters],
    async () => {
      const response = await apiService.getSourcingSummary(summaryFilters);
      return response.data;
    },
    {
      enabled: Object.keys(summaryFilters).length > 0, // Only run when filters are applied
      retry: false,
      onSuccess: (data) => {
        console.log('Sourcing summary received:', data);
      },
      onError: (error) => {
        console.error('Sourcing summary API error:', error);
      }
    }
  );


  const getSourcingScoreColor = (score) => {
    if (score >= 0.8) return 'green';
    if (score >= 0.6) return 'orange';
    return 'red';
  };

  const getSourcingScoreText = (score) => {
    if (score >= 0.8) return 'High Potential';
    if (score >= 0.6) return 'Medium Potential';
    return 'Low Potential';
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
      title: 'Sourcing Score',
      dataIndex: 'sourcing_score',
      key: 'sourcing_score',
      render: (score) => (
        <div>
          <Progress 
            percent={Math.round(score * 100)} 
            size="small" 
            strokeColor={getSourcingScoreColor(score)}
            showInfo={false}
          />
          <Tag color={getSourcingScoreColor(score)}>
            {getSourcingScoreText(score)}
          </Tag>
        </div>
      ),
      sorter: (a, b) => a.sourcing_score - b.sourcing_score,
    },
    {
      title: 'Days Since Created',
      dataIndex: 'days_since_created',
      key: 'days_since_created',
      render: (days) => (
        <Tag color={days <= 7 ? 'green' : days <= 30 ? 'orange' : 'red'}>
          {days} days
        </Tag>
      ),
      sorter: (a, b) => a.days_since_created - b.days_since_created,
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
      title: 'Competitor',
      dataIndex: 'competitor_tool',
      key: 'competitor_tool',
      render: (tool) => tool ? <Tag color="red">{tool}</Tag> : <Tag color="green">No Competitor</Tag>,
    },
  ];

  if (isLoading) {
    return (
      <div style={{ textAlign: 'center', padding: '50px 0' }}>
        <Spin size="large" />
        <div style={{ marginTop: 16 }}>Loading lead sourcing data...</div>
      </div>
    );
  }

  if (error) {
    return (
      <Alert
        message="Error Loading Lead Sourcing Data"
        description="Failed to fetch lead sourcing information. Please try again later."
        type="error"
        showIcon
      />
    );
  }

  // Calculate summary statistics
  const totalLeads = leads?.length || 0;
  const highPotentialLeads = leads?.filter(lead => lead.sourcing_score >= 0.8).length || 0;
  const avgSourcingScore = leads?.reduce((sum, lead) => sum + lead.sourcing_score, 0) / totalLeads || 0;
  const newLeads = leads?.filter(lead => lead.days_since_created <= 7).length || 0;

  return (
    <div style={{ marginTop: '20px' }}>
      <Card title="New Relic Lead Sourcing Intelligence" className="nr-card" style={{ marginBottom: 24 }}>
        <div style={{ marginBottom: 16 }}>
          <h3 style={{ margin: 0, color: 'var(--nr-gray-900)' }}>Lead Sourcing & Discovery</h3>
          <p style={{ margin: '8px 0 0 0', color: 'var(--nr-gray-600)' }}>
            Identify high-potential leads and optimize your sourcing strategy
          </p>
        </div>

        {/* Data Filters - Removed for simplified version */}

        {/* AI Executive Summary */}
        <ExecutiveSummary
          summary={summaryData?.summary}
          isLoading={summaryLoading}
          error={summaryError?.message}
          recordCount={summaryData?.record_count}
          dataType="sourcing"
        />

        {/* Summary Statistics */}
        <Row gutter={16} style={{ marginBottom: 24 }}>
          <Col span={6}>
            <Card size="small">
              <Statistic
                title="Total High-Potential Leads"
                value={totalLeads}
                prefix={<SearchOutlined />}
                valueStyle={{ color: 'var(--nr-primary)' }}
              />
            </Card>
          </Col>
          <Col span={6}>
            <Card size="small">
              <Statistic
                title="Premium Prospects"
                value={highPotentialLeads}
                prefix={<UserOutlined />}
                valueStyle={{ color: 'var(--nr-success)' }}
              />
            </Card>
          </Col>
          <Col span={6}>
            <Card size="small">
              <Statistic
                title="Avg Sourcing Score"
                value={Math.round(avgSourcingScore * 100)}
                suffix="%"
                prefix={<DollarOutlined />}
                valueStyle={{ color: 'var(--nr-warning)' }}
              />
            </Card>
          </Col>
          <Col span={6}>
            <Card size="small">
              <Statistic
                title="New Leads (7 days)"
                value={newLeads}
                prefix={<CalendarOutlined />}
                valueStyle={{ color: 'var(--nr-info)' }}
              />
            </Card>
          </Col>
        </Row>

        {/* Lead Sourcing Table */}
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
          scroll={{ x: 1000 }}
          size="middle"
        />
      </Card>
    </div>
  );
};

export default LeadSourcing;
