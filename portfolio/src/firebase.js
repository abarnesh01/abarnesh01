// src/firebase.js
import { initializeApp } from "firebase/app";
import { getAuth, GoogleAuthProvider, signInWithPopup, signOut } from "firebase/auth";
import { getFirestore } from "firebase/firestore";

const firebaseConfig = {
  apiKey: "",
  authDomain: "",
  projectId: "",
  storageBucket: "",
  messagingSenderId: "",
  appId: ""
};

// Only initialize if API Key is provided
let app, auth, db;
const provider = new GoogleAuthProvider();

if (firebaseConfig.apiKey) {
  try {
    app = initializeApp(firebaseConfig);
    auth = getAuth(app);
    db = getFirestore(app);
  } catch (error) {
    console.error("Firebase initialization failed:", error);
  }
} else {
  console.warn("Firebase API Key is missing. Some features like Chat Room will not work.");
}

export { auth, db };
export const loginWithGoogle = () => {
  if (!auth) {
    alert("Firebase is not configured.");
    return Promise.reject("Firebase not configured");
  }
  return signInWithPopup(auth, provider);
};
export const logout = () => {
  if (!auth) return Promise.resolve();
  return signOut(auth);
};
