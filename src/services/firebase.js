import { initializeApp } from 'firebase/app';
import { getAuth, GoogleAuthProvider, signInWithPopup, signOut } from 'firebase/auth';

const firebaseConfig= {
apiKey: "AIzaSyDP-0zAhfsiBsYSYTZ2yis0ZzOXHd6kf7Q",
authDomain: "auraxkhidmat-f4c73.firebaseapp.com",
projectId: "auraxkhidmat-f4c73",
storageBucket: "auraxkhidmat-f4c73.firebasestorage.app",
messagingSenderId: "267970086214",
appId: "1:267970086214:web:0fac2101fd29f55a4d9147",
measurementId: "G-C580KTG8P5"
};


const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);

const provider = new GoogleAuthProvider();

export const signInWithGoogle = async () => {
  try {
    const result = await signInWithPopup(auth, provider);
    const { user } = result;

    // After successful sign-in, notify our backend
    const response = await fetch('/api/users/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        uid: user.uid,
        email: user.email,
        displayName: user.displayName,
      }),
    });

    if (!response.ok) {
      throw new Error('Failed to sync user with backend');
    }

    const userData = await response.json();
    return userData; // This will include the user's status
  } catch (error) {
    console.error("Error signing in with Google: ", error);
  }
};

export const signOutUser = async () => {
  try {
    await signOut(auth);
  } catch (error) {
    console.error("Error signing out: ", error);
  }
}; 