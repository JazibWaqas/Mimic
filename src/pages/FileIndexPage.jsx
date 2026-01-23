import React, { useState, useEffect, useRef, useCallback, useMemo } from 'react';
import '../styles/FileIndex.css';
import ShinyText from '../components/ShinyText';
import Header from '../components/Header.jsx';
import CategorySidebar from '../components/CategorySidebar.jsx';
import { useNavigate, useLocation } from 'react-router-dom';
import { FiFile, FiEye, FiDownload, FiLoader, FiX, FiSearch, FiFilter, FiCalendar, FiPlus, FiMenu } from 'react-icons/fi';
import FileCard from '../components/FileCard.jsx';
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import { useAuth } from '../App';
import { getIdToken } from 'firebase/auth';

export default function FileIndexPage() {
  
  const [recentFiles, setRecentFiles] = useState([]);
  const [categories, setCategories] = useState([]);
  const [allFiles, setAllFiles] = useState([]);
  const [isLoadingFiles, setIsLoadingFiles] = useState(true);
  const [isLoadingCategories, setIsLoadingCategories] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [showCategoryFilter, setShowCategoryFilter] = useState(false);
  const [expandedCategory, setExpandedCategory] = useState(null);
  const [selectedCategory, setSelectedCategory] = useState('');
  const [selectedSubCategory, setSelectedSubCategory] = useState('');
  const [selectedYear, setSelectedYear] = useState('');
  const [showYearFilter, setShowYearFilter] = useState(false);
  const [error, setError] = useState(null);
  const [successMessage, setSuccessMessage] = useState(null);
  const [lastVisible, setLastVisible] = useState(null);
  const [hasMoreFiles, setHasMoreFiles] = useState(false);
  const [isLoadingMore, setIsLoadingMore] = useState(false);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  const debounceTimeout = useRef(null);
  const { user, loading: authLoading } = useAuth();

  // Fetch categories and initial files
  useEffect(() => {
    const fetchCategories = async () => {
      setIsLoadingCategories(true);
      try {
        const res = await fetch('/api/categories');
        if (!res.ok) throw new Error('Failed to fetch categories');
        const categoriesData = await res.json();
        const financialStatements = categoriesData.filter(cat => cat === 'Financial Statements');
        const other = categoriesData.filter(cat => cat === 'Other');
        const rest = categoriesData.filter(cat => cat !== 'Financial Statements' && cat !== 'Other');
        setCategories([...financialStatements, ...rest, ...other]);
      } catch (err) {
        setError(err.message);
      } finally {
        setIsLoadingCategories(false);
      }
    };
    fetchCategories();
  }, []);

  // Fetch paginated files (All Files)
  const fetchFiles = useCallback(async (reset = false, search = searchTerm) => {
    if (reset) {
      setIsLoadingFiles(true);
      setAllFiles([]);
      setLastVisible(null);
    } else {
      setIsLoadingMore(true);
    }
    setError(null);
    try {
      const params = new URLSearchParams({
        category: selectedCategory,
        subCategory: selectedSubCategory,
        year: selectedYear,
        search: search,
        limit: 16,
        ...(lastVisible && !reset ? { startAfter: lastVisible } : {})
      });
      const res = await fetch(`/api/files/paginated?${params}`);
      if (!res.ok) throw new Error('Failed to fetch files');
      const { files, lastVisible: newLastVisible, hasNextPage } = await res.json();
      setAllFiles(prev => reset ? files : [...prev, ...files]);
      setLastVisible(newLastVisible);
      setHasMoreFiles(hasNextPage);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoadingFiles(false);
      setIsLoadingMore(false);
    }
  }, [selectedCategory, selectedSubCategory, selectedYear, lastVisible]);

  // Fetch recent files (limit 4, same filters)
  const fetchRecentFiles = useCallback(async (search = searchTerm) => {
    try {
      const params = new URLSearchParams({
        category: selectedCategory,
        subCategory: selectedSubCategory,
        year: selectedYear,
        search: search,
        limit: 4
      });
      const res = await fetch(`/api/files/paginated?${params}`);
      if (!res.ok) throw new Error('Failed to fetch recent files');
      const { files } = await res.json();
      setRecentFiles(files);
    } catch (err) {
      setRecentFiles([]);
    }
  }, [selectedCategory, selectedSubCategory, selectedYear]);

  // Effect for initial load and filter changes (but not search)
  useEffect(() => {
    fetchFiles(true);
    fetchRecentFiles();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedCategory, selectedSubCategory, selectedYear]);

  // Effect for handling search term changes with debounce
  useEffect(() => {
    if (debounceTimeout.current) {
      clearTimeout(debounceTimeout.current);
    }
    debounceTimeout.current = setTimeout(() => {
      fetchFiles(true, searchTerm);
      fetchRecentFiles(searchTerm);
    }, 500); // 500ms debounce delay

    return () => {
      if (debounceTimeout.current) {
        clearTimeout(debounceTimeout.current);
      }
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [searchTerm]);

  // Responsive sidebar
  useEffect(() => {
    const handleResize = () => setIsSidebarOpen(window.innerWidth >= 900);
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  useEffect(() => {
    if (location.state?.message) {
      setSuccessMessage(location.state.message);
      const timer = setTimeout(() => {
        setSuccessMessage(null);
        navigate(location.pathname, { replace: true });
      }, 3000);
      return () => clearTimeout(timer);
    }
  }, [location, navigate]);

  const handleViewFile = useCallback((fileId) => navigate(`/file-viewer/${fileId}`), [navigate]);
  const handleDownload = useCallback(async (fileId, fileName) => {
    // Find the file object from allFiles or recentFiles
    const fileObj = allFiles.find(f => f._id === fileId) || recentFiles.find(f => f._id === fileId);
    // If file requires authentication
    if (fileObj && fileObj.requiresAuth) {
      if (authLoading) {
        toast.info('Checking authentication...');
        return;
      }
      if (!user) {
        toast.info('You must be signed in to download this file.');
        return;
      }
      if (user.userData?.status !== 'approved') {
        toast.info('Only approved users can download this file.');
        return;
      }
    }
    try {
      let headers = {};
      if (fileObj && fileObj.requiresAuth && user && user.firebaseUser) {
        const token = await getIdToken(user.firebaseUser);
        headers['Authorization'] = `Bearer ${token}`;
      }
      const response = await fetch(`/api/files/${fileId}`, { headers });
      if (response.status === 401) {
        toast.info('Sign in required.');
        return;
      }
      if (!response.ok) {
        toast.error('Failed to download file. Please try again.');
        return;
      }
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = fileName;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      toast.error('Failed to download file. Please try again.');
    }
  }, [allFiles, recentFiles, user, authLoading]);
  const handleSearchChange = (e) => {
    setSearchTerm(e.target.value);
  };
  const handleCategorySelect = useCallback((cat, sub, isSubCategory) => {
    setSelectedCategory(cat);
    setSelectedSubCategory(sub);
    if (isSubCategory) setIsSidebarOpen(false); // Only close sidebar if a subcategory is selected
  }, []);
  const getUniqueYears = useMemo(() => {
    const years = Array.from(new Set(allFiles.map(file => file.year))).filter(Boolean);
    return years.sort((a, b) => b - a);
  }, [allFiles]);
  const handleLoadMore = useCallback(() => {
    fetchFiles(false);
  }, [fetchFiles]);
  const getSectionTitle = useMemo(() => {
    if (selectedSubCategory) return selectedSubCategory;
    if (selectedCategory) return selectedCategory;
    if (searchTerm) return `Search Results`;
    return 'Recently Uploaded Files';
  }, [selectedCategory, selectedSubCategory, searchTerm]);
  if (error) {
    return (
      <div className="app-root">
        <Header />
        <main className="main-content">
          <div className="error-container">
            <h2>Error Loading Files</h2>
            <p>{error}</p>
            <button onClick={() => window.location.reload()} className="retry-button">
              Retry
            </button>
          </div>
        </main>
      </div>
    );
  }
  return (
    <div className="app-root">
      <Header />
      <main className="main-content">
        <div className={`file-index-layout ${isSidebarOpen ? 'sidebar-open' : ''}`}>
        <div
  className="sidebar-container"
  onClick={(e) => e.stopPropagation()} // ✅ this is the fix
>
  <CategorySidebar onSelect={handleCategorySelect} />
</div>


          {isSidebarOpen && <div className="sidebar-overlay" onClick={() => setIsSidebarOpen(false)}></div>}

          <div className="file-index-page-content">
            <div className="page-header">
              <button className="sidebar-toggle-btn" onClick={() => setIsSidebarOpen(!isSidebarOpen)}>
                {isSidebarOpen ? <FiX /> : <FiMenu />}
                <span>Categories</span>
              </button>
              

            </div>

            {successMessage && (
              <div className="success-message">
                {successMessage}
              </div>
            )}

            <div className="search-filter-bar">
              <div className="search-container">
                <FiSearch className="search-icon" />
                <input
                  type="text"
                  placeholder="Search files..."
                  className="search-input"
                  value={searchTerm}
                  onChange={handleSearchChange}
                />
              </div>
              
              <div className="filter-container">
                <button
                  className={`filter-button ${selectedYear ? 'active' : ''}`}
                  onClick={() => setShowYearFilter(!showYearFilter)}
                >
                  <FiCalendar />
                  Year {selectedYear && `(${selectedYear})`}
                </button>
                {showYearFilter && (
                  <div className="filter-dropdown">
                    {getUniqueYears.map(year => (
  <button
    key={year}
    className={`filter-option ${selectedYear === year ? 'selected' : ''}`}
    onClick={() => {
      setSelectedYear(year);
      setShowYearFilter(false); // <-- Close dropdown after selection
    }}
  >
    {year}
  </button>
))}
                  </div>
                )}
              </div>
              {(selectedCategory || selectedYear) && (
                <button
                  className="clear-filters-button"
                  onClick={() => {
                    setSelectedCategory('');
                    setSelectedSubCategory('');
                    setSelectedYear('');
                  }}
                >
                  <FiX /> Clear Filters
                </button>
              )}
            </div>
            {/* Filtered/Category Section */}
            <section className="files-section">
            <ShinyText text={getSectionTitle} className="files-section-title" />

              <div className="files-scroll-grid">
                {isLoadingFiles ? (
                  <div className="loading-indicator" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', width: '100%', minHeight: '120px' }}>
                    <FiLoader className="spinner-icon" />
                    <p>Loading files...</p>
                  </div>
                ) : recentFiles.length === 0 ? (
                  <div className="empty-state">
                    <FiFile className="empty-icon" />
                    <p>No files found</p>
                  </div>
                ) : (
                  recentFiles.map((file) => (
                    <FileCard
                      key={file._id}
                      file={file}
                      onView={handleViewFile}
                      onDownload={handleDownload}
                    />
                  ))
                )}
              </div>
            </section>
            {/* All Files Section */}
            <section className="all-files-section">
              <ShinyText text="All Files" className="all-files-title" />
              <div className="all-files-scroll-grid">
                {isLoadingFiles && allFiles.length === 0 ? (
                  <div className="loading-indicator" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', width: '100%', minHeight: '120px' }}>
                    <FiLoader className="spinner-icon" />
                    <p>Loading files...</p>
                  </div>
                ) : allFiles.length === 0 ? (
                  <div className="empty-state">
                    <FiFile className="empty-icon" />
                    <p>No files found matching your criteria</p>
                  </div>
                ) : (
                  <>
                    {allFiles.map((file) => (
                      <FileCard
                        key={file._id}
                        file={file}
                        onView={handleViewFile}
                        onDownload={handleDownload}
                      />
                    ))}
                    {hasMoreFiles && (
                      <div className="load-more-container">
                        <button className="load-more-button" onClick={handleLoadMore} disabled={isLoadingMore}>
                          <FiPlus className="load-more-icon" />
                          {isLoadingMore ? 'Loading...' : 'Load More'}
                        </button>
                      </div>
                    )}
                  </>
                )}
              </div>
            </section>
          </div>
        </div>
        <ToastContainer
          position="top-right"
          autoClose={4000}
          hideProgressBar={false}
          newestOnTop={false}
          closeOnClick
          rtl={false}
          pauseOnFocusLoss
          draggable
          pauseOnHover
          theme="colored"
        />
      </main>
    </div>
  );
}