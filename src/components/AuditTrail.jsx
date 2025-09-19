import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
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
import { auditTrail } from '../mockData';

const AuditTrail = () => {
  const [searchTerm, setSearchTerm] = useState('');

  // Format timestamp to readable date and time
  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleString();
  };

  // Filter audit trail entries based on search term
  const filteredAuditTrail = auditTrail.filter(entry => {
    if (!searchTerm) return true;
    
    const searchLower = searchTerm.toLowerCase();
    return (
      entry.user.toLowerCase().includes(searchLower) ||
      entry.action.toLowerCase().includes(searchLower) ||
      entry.fileName.toLowerCase().includes(searchLower)
    );
  });

  return (
    <Paper elevation={2} sx={{ p: 3, borderRadius: 2 }}>
      <Box sx={{ mb: 3 }}>
        <Typography variant="h5" fontWeight="medium" gutterBottom>
          Audit Trail
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Track all user actions and file uploads in the system
        </Typography>
      </Box>
      
      <TextField
        label="Search Audit Trail"
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
              <TableCell sx={{ fontWeight: 'bold', backgroundColor: '#f5f5f5' }}>User</TableCell>
              <TableCell sx={{ fontWeight: 'bold', backgroundColor: '#f5f5f5' }}>Action</TableCell>
              <TableCell sx={{ fontWeight: 'bold', backgroundColor: '#f5f5f5' }}>File Name</TableCell>
              <TableCell sx={{ fontWeight: 'bold', backgroundColor: '#f5f5f5' }}>Timestamp</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {filteredAuditTrail.map((entry, index) => (
              <TableRow key={index} hover>
                <TableCell>{entry.user}</TableCell>
                <TableCell>
                  <Box sx={{ 
                    display: 'inline-block', 
                    px: 1, 
                    py: 0.5, 
                    borderRadius: 1,
                    backgroundColor: 
                      entry.action.includes('Upload') ? '#e3f2fd' :
                      entry.action.includes('Generate') ? '#e8f5e9' :
                      entry.action.includes('Export') ? '#fff8e1' :
                      '#f5f5f5',
                    color: 
                      entry.action.includes('Upload') ? '#1976d2' :
                      entry.action.includes('Generate') ? '#2e7d32' :
                      entry.action.includes('Export') ? '#f57c00' :
                      '#757575',
                    fontSize: '0.875rem'
                  }}>
                    {entry.action}
                  </Box>
                </TableCell>
                <TableCell>{entry.fileName}</TableCell>
                <TableCell>{formatTimestamp(entry.timestamp)}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Paper>
  );
};

export default AuditTrail;