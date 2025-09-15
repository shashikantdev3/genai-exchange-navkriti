import React, { useState } from 'react';
import { Container, Typography, Button, Box } from '@mui/material';
import FileUpload from './components/FileUpload';
import TestCaseTable from './components/TestCaseTable';
import FeedbackForm from './components/FeedbackForm';

// CSV export helper
function exportToCsv(filename, rows) {
  if (!rows || !rows.length) return;
  const separator = ',';
  const keys = Object.keys(rows[0]);
  const csvContent =
    keys.join(separator) +
    '\n' +
    rows.map(row =>
      keys.map(k => `"${(row[k] ? row[k] : '').toString().replace(/"/g, '""')}"`).join(separator)
    ).join('\n');

  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  const link = document.createElement('a');
  link.href = URL.createObjectURL(blob);
  link.setAttribute('download', filename);
  link.click();
}

export default function App() {
  const [testCases, setTestCases] = useState([]);
  const [feedbacks, setFeedbacks] = useState([]);

  const handleUpload = (cases) => setTestCases(cases);
  const handleFeedback = (fb) => {
    setFeedbacks([...feedbacks, fb]);
    console.log('Feedback received:', fb);
  };

  return (
    <Container maxWidth="md" sx={{ py: 4 }}>
      <Typography variant="h4" gutterBottom>
        Healthcare AI Test Case Generator
      </Typography>
      <FileUpload onUpload={handleUpload} />

      {testCases.length > 0 && (
        <Box sx={{ mt: 3 }}>
          <Button
            variant="outlined"
            onClick={() => exportToCsv('testcases.csv', testCases)}
            sx={{ mb: 2 }}
          >
            Download Test Cases CSV
          </Button>
          <TestCaseTable testCases={testCases} />
        </Box>
      )}

      <FeedbackForm onSubmit={handleFeedback} />
    </Container>
  );
}
