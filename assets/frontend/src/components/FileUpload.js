import React, { useState, useEffect } from 'react';
import { Box, Button, Typography, LinearProgress, Alert } from '@mui/material';
import UploadFileIcon from '@mui/icons-material/UploadFile';
import { getStorage, ref, uploadBytesResumable, getDownloadURL } from 'firebase/storage';
import { storage } from '../firebase';
import { getAuth, signInAnonymously, onAuthStateChanged } from "firebase/auth";


const ALLOWED_TYPES = [
  'application/pdf',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
];
const MAX_SIZE = 5 * 1024 * 1024; // 5MB

export default function FileUpload({ onUpload }) {
  const [selectedFile, setSelectedFile] = useState(null);
  const [error, setError] = useState('');
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [authUser, setAuthUser] = useState(null);
  const auth = getAuth();
  
  useEffect(() => {
  // Listen to auth state changes
  const unsubscribe = onAuthStateChanged(auth, (user) => {
    if (user) {
      // User is signed in
      setAuthUser(user);
    } else {
      // No user signed in, sign in anonymously
      signInAnonymously(auth)
        .then(({ user }) => {
          setAuthUser(user);
        })
        .catch((error) => {
          console.error("Anonymous sign-in failed", error);
        });
    }
  });

  // Cleanup subscription on unmount
  return () => unsubscribe();
  }, [auth]);

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
    if (!authUser) {
      console.log("User not signed in yet.");
      return;
    }
    if (!selectedFile) return;

    setUploading(true);
    setError('');
    setProgress(0);

    const fileRef = ref(storage, `uploads/${Date.now()}-${selectedFile.name}`);
    const uploadTask = uploadBytesResumable(fileRef, selectedFile);

    uploadTask.on(
      'state_changed',
      (snapshot) => {
        const percent = (snapshot.bytesTransferred / snapshot.totalBytes) * 100;
        setProgress(percent);
      },
      (err) => {
        console.error(err);
        setError('Upload failed. Please try again.');
        setUploading(false);
      },
      async () => {
        const downloadURL = await getDownloadURL(uploadTask.snapshot.ref);
        const uploadedData = {
          name: selectedFile.name,
          size: selectedFile.size,
          type: selectedFile.type,
          url: downloadURL,
        };

        onUpload(uploadedData); // <-- Pass to parent
        setSelectedFile(null);
        setUploading(false);
        setProgress(0);
      }
    );
  };

  return (
    <Box sx={{ my: 3 }}>
      <Typography variant="h6" gutterBottom>Upload Requirements Document</Typography>
      <Button
        variant="contained"
        component="label"
        startIcon={<UploadFileIcon />}
        sx={{ mr: 2 }}
        disabled={uploading}
      >
        Choose File
        <input hidden type="file" onChange={handleFileChange} />
      </Button>
      {selectedFile && (
        <Typography sx={{ display: 'inline-block', mr: 2 }}>
          {selectedFile.name}
        </Typography>
      )}
      <Button
        variant="outlined"
        onClick={handleUpload}
        disabled={!selectedFile || uploading}
      >
        {uploading ? 'Uploading...' : 'Upload'}
      </Button>
      {uploading && (
        <LinearProgress
          variant="determinate"
          value={progress}
          sx={{ mt: 2 }}
        />
      )}
      {error && (
        <Alert severity="error" sx={{ mt: 2 }}>
          {error}
        </Alert>
      )}
    </Box>
  );
}