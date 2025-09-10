import React, { useState } from 'react';
import { Card, Form, Input, Select, Button, Space, Spin, Alert, Divider, Tag } from 'antd';
import { SendOutlined, CopyOutlined } from '@ant-design/icons';
import { apiService } from '../services/api';

const { Option } = Select;
const { TextArea } = Input;

const OutreachGenerator = () => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [outreachResult, setOutreachResult] = useState(null);
  const [error, setError] = useState(null);

  const handleGenerate = async (values) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await apiService.generateOutreach({
        company_name: values.company_name,
        contact_name: values.contact_name,
        job_title: values.job_title,
        industry: values.industry,
        tech_stack: values.tech_stack || [],
        hiring_signals: values.hiring_signals || []
      });
      
      setOutreachResult(response.data);
    } catch (err) {
      setError('Failed to generate outreach. Please try again.');
      console.error('Outreach generation error:', err);
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    // You could add a notification here
  };

  return (
    <div style={{ marginTop: '20px' }}>
      <Card title="New Relic Personalized Outreach Generator" className="nr-card" style={{ marginBottom: 24 }}>
        <Form
          form={form}
          layout="vertical"
          onFinish={handleGenerate}
          initialValues={{
            tech_stack: [],
            hiring_signals: []
          }}
        >
          <Form.Item
            label="Company Name"
            name="company_name"
            rules={[{ required: true, message: 'Please enter company name' }]}
          >
            <Input placeholder="e.g., Acme Corp" />
          </Form.Item>

          <Form.Item
            label="Contact Name"
            name="contact_name"
            rules={[{ required: true, message: 'Please enter contact name' }]}
          >
            <Input placeholder="e.g., John Smith" />
          </Form.Item>

          <Form.Item
            label="Job Title"
            name="job_title"
            rules={[{ required: true, message: 'Please enter job title' }]}
          >
            <Input placeholder="e.g., VP of Engineering" />
          </Form.Item>

          <Form.Item
            label="Industry"
            name="industry"
            rules={[{ required: true, message: 'Please select industry' }]}
          >
            <Select placeholder="Select industry">
              <Option value="Technology">Technology</Option>
              <Option value="Healthcare">Healthcare</Option>
              <Option value="Financial Services">Financial Services</Option>
              <Option value="Manufacturing">Manufacturing</Option>
              <Option value="Retail">Retail</Option>
              <Option value="Education">Education</Option>
              <Option value="Government">Government</Option>
              <Option value="Energy">Energy</Option>
              <Option value="Telecommunications">Telecommunications</Option>
              <Option value="Media">Media</Option>
            </Select>
          </Form.Item>

          <Form.Item
            label="Technology Stack"
            name="tech_stack"
            help="Select technologies the company is using"
          >
            <Select
              mode="multiple"
              placeholder="Select technologies"
              style={{ width: '100%' }}
            >
              <Option value="AWS">AWS</Option>
              <Option value="Azure">Azure</Option>
              <Option value="GCP">Google Cloud</Option>
              <Option value="Docker">Docker</Option>
              <Option value="Kubernetes">Kubernetes</Option>
              <Option value="Python">Python</Option>
              <Option value="Java">Java</Option>
              <Option value="Node.js">Node.js</Option>
              <Option value="React">React</Option>
              <Option value="Angular">Angular</Option>
              <Option value="Datadog">Datadog</Option>
              <Option value="Splunk">Splunk</Option>
              <Option value="Dynatrace">Dynatrace</Option>
              <Option value="AppDynamics">AppDynamics</Option>
              <Option value="Elastic Stack">Elastic Stack</Option>
              <Option value="Prometheus">Prometheus</Option>
              <Option value="Grafana">Grafana</Option>
              <Option value="Jaeger">Jaeger</Option>
              <Option value="Zipkin">Zipkin</Option>
            </Select>
          </Form.Item>

          <Form.Item
            label="Hiring Signals"
            name="hiring_signals"
            help="Select recent hiring trends or job postings"
          >
            <Select
              mode="multiple"
              placeholder="Select hiring signals"
              style={{ width: '100%' }}
            >
              <Option value="DevOps Engineers">DevOps Engineers</Option>
              <Option value="Site Reliability Engineers">Site Reliability Engineers</Option>
              <Option value="Security Operations">Security Operations</Option>
              <Option value="Platform Engineers">Platform Engineers</Option>
              <Option value="Director of Observability">Director of Observability</Option>
              <Option value="Head of Platform Engineering">Head of Platform Engineering</Option>
              <Option value="Distributed Tracing">Distributed Tracing</Option>
              <Option value="APM">APM</Option>
              <Option value="OpenTelemetry">OpenTelemetry</Option>
            </Select>
          </Form.Item>

          <Form.Item>
            <Button
              type="primary"
              htmlType="submit"
              loading={loading}
              icon={<SendOutlined />}
              size="large"
              className="nr-btn-primary"
            >
              Generate New Relic Outreach
            </Button>
          </Form.Item>
        </Form>
      </Card>

      {error && (
        <Alert
          message="Error"
          description={error}
          type="error"
          showIcon
          style={{ marginBottom: 24 }}
        />
      )}

      {loading && (
        <Card>
          <div style={{ textAlign: 'center', padding: '40px 0' }}>
            <Spin size="large" />
            <p style={{ marginTop: 16 }}>Generating personalized outreach...</p>
          </div>
        </Card>
      )}

      {outreachResult && (
        <Card title="Generated Outreach">
          <div style={{ marginBottom: 16 }}>
            <Tag color="green">Personalization Score: {(outreachResult.personalization_score * 100).toFixed(0)}%</Tag>
            <Tag color="blue">AI-Generated</Tag>
            {outreachResult.personalization_insights && (
              <Tag color="purple">Enhanced Personalization</Tag>
            )}
          </div>

          <div className="outreach-preview">
            {outreachResult.outreach_text}
          </div>

          <Divider />

          {outreachResult.personalization_insights && (
            <div style={{ marginBottom: 16 }}>
              <h4>Personalization Insights:</h4>
              <p style={{ color: '#666', fontStyle: 'italic' }}>
                {outreachResult.personalization_insights}
              </p>
            </div>
          )}

          <div style={{ marginBottom: 16 }}>
            <h4>Key Signals Used:</h4>
            <div style={{ marginBottom: 8 }}>
              <strong>Hiring Signals:</strong>{' '}
              {outreachResult.key_signals_used.hiring_signals.map(signal => (
                <Tag key={signal} color="orange">{signal}</Tag>
              ))}
            </div>
            <div style={{ marginBottom: 8 }}>
              <strong>Tech Stack:</strong>{' '}
              {outreachResult.key_signals_used.tech_stack.map(tech => (
                <Tag key={tech} color="blue">{tech}</Tag>
              ))}
            </div>
            <div>
              <strong>Industry:</strong>{' '}
              <Tag color="green">{outreachResult.key_signals_used.industry}</Tag>
            </div>
            {outreachResult.key_signals_used.job_title && (
              <div style={{ marginTop: 8 }}>
                <strong>Role:</strong>{' '}
                <Tag color="purple">{outreachResult.key_signals_used.job_title}</Tag>
              </div>
            )}
          </div>

          <div style={{ marginBottom: 16 }}>
            <h4>Follow-up Suggestion:</h4>
            <p style={{ color: '#666' }}>{outreachResult.suggested_follow_up}</p>
          </div>

          <Space>
            <Button
              type="primary"
              icon={<CopyOutlined />}
              onClick={() => copyToClipboard(outreachResult.outreach_text)}
            >
              Copy to Clipboard
            </Button>
            <Button onClick={() => setOutreachResult(null)}>
              Generate New
            </Button>
          </Space>
        </Card>
      )}
    </div>
  );
};

export default OutreachGenerator;
