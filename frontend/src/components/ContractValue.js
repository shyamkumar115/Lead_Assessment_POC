import React, { useState } from 'react';
import { useQuery } from 'react-query';
import { Card, Table, Tag, Statistic, Row, Col, Progress, Alert, Spin } from 'antd';
import { DollarOutlined, RiseOutlined, ReloadOutlined, CrownOutlined } from '@ant-design/icons';
import { apiService } from '../services/api';
import ExecutiveSummary from './ExecutiveSummary';

const ContractValue = () => {
  const [filters, setFilters] = useState({ limit: 200 });
  const [summaryFilters, setSummaryFilters] = useState({});

  const { data: leads, isLoading, error } = useQuery(
    ['contractValueData', filters],
    async () => {
      const response = await apiService.getContractValueData(filters);
      return response.data;
    },
    { 
      refetchInterval: 30000,
      onSuccess: (data) => {
        console.log('Contract value data received:', data);
      },
      onError: (error) => {
        console.error('Contract value API error:', error);
      }
    }
  );

  const { data: summaryData, isLoading: summaryLoading, error: summaryError } = useQuery(
    ['contractValueSummary', summaryFilters],
    async () => {
      const response = await apiService.getContractValueSummary(summaryFilters);
      return response.data;
    },
    {
      enabled: Object.keys(summaryFilters).length > 0,
      retry: false,
      onSuccess: (data) => {
        console.log('Contract value summary received:', data);
      },
      onError: (error) => {
        console.error('Contract value summary API error:', error);
      }
    }
  );


  const getValueTierColor = (tier) => {
    switch (tier) {
      case 'Strategic': return 'purple';
      case 'Enterprise': return 'blue';
      case 'Professional': return 'green';
      case 'Standard': return 'orange';
      default: return 'default';
    }
  };

  const getUpsellColor = (potential) => {
    if (potential >= 0.7) return 'green';
    if (potential >= 0.4) return 'orange';
    return 'red';
  };

  const getRenewalColor = (probability) => {
    if (probability >= 0.8) return 'green';
    if (probability >= 0.6) return 'orange';
    return 'red';
  };

  const formatCurrency = (amount) => {
    if (amount >= 1000000) {
      return `$${(amount / 1000000).toFixed(1)}M`;
    } else if (amount >= 1000) {
      return `$${(amount / 1000).toFixed(0)}K`;
    }
    return `$${amount.toFixed(0)}`;
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
      title: 'Estimated Contract Value',
      dataIndex: 'estimated_contract_value',
      key: 'estimated_contract_value',
      render: (value) => (
        <div>
          <div style={{ fontWeight: 'bold', fontSize: '16px', color: 'var(--nr-primary)' }}>
            {formatCurrency(value)}
          </div>
        </div>
      ),
      sorter: (a, b) => a.estimated_contract_value - b.estimated_contract_value,
    },
    {
      title: 'Value Tier',
      dataIndex: 'value_tier',
      key: 'value_tier',
      render: (tier) => (
        <Tag color={getValueTierColor(tier)} style={{ fontWeight: 'bold' }}>
          {tier}
        </Tag>
      ),
      filters: [
        { text: 'Strategic', value: 'Strategic' },
        { text: 'Enterprise', value: 'Enterprise' },
        { text: 'Professional', value: 'Professional' },
        { text: 'Standard', value: 'Standard' },
      ],
      onFilter: (value, record) => record.value_tier === value,
    },
    {
      title: 'Upsell Potential',
      dataIndex: 'upsell_potential',
      key: 'upsell_potential',
      render: (potential) => (
        <div>
          <Progress 
            percent={Math.round(potential * 100)} 
            size="small" 
            strokeColor={getUpsellColor(potential)}
            showInfo={false}
          />
          <Tag color={getUpsellColor(potential)}>
            {potential >= 0.7 ? 'High' : potential >= 0.4 ? 'Medium' : 'Low'}
          </Tag>
        </div>
      ),
      sorter: (a, b) => a.upsell_potential - b.upsell_potential,
    },
    {
      title: 'Renewal Probability',
      dataIndex: 'renewal_probability',
      key: 'renewal_probability',
      render: (probability) => (
        <div>
          <Progress 
            percent={Math.round(probability * 100)} 
            size="small" 
            strokeColor={getRenewalColor(probability)}
            showInfo={false}
          />
          <Tag color={getRenewalColor(probability)}>
            {probability >= 0.8 ? 'High' : probability >= 0.6 ? 'Medium' : 'Low'}
          </Tag>
        </div>
      ),
      sorter: (a, b) => a.renewal_probability - b.renewal_probability,
    },
    {
      title: 'Company Revenue',
      dataIndex: 'revenue',
      key: 'revenue',
      render: (revenue) => formatCurrency(revenue),
      sorter: (a, b) => a.revenue - b.revenue,
    },
    {
      title: 'Employee Count',
      dataIndex: 'employee_count',
      key: 'employee_count',
      render: (count) => `${count.toLocaleString()}`,
      sorter: (a, b) => a.employee_count - b.employee_count,
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
  ];

  if (isLoading) {
    return (
      <div style={{ textAlign: 'center', padding: '50px 0' }}>
        <Spin size="large" />
        <div style={{ marginTop: 16 }}>Loading contract value data...</div>
      </div>
    );
  }

  if (error) {
    return (
      <Alert
        message="Error Loading Contract Value Data"
        description="Failed to fetch contract value information. Please try again later."
        type="error"
        showIcon
      />
    );
  }

  // Calculate summary statistics
  const totalLeads = leads?.length || 0;
  const totalContractValue = leads?.reduce((sum, lead) => sum + lead.estimated_contract_value, 0) || 0;
  const avgContractValue = totalContractValue / totalLeads || 0;
  const strategicLeads = leads?.filter(lead => lead.value_tier === 'Strategic').length || 0;
  const highUpsellLeads = leads?.filter(lead => lead.upsell_potential >= 0.7).length || 0;

  return (
    <div style={{ marginTop: '20px' }}>
      <Card title="New Relic Contract Value Intelligence" className="nr-card" style={{ marginBottom: 24 }}>
        <div style={{ marginBottom: 16 }}>
          <h3 style={{ margin: 0, color: 'var(--nr-gray-900)' }}>Contract Value & Revenue Optimization</h3>
          <p style={{ margin: '8px 0 0 0', color: 'var(--nr-gray-600)' }}>
            Analyze contract values, upsell opportunities, and renewal probabilities to maximize revenue
          </p>
        </div>

        {/* Data Filters - Removed for simplified version */}

        {/* AI Executive Summary */}
        <ExecutiveSummary
          summary={summaryData?.summary}
          isLoading={summaryLoading}
          error={summaryError?.message}
          recordCount={summaryData?.record_count}
          dataType="contract-value"
        />

        {/* Summary Statistics */}
        <Row gutter={16} style={{ marginBottom: 24 }}>
          <Col span={6}>
            <Card size="small">
              <Statistic
                title="Total Pipeline Value"
                value={formatCurrency(totalContractValue)}
                prefix={<DollarOutlined />}
                valueStyle={{ color: 'var(--nr-primary)' }}
              />
            </Card>
          </Col>
          <Col span={6}>
            <Card size="small">
              <Statistic
                title="Average Contract Value"
                value={formatCurrency(avgContractValue)}
                prefix={<RiseOutlined />}
                valueStyle={{ color: 'var(--nr-success)' }}
              />
            </Card>
          </Col>
          <Col span={6}>
            <Card size="small">
              <Statistic
                title="Strategic Accounts"
                value={strategicLeads}
                prefix={<CrownOutlined />}
                valueStyle={{ color: 'var(--nr-warning)' }}
              />
            </Card>
          </Col>
          <Col span={6}>
            <Card size="small">
              <Statistic
                title="High Upsell Potential"
                value={highUpsellLeads}
                prefix={<ReloadOutlined />}
                valueStyle={{ color: 'var(--nr-info)' }}
              />
            </Card>
          </Col>
        </Row>

        {/* Contract Value Table */}
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

export default ContractValue;
