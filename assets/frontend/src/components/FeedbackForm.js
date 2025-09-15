import React, { useState } from 'react';
import { Box, TextField, Button, Typography } from '@mui/material';

export default function FeedbackForm({ onSubmit }) {
  const [feedback, setFeedback] = useState('');

  // Optional: Pre-fill dummy feedback for demonstration/testing purposes
  // Remove or comment out for production
  React.useEffect(() => {
    setFeedback(
      "The generated test cases look comprehensive but please review edge case scenarios in TC-002. The UI is very user-friendly and the upload process is smooth. Looking forward to continuous improvements in accuracy and reporting."
    );
  }, []);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (feedback.trim()) {
      onSubmit(feedback.trim());
      setFeedback('');
      alert('Thank you for your feedback!');
    }
  };

  return (
    <Box component="form" onSubmit={handleSubmit} sx={{ mt: 4 }}>
      <Typography variant="h6" gutterBottom>Feedback</Typography>
      <TextField
        label="Enter your feedback"
        value={feedback}
        onChange={e => setFeedback(e.target.value)}
        fullWidth
        multiline
        rows={4}
        inputProps={{ maxLength: 500 }}
        required
      />
      <Button sx={{ mt: 2 }} type="submit" variant="contained">Submit</Button>
    </Box>
  );
}
