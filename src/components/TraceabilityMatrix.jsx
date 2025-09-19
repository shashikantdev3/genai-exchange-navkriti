import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,
  InputAdornment
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import FileDownloadIcon from '@mui/icons-material/FileDownload';
import { requirements, testCases, complianceStandards } from '../mockData';

const TraceabilityMatrix = () => {
  const [searchTerm, setSearchTerm] = useState('');

  // Get compliance standard name and color by ID
  const getComplianceInfo = (id) => {
    const standard = complianceStandards.find(std => std.id === id);
    return standard || { name: id, color: '#757575' };
  };

  // Get test cases for a requirement
  const getTestCasesForRequirement = (reqId) => {
    return testCases.filter(tc => tc.requirementId === reqId);
  };

  // Get status for a requirement based on its test cases
  const getRequirementStatus = (reqId) => {
    const relatedTestCases = getTestCasesForRequirement(reqId);
    if (relatedTestCases.length === 0) return 'Not Tested';
    
    const statuses = relatedTestCases.map(tc => tc.status);
    if (statuses.includes('Fail')) return 'Fail';
    if (statuses.every(status => status === 'Pass')) return 'Pass';
    return 'In Progress';
  };

  // Filter requirements based on search term
  const filteredRequirements = requirements.filter(req => {
    if (!searchTerm) return true;
    
    const searchLower = searchTerm.toLowerCase();
    return (
      req.id.toLowerCase().includes(searchLower) ||
      req.description.toLowerCase().includes(searchLower) ||
      req.complianceRefs.some(ref => {
        const { name } = getComplianceInfo(ref);
        return name.toLowerCase().includes(searchLower);
      })
    );
  });

  // Export RTM to CSV
  const exportToCSV = () => {
    const headers = ['Requirement ID', 'Requirement Description', 'Test Case IDs', 'Compliance Standards', 'Status'];
    
    const rows = requirements.map(req => {
      const testCaseIds = getTestCasesForRequirement(req.id).map(tc => tc.id).join(', ');
      const complianceStds = req.complianceRefs.map(ref => getComplianceInfo(ref).name).join(', ');
      const status = getRequirementStatus(req.id);
      
      return [
        req.id,
        req.description,
        testCaseIds,
        complianceStds,
        status
      ];
    });
    
    const csvContent = [
      headers.join(','),
      ...rows.map(row => row.map(cell => `"${cell}"`).join(','))
    ].join('\n');
    
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.setAttribute('href', url);
    link.setAttribute('download', 'Requirements_Traceability_Matrix.csv');
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <Paper elevation={2} sx={{ p: 3, borderRadius: 2 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h5" fontWeight="medium">
          Requirements Traceability Matrix
        </Typography>
        <Button
          variant="outlined"
          startIcon={<FileDownloadIcon />}
          onClick={exportToCSV}
        >
          Export RTM
        </Button>
      </Box>
      
      <TextField
        label="Search Requirements"
        variant="outlined"
        size="small"
        fullWidth
        sx={{ mb: 3 }}
        value={searchTerm}
        onChange={(e) => setSearchTerm(e.target.value)}
        InputProps={{
          startAdornment: (
            <InputAdornment position="start">
              <SearchIcon fontSize="small" />
            </InputAdornment>
          ),
        }}
      />
      
      <TableContainer component={Paper} elevation={0} sx={{ maxHeight: 600 }}>
        <Table stickyHeader>
          <TableHead>
            <TableRow>
              <TableCell sx={{ fontWeight: 'bold', backgroundColor: '#f5f5f5' }}>Requirement ID</TableCell>
              <TableCell sx={{ fontWeight: 'bold', backgroundColor: '#f5f5f5' }}>Requirement Description</TableCell>
              <TableCell sx={{ fontWeight: 'bold', backgroundColor: '#f5f5f5' }}>Test Case ID(s)</TableCell>
              <TableCell sx={{ fontWeight: 'bold', backgroundColor: '#f5f5f5' }}>Compliance Standard(s)</TableCell>
              <TableCell sx={{ fontWeight: 'bold', backgroundColor: '#f5f5f5' }}>Status</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {filteredRequirements.map((req) => {
              const relatedTestCases = getTestCasesForRequirement(req.id);
              const status = getRequirementStatus(req.id);
              
              return (
                <TableRow key={req.id} hover>
                  <TableCell>{req.id}</TableCell>
                  <TableCell>{req.description}</TableCell>
                  <TableCell>
                    <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                      {relatedTestCases.map(tc => (
                        <Chip
                          key={tc.id}
                          label={tc.id}
                          size="small"
                          sx={{ backgroundColor: '#e3f2fd', color: '#1976d2' }}
                        />
                      ))}
                      {relatedTestCases.length === 0 && (
                        <Typography variant="body2" color="text.secondary">
                          No test cases
                        </Typography>
                      )}
                    </Box>
                  </TableCell>
                  <TableCell>
                    <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                      {req.complianceRefs.map(ref => {
                        const { name, color } = getComplianceInfo(ref);
                        return (
                          <Chip
                            key={ref}
                            label={name}
                            size="small"
                            sx={{
                              backgroundColor: `${color}20`,
                              color: color,
                              fontWeight: 'medium',
                              fontSize: '0.7rem'
                            }}
                          />
                        );
                      })}
                    </Box>
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={status}
                      size="small"
                      sx={{
                        backgroundColor:
                          status === 'Pass' ? '#e8f5e9' :
                          status === 'Fail' ? '#ffebee' :
                          '#f5f5f5',
                        color:
                          status === 'Pass' ? '#2e7d32' :
                          status === 'Fail' ? '#c62828' :
                          '#757575',
                        fontWeight: 'medium'
                      }}
                    />
                  </TableCell>
                </TableRow>
              );
            })}
          </TableBody>
        </Table>
      </TableContainer>
    </Paper>
  );
};

export default TraceabilityMatrix;
