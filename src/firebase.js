// Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";
import { getAnalytics } from "firebase/analytics";
import { getStorage, connectStorageEmulator } from "firebase/storage";
import { getAuth, signInAnonymously } from "firebase/auth";

// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries

// Your web app's Firebase configuration
// For Firebase JS SDK v7.20.0 and later, measurementId is optional
console.log("Firebase Environment Variables:", process.env);
const firebaseConfig = {
	apiKey: "AIzaSyBSHPpvhnrH2KRR_M4NBa1WwZ98B70dO7Y",
	authDomain: "workshop2-471011.firebaseapp.com",
	projectId: "workshop2-471011",
	storageBucket: "workshop2-471011.firebasestorage.app",
	messagingSenderId: "1089122624415",
	appId: "1:1089122624415:web:31f15edd877479eefa93aa",
	measurementId: "G-JNLEK6XSVN",
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