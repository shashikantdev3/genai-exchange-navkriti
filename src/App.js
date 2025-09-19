import React, { useState } from 'react';
import { 
  BrowserRouter as Router,
  Routes,
  Route,
  Link
} from 'react-router-dom';
import { 
  Container, 
  Box, 
  AppBar, 
  Toolbar, 
  Typography, 
  Button, 
  Tabs, 
  Tab,
  Paper
} from '@mui/material';
import DashboardIcon from '@mui/icons-material/Dashboard';
import AssignmentIcon from '@mui/icons-material/Assignment';
import TableChartIcon from '@mui/icons-material/TableChart';
import HistoryIcon from '@mui/icons-material/History';

// Import components
import Dashboard from './components/Dashboard';
import TestCaseTable from './components/TestCaseTable';
import TraceabilityMatrix from './components/TraceabilityMatrix';
import AuditTrail from './components/AuditTrail';
import TestCaseControls from './components/TestCaseControls';

const App = () => {
  const [value, setValue] = useState(0);
  const [testCasesGenerated, setTestCasesGenerated] = useState(false);

  // Handle tab change
  const handleChange = (event, newValue) => {
    setValue(newValue);
  };

  // Handle test case generation
  const handleGenerate = (fileInfo) => {
    console.log('File uploaded and test cases generated:', fileInfo);
    setTestCasesGenerated(true);
    // In a real app, this would call an API to generate test cases
  };

  // Handle test case regeneration
  const handleRegenerate = (answers) => {
    console.log('Regenerating test cases with answers:', answers);
    // In a real app, this would call an API to regenerate test cases
  };

  return (
    <Router>
      <Box sx={{ flexGrow: 1 }}>
        <AppBar position="static" color="primary">
          <Toolbar>
            <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
              Healthcare AI Test Case Generator
            </Typography>
          </Toolbar>
        </AppBar>

        <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
          <Paper sx={{ p: 2, mb: 3 }}>
            <TestCaseControls 
              onGenerate={handleGenerate} 
              onRegenerate={handleRegenerate} 
            />
          </Paper>

          <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
            <Tabs 
              value={value} 
              onChange={handleChange} 
              aria-label="navigation tabs"
              variant="fullWidth"
            >
              <Tab 
                icon={<DashboardIcon />} 
                label="Dashboard" 
                component={Link} 
                to="/" 
              />
              <Tab 
                icon={<AssignmentIcon />} 
                label="Test Cases" 
                component={Link} 
                to="/test-cases" 
                disabled={!testCasesGenerated}
              />
              <Tab 
                icon={<TableChartIcon />} 
                label="Traceability Matrix" 
                component={Link} 
                to="/traceability" 
                disabled={!testCasesGenerated}
              />
              <Tab 
                icon={<HistoryIcon />} 
                label="Audit Trail" 
                component={Link} 
                to="/audit" 
              />
            </Tabs>
          </Box>

          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/test-cases" element={<TestCaseTable />} />
            <Route path="/traceability" element={<TraceabilityMatrix />} />
            <Route path="/audit" element={<AuditTrail />} />
          </Routes>
        </Container>
      </Box>
    </Router>
  );
};

export default App;