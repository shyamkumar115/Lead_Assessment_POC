import React from 'react';
import { Card, Spin, Alert, Typography, Space, Tag } from 'antd';
import { RobotOutlined, BulbOutlined, RiseOutlined, DollarOutlined } from '@ant-design/icons';

const { Text, Paragraph } = Typography;

const ExecutiveSummary = ({ 
  summary, 
  isLoading, 
  error, 
  recordCount, 
  dataType = "data" 
}) => {
  const getSummaryIcon = () => {
    switch (dataType) {
      case 'sourcing':
        return <RiseOutlined style={{ color: '#00AC69' }} />;
      case 'scoring':
        return <BulbOutlined style={{ color: '#1E3A8A' }} />;
      case 'contract-value':
        return <DollarOutlined style={{ color: '#F59E0B' }} />;
      default:
        return <RobotOutlined style={{ color: '#6366F1' }} />;
    }
  };

  const getSummaryTitle = () => {
    switch (dataType) {
      case 'sourcing':
        return 'Lead Sourcing Intelligence';
      case 'scoring':
        return 'Lead Scoring Insights';
      case 'contract-value':
        return 'Revenue Optimization Analysis';
      case 'product-tiers':
        return 'Product Tier Analysis';
      case 'lead-sources':
        return 'Lead Source Effectiveness';
      case 'observability-adoption':
        return 'Observability Market Analysis';
      case 'gtm-overview':
        return 'GTM Overview Intelligence';
      case 'pipeline-health':
        return 'Pipeline Health Analysis';
      case 'industry-analysis':
        return 'Industry Performance Analysis';
      case 'competitive-landscape':
        return 'Competitive Landscape Analysis';
      default:
        return 'AI Executive Summary';
    }
  };

  if (isLoading) {
    return (
      <Card 
        size="small" 
        style={{ marginBottom: 16, background: 'linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%)' }}
        title={
          <Space>
            {getSummaryIcon()}
            <span style={{ fontWeight: 600 }}>Generating AI Insights...</span>
          </Space>
        }
      >
        <div style={{ textAlign: 'center', padding: '20px 0' }}>
          <Spin size="large" />
          <div style={{ marginTop: 12, color: '#64748b' }}>
            Analyzing {recordCount || 0} records with Gemini AI
          </div>
        </div>
      </Card>
    );
  }

  if (error) {
    return (
      <Card 
        size="small" 
        style={{ marginBottom: 16 }}
        title={
          <Space>
            <RobotOutlined style={{ color: '#EF4444' }} />
            <span style={{ fontWeight: 600 }}>AI Summary Unavailable</span>
          </Space>
        }
      >
        <Alert
          message="Unable to generate AI summary"
          description={error}
          type="warning"
          showIcon
        />
      </Card>
    );
  }

  if (!summary) {
    return null;
  }

  return (
    <Card 
      size="small" 
      style={{ 
        marginBottom: 16, 
        background: 'linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%)',
        border: '1px solid #0ea5e9'
      }}
      title={
        <Space>
          {getSummaryIcon()}
          <span style={{ fontWeight: 600, color: '#0c4a6e' }}>
            {getSummaryTitle()}
          </span>
          {recordCount && (
            <Tag color="blue" style={{ marginLeft: 8 }}>
              {recordCount} records analyzed
            </Tag>
          )}
        </Space>
      }
    >
      <div style={{ padding: '8px 0' }}>
        <Paragraph 
          style={{ 
            margin: 0, 
            fontSize: '14px', 
            lineHeight: '1.6',
            color: '#0c4a6e',
            fontWeight: 500
          }}
        >
          {summary}
        </Paragraph>
      </div>
      
      <div style={{ 
        marginTop: 12, 
        padding: '8px 12px', 
        background: 'rgba(14, 165, 233, 0.1)', 
        borderRadius: '6px',
        border: '1px solid rgba(14, 165, 233, 0.2)'
      }}>
        <Text style={{ fontSize: '12px', color: '#0369a1', fontStyle: 'italic' }}>
          💡 Powered by Gemini AI • Insights generated from filtered data analysis
        </Text>
      </div>
    </Card>
  );
};

export default ExecutiveSummary;
