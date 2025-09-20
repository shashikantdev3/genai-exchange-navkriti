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
  
  // Check authentication state
  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, (user) => {
      if (user) {
        // User is signed in
        console.log('User is authenticated:', user.uid);
        setIsAuthenticated(true);
      } else {
        // User is signed out
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

  // Handle file selection
  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (!file) return;
    
    if (!ALLOWED_TYPES.includes(file.type)) {
      setError('Only PDF, Word, Text, or API spec files allowed.');
      return;
    }
    
    console.log('File selected:', file.name, file.type, file.size);
    console.log('Firebase storage object:', storage);
    console.log('Authentication status:', isAuthenticated, 'Current user:', auth.currentUser?.uid);
    
    setSelectedFile(file);
    setFileUploaded(false);
    setError('');
    setGenerating(true);
    setUploadProgress(0);
    
    // Check if user is authenticated before uploading
    if (!isAuthenticated) {
      console.log('Waiting for authentication before uploading...');
      setSnackbarMessage('Authenticating before upload...');
      setSnackbarOpen(true);
      
      // Wait for authentication to complete (max 5 seconds)
      let authCheckCount = 0;
      const authCheckInterval = setInterval(() => {
        authCheckCount++;
        if (auth.currentUser) {
          clearInterval(authCheckInterval);
          console.log('Authentication completed, proceeding with upload');
          uploadFile(file);
        } else if (authCheckCount >= 10) { // 5 seconds (10 * 500ms)
          clearInterval(authCheckInterval);
          setError('Authentication failed. Please try again.');
          setGenerating(false);
        }
      }, 500);
    } else {
      uploadFile(file);
    }
  };
  
  // Function to handle file upload
  const uploadFile = (file) => {
    try {
      // Create a storage reference
      const storageRef = ref(storage, `requirements/${file.name}`);
      console.log('Storage reference created:', storageRef);
      
      // Upload file to Firebase Storage
      const uploadTask = uploadBytesResumable(storageRef, file);
      console.log('Upload task created');
      
      // Monitor upload progress
      uploadTask.on(
        'state_changed',
        (snapshot) => {
          // Track and update upload progress
          const progress = (snapshot.bytesTransferred / snapshot.totalBytes) * 100;
          console.log(`Upload progress: ${progress}%, transferred: ${snapshot.bytesTransferred}, total: ${snapshot.totalBytes}`);
          setUploadProgress(progress);
        },
        (error) => {
          // Handle errors
          console.error('Upload error code:', error.code);
          console.error('Upload error message:', error.message);
          console.error('Full error object:', JSON.stringify(error));
          setError(`Upload failed: ${error.message}`);
          setGenerating(false);
        },
        () => {
          // Upload completed successfully
          console.log('Upload completed successfully');
          getDownloadURL(uploadTask.snapshot.ref).then((downloadURL) => {
            console.log('File available at', downloadURL);
            setFileUploaded(true);
            setGenerating(false);
            
            // Show success message
            setSnackbarMessage(`File "${file.name}" uploaded successfully to Firebase`);
            setSnackbarOpen(true);
          }).catch(err => {
            console.error('Error getting download URL:', err);
            setError(`Error getting download URL: ${err.message}`);
            setGenerating(false);
          });
        }
      );
    } catch (err) {
      console.error('Error setting up upload:', err);
      setError(`Error setting up upload: ${err.message}`);
      setGenerating(false);
    }
  };

  // Handle generate button click
  const handleGenerate = () => {
    if (!fileUploaded) return;
    
    setGenerating(true);
    
    // Simulate API call with timeout
    setTimeout(() => {
      setGenerating(false);
      
      // Call parent handler
      if (onGenerate) {
        onGenerate({
          fileName: selectedFile.name,
          fileType: selectedFile.type,
          fileSize: selectedFile.size
        });
      }
      
      // Show success message
      setSnackbarMessage('Test cases generated successfully');
      setSnackbarOpen(true);
    }, 2000);
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