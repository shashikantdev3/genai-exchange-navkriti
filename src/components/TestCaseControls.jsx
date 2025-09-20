import React, { useState, useEffect } from 'react';
import {
  Box,
  Button,
  Typography,
  Paper,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  FormLabel,
  RadioGroup,
  FormControlLabel,
  Radio,
  Checkbox,
  LinearProgress,
  Alert,
  Snackbar
} from '@mui/material';
import { storage, auth } from '../firebase';
import { ref, uploadBytesResumable, getDownloadURL } from 'firebase/storage';
import { onAuthStateChanged } from 'firebase/auth';
import UploadFileIcon from '@mui/icons-material/UploadFile';
import AutorenewIcon from '@mui/icons-material/Autorenew';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import { clarifyingQuestions } from '../mockData';

const TestCaseControls = ({ onGenerate, onRegenerate }) => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [fileUploaded, setFileUploaded] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [regenerateDialogOpen, setRegenerateDialogOpen] = useState(false);
  const [answers, setAnswers] = useState({});
  const [snackbarOpen, setSnackbarOpen] = useState(false);
  const [snackbarMessage, setSnackbarMessage] = useState('');
  const [error, setError] = useState('');
  const [uploadProgress, setUploadProgress] = useState(0);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [gcsFilePath, setGcsFilePath] = useState(''); // New state variable to store GCS path

  // Check authentication state
  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, (user) => {
      if (user) {
        console.log('User is authenticated:', user.uid);
        setIsAuthenticated(true);
      } else {
        console.log('User is not authenticated');
        setIsAuthenticated(false);
      }
    });
    
    // Cleanup subscription
    return () => unsubscribe();
  }, []);

  // Allowed file types
  const ALLOWED_TYPES = [
    'application/pdf',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'text/plain',
    'application/json' // For API specs
  ];

  // Handle file selection and upload
  const handleFileChange = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    
    if (!ALLOWED_TYPES.includes(file.type)) {
      setError('Only PDF, Word, Text, or API spec files allowed.');
      return;
    }
    
    setSelectedFile(file);
    setFileUploaded(false);
    setGcsFilePath('');
    setError('');
    setGenerating(true);
    setUploadProgress(0);

    try {
        const formData = new FormData();
        formData.append('file', file);
      
        // Call the backend /upload endpoint
        const response = await fetch('http://127.0.0.1:8000/upload', {
            method: 'POST',
            body: formData,
        });

        if (!response.ok) {
            throw new Error(`Upload failed with status: ${response.status}`);
        }

        const data = await response.json();
        console.log('Backend upload response:', data);

        // Store the GCS path from the backend response
        setGcsFilePath(data.file_metadata.storage_path);
        setFileUploaded(true);
        setGenerating(false);
        setSnackbarMessage(`File "${file.name}" uploaded successfully!`);
        setSnackbarOpen(true);

    } catch (err) {
        setError(`Upload failed: ${err.message}`);
        setGenerating(false);
    }
  };
  
  // Handle generate button click with real API call
  const handleGenerate = async () => {
    if (!gcsFilePath) return; // Ensure a path exists

    setGenerating(true);
    setError('');

    try {
        // Send the GCS file path to the backend
        const response = await fetch('http://127.0.0.1:8000/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ gcs_path: gcsFilePath }),
        });

        if (!response.ok) {
            throw new Error(`Generation failed with status: ${response.status}`);
        }

        const data = await response.json();
        
        setGenerating(false);
        onGenerate(data.test_cases); // Pass the generated test cases to the parent component
        setSnackbarMessage('Test cases generated successfully');
        setSnackbarOpen(true);

    } catch (err) {
        setGenerating(false);
        setError(`Generation failed: ${err.message}`);
    }
  };

  // Open regenerate dialog
  const handleOpenRegenerateDialog = () => {
    setRegenerateDialogOpen(true);
  };

  // Close regenerate dialog
  const handleCloseRegenerateDialog = () => {
    setRegenerateDialogOpen(false);
  };

  // Handle answer change in dialog
  const handleAnswerChange = (questionId, value) => {
    setAnswers(prev => ({
      ...prev,
      [questionId]: value
    }));
  };

  // Handle checkbox change in dialog
  const handleCheckboxChange = (questionId, option) => {
    const currentAnswers = answers[questionId] || [];
    let newAnswers;
    
    if (currentAnswers.includes(option)) {
      newAnswers = currentAnswers.filter(item => item !== option);
    } else {
      newAnswers = [...currentAnswers, option];
    }
    
    setAnswers(prev => ({
      ...prev,
      [questionId]: newAnswers
    }));
  };

  // Submit regeneration request
  const handleSubmitRegeneration = () => {
    setRegenerateDialogOpen(false);
    setGenerating(true);
    
    // Simulate API call with timeout
    setTimeout(() => {
      setGenerating(false);
      
      // Call parent handler
      if (onRegenerate) {
        onRegenerate({
          fileName: selectedFile.name,
          answers: answers
        });
      }
      
      // Show success message
      setSnackbarMessage('Test cases regenerated successfully');
      setSnackbarOpen(true);
    }, 2000);
  };

  return (
    <Paper elevation={2} sx={{ p: 3, borderRadius: 2, mb: 3 }}>
      <Typography variant="h5" gutterBottom fontWeight="medium">
        Upload & Generate
      </Typography>
      
      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2, alignItems: 'center' }}>
        {/* Upload Button */}
        <Button
          variant="contained"
          component="label"
          startIcon={<UploadFileIcon />}
          color="primary"
        >
          Upload Requirements Document
          <input
            hidden
            type="file"
            onChange={handleFileChange}
            accept=".pdf,.docx,.txt,.json"
          />
        </Button>
        
        {/* File name display */}
        {selectedFile && (
          <Typography variant="body2" sx={{ ml: 1 }}>
            {selectedFile.name}
          </Typography>
        )}
        
        {/* Generate Button */}
        <Button
          variant="contained"
          color="secondary"
          startIcon={<PlayArrowIcon />}
          disabled={!fileUploaded || generating}
          onClick={handleGenerate}
        >
          Generate Test Cases
        </Button>
        
        {/* Regenerate Button - only visible after generation */}
        {fileUploaded && !generating && (
          <Button
            variant="outlined"
            color="primary"
            startIcon={<AutorenewIcon />}
            onClick={handleOpenRegenerateDialog}
          >
            Regenerate Test Cases
          </Button>
        )}
      </Box>
      
      {/* Error message */}
      {error && (
        <Alert severity="error" sx={{ mt: 2 }}>
          {error}
        </Alert>
      )}
      
      {/* Progress indicator */}
      {generating && (
        <Box sx={{ width: '100%', mt: 2 }}>
          <LinearProgress variant={selectedFile && !fileUploaded ? "determinate" : "indeterminate"} value={uploadProgress} />
          <Typography variant="body2" sx={{ mt: 1 }}>
            {!fileUploaded && selectedFile ? `Uploading file: ${Math.round(uploadProgress)}%` : 
             fileUploaded ? 'Generating test cases...' : 'Regenerating test cases...' }
          </Typography>
        </Box>
      )}
      
      {/* Regenerate Dialog */}
      <Dialog open={regenerateDialogOpen} onClose={handleCloseRegenerateDialog} maxWidth="sm" fullWidth>
        <DialogTitle>Refine Test Case Generation</DialogTitle>
        <DialogContent>
          <Typography variant="body2" paragraph>
            Please answer the following questions to help refine the regenerated test cases:
          </Typography>
          
          {clarifyingQuestions.map((question) => (
            <FormControl component="fieldset" key={question.id} sx={{ mb: 3, width: '100%' }}>
              <FormLabel component="legend">{question.question}</FormLabel>
              
              {question.options.length <= 2 ? (
                <RadioGroup
                  value={answers[question.id] || ''}
                  onChange={(e) => handleAnswerChange(question.id, e.target.value)}
                >
                  {question.options.map((option) => (
                    <FormControlLabel key={option} value={option} control={<Radio />} label={option} />
                  ))}
                </RadioGroup>
              ) : (
                <Box sx={{ ml: 1, mt: 1 }}>
                  {question.options.map((option) => (
                    <FormControlLabel
                      key={option}
                      control={
                        <Checkbox
                          checked={answers[question.id]?.includes(option) || false}
                          onChange={() => handleCheckboxChange(question.id, option)}
                        />
                      }
                      label={option}
                    />
                  ))}
                </Box>
              )}
            </FormControl>
          ))}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseRegenerateDialog}>Cancel</Button>
          <Button onClick={handleSubmitRegeneration} variant="contained" color="primary">
            Submit & Regenerate
          </Button>
        </DialogActions>
      </Dialog>
      
      {/* Snackbar for notifications */}
      <Snackbar
        open={snackbarOpen}
        autoHideDuration={6000}
        onClose={() => setSnackbarOpen(false)}
        message={snackbarMessage}
      />
    </Paper>
  );
};

export default TestCaseControls;