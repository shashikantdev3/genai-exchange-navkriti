// Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";
import { getAnalytics } from "firebase/analytics";
import { getStorage, connectStorageEmulator } from "firebase/storage";
import { getAuth, signInAnonymously } from "firebase/auth";

// Firebase config from .env
const firebaseConfig = {
  apiKey: process.env.REACT_APP_FIREBASE_API_KEY,
  authDomain: process.env.REACT_APP_FIREBASE_AUTH_DOMAIN,
  projectId: process.env.REACT_APP_FIREBASE_PROJECT_ID,
  storageBucket: process.env.REACT_APP_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: process.env.REACT_APP_FIREBASE_MESSAGING_SENDER_ID,
  appId: process.env.REACT_APP_FIREBASE_APP_ID,
  measurementId: process.env.REACT_APP_FIREBASE_MEASUREMENT_ID,
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const analytics = getAnalytics(app);
const auth = getAuth(app);
const storage = getStorage(app);

// Sign in anonymously to allow storage access
// Only sign in if not already authenticated
if (!auth.currentUser) {
  signInAnonymously(auth)
    .then(() => {
      console.log('Signed in anonymously to Firebase');
    })
    .catch((error) => {
      console.error('Anonymous auth error:', error.code, error.message);
    });
} else {
  console.log('User already authenticated:', auth.currentUser.uid);
}

export { app, analytics, storage, auth };