import React, { useState } from 'react';
import { Box, Button, Typography, LinearProgress, Alert } from '@mui/material';
import UploadFileIcon from '@mui/icons-material/UploadFile';

const ALLOWED_TYPES = [
  'application/pdf',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
];
const MAX_SIZE = 5 * 1024 * 1024; // 5MB

export default function FileUpload({ onUpload }) {
  const [selectedFile, setSelectedFile] = useState(null);
  const [error, setError] = useState('');
  const [uploading, setUploading] = useState(false);

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (!file) return;
    if (!ALLOWED_TYPES.includes(file.type)) {
      setError('Only PDF or DOCX files allowed.');
      return;
    }
    if (file.size > MAX_SIZE) {
      setError('File size exceeds 5MB.');
      return;
    }
    setSelectedFile(file);
    setError('');
  };

  const handleUpload = () => {
    if (!selectedFile) return;

    setUploading(true);
    setError('');

    // Simulate upload delay with dummy data for prototype
    setTimeout(() => {
      const dummyTestCases = [
        { id: 'TC-001', preconditions: 'User registered', steps: 'Login', expectedResults: 'Success' },
        { id: 'TC-002', preconditions: 'User logged in', steps: 'Upload PDF', expectedResults: 'Processed' }
      ];
      onUpload(dummyTestCases);
      setSelectedFile(null);
      setUploading(false);
    }, 1500);
  };

  return (
    <Box sx={{ my: 3 }}>
      <Typography variant="h6" gutterBottom>Upload Requirements Document</Typography>
      <Button
        variant="contained"
        component="label"
        startIcon={<UploadFileIcon />}
        sx={{ mr: 2 }}
      >
        Choose File
        <input hidden type="file" onChange={handleFileChange} />
      </Button>
      {selectedFile && <Typography sx={{ display: 'inline-block', mr: 2 }}>{selectedFile.name}</Typography>}
      <Button variant="outlined" onClick={handleUpload} disabled={!selectedFile || uploading}>
        {uploading ? 'Uploading...' : 'Upload'}
      </Button>
      {uploading && <LinearProgress sx={{ mt: 2 }} />}
      {error && <Alert severity="error" sx={{ mt: 2 }}>{error}</Alert>}
    </Box>
  );
}
