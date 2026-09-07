// Firebase initialization for Between Books
// Uses Firebase v10 modular SDK via CDN (no npm install needed)

import { initializeApp } from "https://www.gstatic.com/firebasejs/10.13.0/firebase-app.js";
import {
    getAuth,
    createUserWithEmailAndPassword,
    signInWithEmailAndPassword,
    signOut,
    onAuthStateChanged
} from "https://www.gstatic.com/firebasejs/10.13.0/firebase-auth.js";
import {
    getFirestore,
    doc,
    setDoc,
    getDoc,
    updateDoc
} from "https://www.gstatic.com/firebasejs/10.13.0/firebase-firestore.js";

// TODO: replace apiKey below with your real key from Firebase Console
// (Project Settings > General > Your apps > SDK setup and configuration)
const firebaseConfig = {
    apiKey: "AIzaSyDy2Lt8SYct4Bl8H01zujxdSPnApcZlYMc",
    authDomain: "between-books-music.firebaseapp.com",
    projectId: "between-books-music",
    storageBucket: "between-books-music.firebasestorage.app",
    messagingSenderId: "91021115177",
    appId: "1:91021115177:web:ebfd751a10df79246b0138",
    measurementId: "G-030QG7QR0B"
};

const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const db = getFirestore(app);

export {
    auth,
    db,
    createUserWithEmailAndPassword,
    signInWithEmailAndPassword,
    signOut,
    onAuthStateChanged,
    doc,
    setDoc,
    getDoc,
    updateDoc
};