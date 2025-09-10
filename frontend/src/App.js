import React from 'react';
import { BrowserRouter as Router, Routes, Route, useLocation, useNavigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from 'react-query';
import { Layout, Menu } from 'antd';
import {
  DashboardOutlined,
  MessageOutlined,
  BarChartOutlined,
  DollarOutlined,
  RocketOutlined,
  GlobalOutlined
} from '@ant-design/icons';
import GTMDashboard from './components/GTMDashboard';
import OutreachGenerator from './components/OutreachGenerator';
import Analytics from './components/Analytics';
import LeadSourcing from './components/LeadSourcing';
import LeadScoring from './components/LeadScoring';
import ContractValue from './components/ContractValue';
import './App.css';

const { Header, Sider, Content } = Layout;

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
});

function AppContent() {
  const [collapsed, setCollapsed] = React.useState(false);
  const location = useLocation();
  const navigate = useNavigate();

  const menuItems = [
    {
      key: 'dashboard',
      icon: <DashboardOutlined />,
      label: 'GTM Overview',
      path: '/'
    },
    {
      key: 'sourcing',
      icon: <GlobalOutlined />,
      label: 'Lead Sourcing',
      path: '/sourcing'
    },
    {
      key: 'predictions',
      icon: <RocketOutlined />,
      label: 'Lead Scoring',
      path: '/predictions'
    },
    {
      key: 'value',
      icon: <DollarOutlined />,
      label: 'Contract Value',
      path: '/value'
    },
    {
      key: 'outreach',
      icon: <MessageOutlined />,
      label: 'Personalized Outreach',
      path: '/outreach'
    },
    {
      key: 'analytics',
      icon: <BarChartOutlined />,
      label: 'GTM Analytics',
      path: '/analytics'
    }
  ];

  // Get current selected key based on location
  const getSelectedKey = () => {
    const path = location.pathname;
    if (path === '/') return ['dashboard'];
    if (path === '/sourcing') return ['sourcing'];
    if (path === '/predictions') return ['predictions'];
    if (path === '/value') return ['value'];
    if (path === '/outreach') return ['outreach'];
    if (path === '/analytics') return ['analytics'];
    return ['dashboard'];
  };

  return (
    <Layout style={{ minHeight: '100vh' }}>
          <Sider 
            collapsible 
            collapsed={collapsed} 
            onCollapse={setCollapsed}
            className="nr-sidebar"
            width={280}
          >
            <div className="nr-sidebar-header">
              <div className="nr-sidebar-logo">
                <img 
                  src="/new_relic_logo_horizontal.png" 
                  alt="New Relic" 
                  className="nr-logo-image"
                  style={{ height: '32px', width: 'auto', objectFit: 'contain' }}
                />
                {!collapsed && (
                  <div>
                    <div style={{ fontSize: '16px', fontWeight: '700', color: 'var(--nr-primary)' }}>GTM Intelligence</div>
                    <div style={{ fontSize: '12px', color: 'var(--nr-gray-500)' }}>Lead Assessment Platform</div>
                  </div>
                )}
              </div>
            </div>
            <Menu
              theme="light"
              selectedKeys={getSelectedKey()}
              mode="inline"
              style={{ border: 'none', background: 'white' }}
              items={menuItems.map(item => ({
                key: item.key,
                icon: item.icon,
                label: item.label,
                onClick: () => navigate(item.path)
              }))}
            />
          </Sider>
          <Layout>
            <Header className="nr-header">
              <div className="nr-logo">
                <img 
                  src="/new_relic_logo_horizontal.png" 
                  alt="New Relic" 
                  className="nr-logo-image"
                  style={{ 
                    height: '40px', 
                    width: 'auto', 
                    objectFit: 'contain',
                    filter: 'brightness(0) invert(1)',
                    backgroundColor: 'rgba(255, 255, 255, 0.1)',
                    padding: '4px 8px',
                    borderRadius: '4px'
                  }}
                />
                <div className="nr-logo-text">
                  <div className="main-title">GTM Intelligence Platform</div>
                  <div className="sub-title">Lead Assessment & Revenue Optimization</div>
                </div>
              </div>
              <div style={{ color: 'white', fontSize: '14px', opacity: 0.9 }}>
                Enterprise Sales Platform
              </div>
            </Header>
            <Content className="nr-content">
              <Routes>
                <Route path="/" element={<GTMDashboard />} />
                <Route path="/sourcing" element={<LeadSourcing />} />
                <Route path="/predictions" element={<LeadScoring />} />
                <Route path="/value" element={<ContractValue />} />
                <Route path="/outreach" element={<OutreachGenerator />} />
                <Route path="/analytics" element={<Analytics />} />
              </Routes>
            </Content>
          </Layout>
    </Layout>
  );
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <AppContent />
      </Router>
    </QueryClientProvider>
  );
}

export default App;
