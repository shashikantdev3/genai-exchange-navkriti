import React, { useState, useMemo } from 'react';
import {
  Box,
  Paper,
  Typography,
  Chip,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Link,
  InputAdornment,
  IconButton
} from '@mui/material';
import { DataGrid } from '@mui/x-data-grid';
import SearchIcon from '@mui/icons-material/Search';
import FilterListIcon from '@mui/icons-material/FilterList';
import { testCases, complianceStandards, requirements } from '../mockData';

const TestCaseTable = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [complianceFilter, setComplianceFilter] = useState('');
  const [requirementFilter, setRequirementFilter] = useState('');

  // Get compliance standard name and color by ID
  const getComplianceInfo = (id) => {
    const standard = complianceStandards.find(std => std.id === id);
    return standard || { name: id, color: '#757575' };
  };

  // Get requirement description by ID
  const getRequirementDesc = (id) => {
    const req = requirements.find(req => req.id === id);
    return req ? req.description : '';
  };

  // Filter test cases based on search term and filters
  const filteredTestCases = useMemo(() => {
    return testCases.filter(testCase => {
      // Filter by requirement ID if selected
      if (requirementFilter && testCase.requirementId !== requirementFilter) {
        return false;
      }
      
      // Filter by compliance standard if selected
      if (complianceFilter && !testCase.complianceRefs.includes(complianceFilter)) {
        return false;
      }
      
      // Search by test case ID or title
      if (searchTerm) {
        const searchLower = searchTerm.toLowerCase();
        return (
          testCase.id.toLowerCase().includes(searchLower) ||
          testCase.title.toLowerCase().includes(searchLower) ||
          testCase.requirementId.toLowerCase().includes(searchLower)
        );
      }
      
      return true;
    });
  }, [searchTerm, complianceFilter, requirementFilter]);

  // Define columns for the DataGrid
  const columns = [
    { 
      field: 'id', 
      headerName: 'Test Case ID', 
      width: 130,
      renderCell: (params) => (
        <Typography variant="body2" fontWeight="medium">
          {params.value}
        </Typography>
      )
    },
    { 
      field: 'title', 
      headerName: 'Title', 
      flex: 1,
      minWidth: 200 
    },
    { 
      field: 'requirementId', 
      headerName: 'Requirement ID', 
      width: 150,
      renderCell: (params) => (
        <Link 
          href="#" 
          onClick={(e) => {
            e.preventDefault();
            // In a real app, this would navigate to requirement details
            console.log(`Navigate to requirement ${params.value}`);
          }}
          sx={{ textDecoration: 'underline' }}
        >
          {params.value}
        </Link>
      )
    },
    { 
      field: 'steps', 
      headerName: 'Test Steps', 
      flex: 1.5,
      minWidth: 250,
      renderCell: (params) => (
        <Typography variant="body2" sx={{ whiteSpace: 'pre-line' }}>
          {params.value}
        </Typography>
      )
    },
    { 
      field: 'expectedResult', 
      headerName: 'Expected Result', 
      flex: 1.5,
      minWidth: 250 
    },
    { 
      field: 'priority', 
      headerName: 'Priority', 
      width: 120,
      renderCell: (params) => {
        const color = 
          params.value === 'High' ? '#f44336' : 
          params.value === 'Medium' ? '#ff9800' : 
          '#4caf50';
        
        return (
          <Chip 
            label={params.value} 
            size="small"
            sx={{ 
              backgroundColor: `${color}20`, // 20% opacity
              color: color,
              fontWeight: 'medium'
            }} 
          />
        );
      }
    },
    { 
      field: 'complianceRefs', 
      headerName: 'Compliance Reference', 
      width: 250,
      renderCell: (params) => (
        <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
          {params.value.map(ref => {
            const { name, color } = getComplianceInfo(ref);
            return (
              <Chip 
                key={ref}
                label={name}
                size="small"
                sx={{ 
                  backgroundColor: `${color}20`, // 20% opacity
                  color: color,
                  fontWeight: 'medium',
                  fontSize: '0.7rem'
                }} 
              />
            );
          })}
        </Box>
      )
    },
    { 
      field: 'status', 
      headerName: 'Status', 
      width: 120,
      renderCell: (params) => {
        const color = 
          params.value === 'Pass' ? '#4caf50' : 
          params.value === 'Fail' ? '#f44336' : 
          '#757575';
        
        return (
          <Chip 
            label={params.value} 
            size="small"
            sx={{ 
              backgroundColor: `${color}20`, // 20% opacity
              color: color,
              fontWeight: 'medium'
            }} 
          />
        );
      }
    }
  ];

  return (
    <Paper elevation={2} sx={{ p: 3, borderRadius: 2 }}>
      <Typography variant="h5" gutterBottom fontWeight="medium">
        Test Cases
      </Typography>
      
      {/* Filters and Search */}
      <Box sx={{ display: 'flex', mb: 3, gap: 2, flexWrap: 'wrap' }}>
        <TextField
          label="Search"
          variant="outlined"
          size="small"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          sx={{ minWidth: 200, flex: 1 }}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon fontSize="small" />
              </InputAdornment>
            ),
          }}
        />
        
        <FormControl size="small" sx={{ minWidth: 200 }}>
          <InputLabel id="requirement-filter-label">Requirement ID</InputLabel>
          <Select
            labelId="requirement-filter-label"
            value={requirementFilter}
            label="Requirement ID"
            onChange={(e) => setRequirementFilter(e.target.value)}
            startAdornment={
              <InputAdornment position="start">
                <FilterListIcon fontSize="small" />
              </InputAdornment>
            }
          >
            <MenuItem value="">All Requirements</MenuItem>
            {requirements.map(req => (
              <MenuItem key={req.id} value={req.id}>
                {req.id} - {req.description.substring(0, 30)}...
              </MenuItem>
            ))}
          </Select>
        </FormControl>
        
        <FormControl size="small" sx={{ minWidth: 200 }}>
          <InputLabel id="compliance-filter-label">Compliance Standard</InputLabel>
          <Select
            labelId="compliance-filter-label"
            value={complianceFilter}
            label="Compliance Standard"
            onChange={(e) => setComplianceFilter(e.target.value)}
            startAdornment={
              <InputAdornment position="start">
                <FilterListIcon fontSize="small" />
              </InputAdornment>
            }
          >
            <MenuItem value="">All Standards</MenuItem>
            {complianceStandards.map(std => (
              <MenuItem key={std.id} value={std.id}>
                {std.name}
              </MenuItem>
            ))}
          </Select>
        </FormControl>
      </Box>
      
      {/* DataGrid */}
      <Box sx={{ height: 500, width: '100%' }}>
        <DataGrid
          rows={filteredTestCases}
          columns={columns}
          pageSize={10}
          rowsPerPageOptions={[5, 10, 25]}
          disableSelectionOnClick
          density="standard"
          sx={{
            '& .MuiDataGrid-cell': {
              py: 1
            },
            '& .MuiDataGrid-columnHeaders': {
              backgroundColor: '#f5f5f5'
            }
          }}
        />
      </Box>
    </Paper>
  );
};

export default TestCaseTable;
