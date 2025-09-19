import React from 'react';
import {
  Box,
  Grid,
  Paper,
  Typography,
  Card,
  CardContent,
  LinearProgress,
  Divider
} from '@mui/material';
import AssignmentIcon from '@mui/icons-material/Assignment';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import BugReportIcon from '@mui/icons-material/BugReport';
import { dashboardStats } from '../mockData';

const Dashboard = () => {
  const {
    totalRequirements,
    totalTestCases,
    traceabilityCoverage,
    edgeCasesIdentified
  } = dashboardStats;

  // KPI Card component
  const KpiCard = ({ title, value, icon, color, subtitle, progress }) => (
    <Card elevation={2} sx={{ height: '100%' }}>
      <CardContent>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
          <Typography variant="h6" color="text.secondary" fontWeight="medium">
            {title}
          </Typography>
          <Box
            sx={{
              backgroundColor: `${color}20`,
              borderRadius: '50%',
              width: 40,
              height: 40,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}
          >
            {icon}
          </Box>
        </Box>
        <Typography variant="h4" fontWeight="bold">
          {value}
        </Typography>
        {subtitle && (
          <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
            {subtitle}
          </Typography>
        )}
        {progress !== undefined && (
          <Box sx={{ mt: 2 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
              <Typography variant="body2" color="text.secondary">
                Progress
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {progress}%
              </Typography>
            </Box>
            <LinearProgress
              variant="determinate"
              value={progress}
              sx={{
                height: 6,
                borderRadius: 3,
                backgroundColor: `${color}20`,
                '& .MuiLinearProgress-bar': {
                  backgroundColor: color
                }
              }}
            />
          </Box>
        )}
      </CardContent>
    </Card>
  );

  return (
    <Box>
      <Paper elevation={2} sx={{ p: 3, borderRadius: 2, mb: 3 }}>
        <Typography variant="h5" gutterBottom fontWeight="medium">
          Dashboard
        </Typography>
        <Typography variant="body2" color="text.secondary" paragraph>
          Overview of test case generation metrics and coverage statistics
        </Typography>

        <Grid container spacing={3}>
          {/* Requirements Parsed */}
          <Grid item xs={12} sm={6} md={3}>
            <KpiCard
              title="Requirements Parsed"
              value={totalRequirements}
              icon={<AssignmentIcon sx={{ color: '#2196F3' }} />}
              color="#2196F3"
              subtitle="Total requirements documents processed"
            />
          </Grid>

          {/* Test Cases Generated */}
          <Grid item xs={12} sm={6} md={3}>
            <KpiCard
              title="Test Cases Generated"
              value={totalTestCases}
              icon={<CheckCircleIcon sx={{ color: '#4CAF50' }} />}
              color="#4CAF50"
              subtitle="Total test cases created from requirements"
            />
          </Grid>

          {/* Traceability Coverage */}
          <Grid item xs={12} sm={6} md={3}>
            <KpiCard
              title="Traceability Coverage"
              value={`${traceabilityCoverage}%`}
              icon={<TrendingUpIcon sx={{ color: '#FF9800' }} />}
              color="#FF9800"
              subtitle="Requirements covered by test cases"
              progress={traceabilityCoverage}
            />
          </Grid>

          {/* Edge Cases Identified */}
          <Grid item xs={12} sm={6} md={3}>
            <KpiCard
              title="Edge Cases Identified"
              value={edgeCasesIdentified}
              icon={<BugReportIcon sx={{ color: '#F44336' }} />}
              color="#F44336"
              subtitle="Potential edge cases requiring attention"
            />
          </Grid>
        </Grid>
      </Paper>

      {/* Recent Activity Section */}
      <Paper elevation={2} sx={{ p: 3, borderRadius: 2 }}>
        <Typography variant="h5" gutterBottom fontWeight="medium">
          Recent Activity
        </Typography>
        <Typography variant="body2" color="text.secondary" paragraph>
          Latest test case generation and updates
        </Typography>

        <Box sx={{ py: 1 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
            <Typography variant="body2" fontWeight="medium">
              PatientCare_Requirements_v1.2.pdf
            </Typography>
            <Typography variant="body2" color="text.secondary">
              18 Sept 2023
            </Typography>
          </Box>
          <Typography variant="body2" color="text.secondary">
            Generated 8 test cases with 100% traceability coverage
          </Typography>
          <Divider sx={{ my: 2 }} />

          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
            <Typography variant="body2" fontWeight="medium">
              MedicationModule_Requirements.docx
            </Typography>
            <Typography variant="body2" color="text.secondary">
              19 Sept 2023
            </Typography>
          </Box>
          <Typography variant="body2" color="text.secondary">
            Regenerated test cases with focus on security testing
          </Typography>
          <Divider sx={{ my: 2 }} />

          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
            <Typography variant="body2" fontWeight="medium">
              RTM Export
            </Typography>
            <Typography variant="body2" color="text.secondary">
              20 Sept 2023
            </Typography>
          </Box>
          <Typography variant="body2" color="text.secondary">
            Exported Requirements Traceability Matrix to CSV
          </Typography>
        </Box>
      </Paper>
    </Box>
  );
};

export default Dashboard;
