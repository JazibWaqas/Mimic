import { BrowserRouter as Router, Routes, Route, Navigate, Outlet } from "react-router-dom";
import { createContext, useContext, useEffect, useState, Suspense, lazy } from "react";
import { auth } from "./services/firebase";
import PageLoader from "./components/PageLoader";
import './styles/pending-approval-popup.css';

// Lazy load the page components
const DashboardPage = lazy(() => import("./pages/DashboardPage"));
const FileIndexPage = lazy(() => import("./pages/FileIndexPage"));
const FileViewerPage = lazy(() => import("./pages/FileViewerPage"));
const FileEditPage = lazy(() => import("./pages/FileEditPage"));
const UploadFilePage = lazy(() => import("./pages/UploadFilePage"));
const PendingApprovalPage = lazy(() => import("./pages/PendingApprovalPage"));
const AccessDeniedPage = lazy(() => import("./pages/AccessDeniedPage"));

const AuthContext = createContext(null);
export function useAuth() {
  return useContext(AuthContext);
}
function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showPendingPopup, setShowPendingPopup] = useState(false);

  useEffect(() => {
    const unsubscribe = auth.onAuthStateChanged(async (firebaseUser) => {
      if (firebaseUser) {
        try {
            const response = await fetch(`/api/users/status/${firebaseUser.uid}`);
            const userData = await response.json();
            setUser({ firebaseUser, userData: userData || { status: 'pending' } });
            if (userData && userData.status === 'pending') {
              setShowPendingPopup(true);
            } else {
              setShowPendingPopup(false);
            }
        } catch (error) {
            setUser({ firebaseUser, userData: { status: 'pending' } });
            setShowPendingPopup(true);
        }
      } else {
        setUser(null);
        setShowPendingPopup(false);
      }
      setLoading(false);
    });
    return unsubscribe;
  }, []);
  
  const value = { user, setUser, loading };
  return (
    <AuthContext.Provider value={value}>
      {showPendingPopup && (
        <div className="pending-approval-popup">
          <div className="pending-approval-popup-content">
            <h2>Approval Pending</h2>
            <p>Your account is awaiting administrator approval. You will be notified by email once approved.</p>
            <button onClick={() => setShowPendingPopup(false)}>Close</button>
          </div>
        </div>
      )}
      {children}
    </AuthContext.Provider>
  );
}

function PrivateRoute() {
    const { user, loading } = useAuth();

    if (loading) {
        return <div>Loading...</div>;
    }
    
    if (!user) {
        // This could be a dedicated "Please log in to access this page" component
        return <UploadFilePage />; 
    }

    if (user.userData.status === 'pending') {
        return <PendingApprovalPage />;
    }

    if (user.userData.status === 'denied') {
        return <AccessDeniedPage />;
    }

    if (user.userData.status === 'approved') {
        return <Outlet />; // Renders the nested child route (e.g., FileEditPage)
    }

    return <AccessDeniedPage />;
}

function App() {
  return (
    <AuthProvider>
      <Router>
        <Suspense fallback={<PageLoader />}>
          <Routes>
            {/* Public Routes */}
            <Route path="/" element={<DashboardPage />} />
            <Route path="/file-index" element={<FileIndexPage />} />
            <Route path="/file-viewer/:id?" element={<FileViewerPage />} />
            

            {/* Protected Routes */}
            <Route element={<PrivateRoute />}>
            <Route path="/upload-file" element={<UploadFilePage />} />
              <Route path="/file-edit/:id" element={<FileEditPage />} />
            </Route>

          </Routes>
        </Suspense>
      </Router>
    </AuthProvider>
  );
}

export default App;