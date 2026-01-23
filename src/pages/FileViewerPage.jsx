import React, { useState, useEffect, useRef } from 'react';
import '../styles/FileViewer.css';
import Header from '../components/Header.jsx';
import { useParams, useNavigate } from 'react-router-dom';
import { FiFile, FiEye, FiDownload, FiLoader, FiX, FiArrowLeft, FiInfo, FiCalendar, FiUser, FiFolder, FiTrash2, FiEdit, FiMaximize, FiMinimize, FiSearch, FiChevronLeft, FiChevronRight } from 'react-icons/fi';
import mammoth from 'mammoth/mammoth.browser';
import * as XLSX from 'xlsx';
import { HotTable } from '@handsontable/react';
import 'handsontable/dist/handsontable.full.min.css';
import '../styles/FileIndex.css';
import { useAuth } from '../App';
import FileCard from '../components/FileCard.jsx';
import { getIdToken } from 'firebase/auth';
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import ConfirmModal from '../components/ConfirmModal';
import Footer from '../components/Footer.jsx';

const isMobileDevice = () => {
  if (typeof navigator === 'undefined') return false;
  return /Mobi|Android|iPhone|iPad|iPod|Opera Mini|IEMobile|WPDesktop/i.test(navigator.userAgent);
};

const FileViewer = () => {
  const { id } = useParams();
  const [file, setFile] = useState(null);
  const [allFiles, setAllFiles] = useState([]);
  const [recentlyViewedFiles, setRecentlyViewedFiles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [previewData, setPreviewData] = useState(null);
  const [previewError, setPreviewError] = useState(null);
  const [excelSheets, setExcelSheets] = useState([]);
  const [activeSheet, setActiveSheet] = useState(null);
  const navigate = useNavigate();
  const { user, loading: authLoading } = useAuth();
  const [actionError, setActionError] = useState(null);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const previewRef = useRef(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedFileId, setSelectedFileId] = useState(null);
  const [isSearching, setIsSearching] = useState(false);
  const scrollRef = useRef(null);
  const [showConfirm, setShowConfirm] = useState(false);
  const [deleting, setDeleting] = useState(false);

  // Load recently viewed files from database
  useEffect(() => {
    const fetchRecentlyViewed = async () => {
      if (!user?.firebaseUser?.uid) {
        setRecentlyViewedFiles([]);
        return;
      }
      
      try {
        const res = await fetch(`/api/files/recently-viewed/${user.firebaseUser.uid}?limit=4`);
        
        if (res.ok) {
          const data = await res.json();
          setRecentlyViewedFiles(data);
        } else {
          const errorText = await res.text();
          console.error('Failed to fetch recently viewed files. Status:', res.status, 'Error:', errorText);
        }
      } catch (err) {
        console.error('Error fetching recently viewed files:', err);
        setRecentlyViewedFiles([]);
      }
    };
    
    fetchRecentlyViewed();
  }, [user?.firebaseUser?.uid]);

  // Add file to recently viewed in database
  const addToRecentlyViewed = async (fileData) => {
    
    if (!fileData || !user?.firebaseUser?.uid) {
      return;
    }
    
    try {
      const res = await fetch('/api/files/recently-viewed', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          fileId: fileData._id,
          userId: user.firebaseUser.uid
        })
      });
      
      if (res.ok) {
        // Refresh the recently viewed files list
        const refreshRes = await fetch(`/api/files/recently-viewed/${user.firebaseUser.uid}?limit=4`);
        
        if (refreshRes.ok) {
          const data = await refreshRes.json();
          setRecentlyViewedFiles(data);
        } else {
          const errorText = await refreshRes.text();
          console.error('Failed to refresh recently viewed files. Status:', refreshRes.status, 'Error:', errorText);
        }
      } else {
        const errorText = await res.text();
        console.error('Failed to add file to recently viewed. Status:', res.status, 'Error:', errorText);
      }
    } catch (err) {
      console.error('Error adding to recently viewed:', err);
    }
  };

  useEffect(() => {
    const fetchFiles = async () => {
      try {
        const res = await fetch('/api/files');
        if (!res.ok) throw new Error('Failed to fetch files');
        const data = await res.json();
        setAllFiles(data.sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt)));
      } catch (err) {
        setAllFiles([]);
      } finally {
        // If no file is selected, stop loading after files are loaded
        if (!id) setLoading(false);
      }
    };
    fetchFiles();
  }, []);

  // Always sync selectedFileId with URL param or default to null
  useEffect(() => {
    if (id && allFiles.some(f => f._id === id)) {
      setSelectedFileId(id);
    } else if (!id) {
      setSelectedFileId(null);
    }
  }, [id, allFiles]);

  // Always exit fullscreen when navigating to a new file or on mount
  useEffect(() => {
    if (document.fullscreenElement) {
      document.exitFullscreen();
    }
    setIsFullscreen(false);
  }, [selectedFileId]);

  // When selectedFileId changes, fetch and show that file
  useEffect(() => {
    let pdfObjectUrl = null; // Track PDF object URL for cleanup
    if (!selectedFileId) {
      setFile(null);
      setLoading(false); // Stop loading if no file is selected
      return;
    }
    // Wait for authLoading to be false before attempting fetch
    if (authLoading) {
      setLoading(true);
      return;
    }
    const fetchFile = async () => {
      setLoading(true);
      setError(null);
      setPreviewError(null);
      setPreviewData(null);
      try {
        const detailsRes = await fetch(`/api/files/${selectedFileId}/details`);
        if (!detailsRes.ok) throw new Error(detailsRes.status === 404 ? 'File not found' : 'Error fetching file details');
        const fileDetails = await detailsRes.json();
        setFile(fileDetails);
        // Add to recently viewed
        addToRecentlyViewed(fileDetails);
        // If file is private and user is not logged in, show message and do not fetch preview
        if (fileDetails.requiresAuth && !user) {
          setError('\🔒\ This is a private file. Only logged-in users can preview its contents. Please sign in to continue.');
          return;
        }
        // Prepare headers for private files
        let headers = {};
        if (fileDetails.requiresAuth && user && user.firebaseUser) {
          const token = await getIdToken(user.firebaseUser);
          headers['Authorization'] = `Bearer ${token}`;
        }
        // PDF preview
        if (fileDetails.fileType === 'pdf') {
          const viewResponse = await fetch(`/api/files/${selectedFileId}/view`, { headers });
          if (viewResponse.status === 401) {
            setError('Sign in required.');
            return;
          }
          if (viewResponse.ok) {
            const blob = await viewResponse.blob();
            pdfObjectUrl = URL.createObjectURL(blob);
            fileDetails.url = pdfObjectUrl;
            setFile(fileDetails);
          }
        } else if (
          fileDetails.fileType === 'csv'
        ) {
          // CSV preview
          setLoading(true);
          const previewResponse = await fetch(`/api/files/${selectedFileId}/preview`, { headers });
          if (previewResponse.status === 401) {
            setError('Sign in required.');
            return;
          }
          if (previewResponse.ok) {
            const previewData = await previewResponse.json();
            setPreviewData(previewData);
            if (!previewData.headers || previewData.headers.length === 0) {
              setPreviewError('No data found in this file.');
            }
          } else {
            setPreviewError('Failed to load preview data.');
          }
        } else if (
          fileDetails.fileType === 'excel' ||
          fileDetails.fileType === 'xlsx' ||
          fileDetails.fileType === 'xls'
        ) {
          // Excel preview (xlsx, xls)
          try {
            setPreviewData(null);
            setPreviewError(null);
            setLoading(true);
            const viewResponse = await fetch(`/api/files/${selectedFileId}/view`);
            if (viewResponse.ok) {
              const arrayBuffer = await viewResponse.arrayBuffer();
              const workbook = XLSX.read(arrayBuffer, { type: 'array' });
              const sheetData = workbook.SheetNames.map((sheetName) => {
                const sheet = workbook.Sheets[sheetName];
                const data = XLSX.utils.sheet_to_json(sheet, { header: 1, defval: '' });
                return { name: sheetName, data };
              });
              setExcelSheets(sheetData);
              setActiveSheet(sheetData[0]);
            } else {
              setPreviewError('Failed to load Excel file.');
            }
          } catch (err) {
            setPreviewError('Error processing Excel file.');
          }
        } else if (
          fileDetails.fileType === 'docx' ||
          fileDetails.fileType === 'doc'
        ) {
          // Word preview (docx, doc)
          try {
            setPreviewData(null);
            setPreviewError(null);
            setLoading(true);
            const viewResponse = await fetch(`/api/files/${selectedFileId}/view`);
            if (viewResponse.ok) {
              const arrayBuffer = await viewResponse.arrayBuffer();
              const result = await mammoth.convertToHtml({ arrayBuffer });
              setPreviewData(result.value);
            } else {
              setPreviewError('Failed to load document preview.');
            }
          } catch (err) {
            setPreviewError('Error loading document preview.');
          }
        }
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };
    fetchFile();
    // Clean up object URLs for PDF (and future blob previews)
    return () => {
      if (pdfObjectUrl) URL.revokeObjectURL(pdfObjectUrl);
    };
  }, [selectedFileId, user, authLoading]);

  // Filter files for scroll box based on search or show recently viewed
  const getScrollBoxFiles = () => {
    if (isSearching && searchTerm.trim()) {
      const searchResults = allFiles.filter(f => {
        const matchesSearch = (
          (f.originalName || f.filename || f.name || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
          (f.category || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
          (f.year || '').toString().includes(searchTerm)
        );
        return matchesSearch;
      });
      return searchResults;
    }
    
    // Show recently viewed files when not searching
    // If no recently viewed files, show the 4 most recent files from allFiles
    if (recentlyViewedFiles.length === 0 && allFiles.length > 0) {
      const fallbackFiles = allFiles.slice(0, 4);
      return fallbackFiles;
    }
    
    // If we have recently viewed files but less than 4, pad with recent files
    if (recentlyViewedFiles.length > 0 && recentlyViewedFiles.length < 4) {
      const usedIds = new Set(recentlyViewedFiles.map(f => f._id));
      const additionalFiles = allFiles
        .filter(f => !usedIds.has(f._id))
        .slice(0, 4 - recentlyViewedFiles.length);
      
      const paddedFiles = [...recentlyViewedFiles, ...additionalFiles];
      return paddedFiles;
    }
    
    return recentlyViewedFiles;
  };

  const scrollBoxFiles = getScrollBoxFiles();

  const scrollByAmount = (amount) => {
    if (scrollRef.current) {
      scrollRef.current.scrollBy({ left: amount, behavior: 'smooth' });
    }
  };

  // Handle search input
  const handleSearchChange = (e) => {
    const value = e.target.value;
    setSearchTerm(value);
    setIsSearching(value.trim().length > 0);
  };

  // Clear search
  const clearSearch = () => {
    setSearchTerm('');
    setIsSearching(false);
  };

  // Helper: is user approved
  const isApproved = user?.userData?.status === 'approved';

  // Handlers
  const handleDownload = async (fileId, fileName) => {
    if (!isApproved) {
      toast.info('Only approved users can download files. Please log in and get approved.');
      return;
    }
    try {
      const response = await fetch(`/api/files/${fileId}`);
      if (response.status === 401) {
        toast.info('Sign in required.');
        return;
      }
      if (!response.ok) throw new Error('Failed to download file');
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
  };
  const handleEditClick = () => {
    if (isApproved) {
      navigate(`/file-edit/${file._id}`);
    } else {
      toast.info('Only approved users can edit files. Please log in and get approved.');
    }
  };
  const handleDelete = async () => {
    setShowConfirm(true);
  };
  const confirmDelete = async () => {
    if (!file || !file._id) return;
    setDeleting(true);
    try {
      const response = await fetch(`/api/files/${file._id}`, { method: 'DELETE' });
      if (!response.ok) throw new Error((await response.json()).message || 'Failed to delete file');
      toast.success('File deleted successfully!');
      navigate('/file-index');
    } catch (error) {
      toast.error(error.message || 'Failed to delete file.');
      setDeleting(false);
    }
  };
  const handleDeleteClick = () => {
    if (isApproved) {
      handleDelete();
    } else {
      toast.info('Only approved users can delete files. Please log in and get approved.');
    }
  };
  const handleToggleFullscreen = () => {
    const elem = previewRef.current;
    if (!elem) return;
    if (!document.fullscreenElement) {
      elem.requestFullscreen();
      setIsFullscreen(true);
    } else {
      document.exitFullscreen();
      setIsFullscreen(false);
    }
  };
  useEffect(() => {
    const onFullscreenChange = () => {
      if (!document.fullscreenElement) setIsFullscreen(false);
    };
    document.addEventListener('fullscreenchange', onFullscreenChange);
    return () => document.removeEventListener('fullscreenchange', onFullscreenChange);
  }, []);

  // Helper to render spreadsheet previews
  const renderSpreadsheet = () => {
    if (previewError) return <div className="spreadsheet-error">{previewError}</div>;
    if (file?.fileType === 'excel' || file?.fileType === 'xlsx') {
      if (!activeSheet?.data?.length) return <div className="spreadsheet-error">No data found in this sheet.</div>;
      const headers = activeSheet.data[0];
      const tableData = activeSheet.data.slice(1);
      return (
        <div className="spreadsheet-preview-container handsontable-container">
          {excelSheets.length > 1 && (
            <div className="sheet-select-row">
              <label htmlFor="sheetSelect" className="sheet-select-label">Sheet:</label>
              <select
                id="sheetSelect"
                value={activeSheet.name}
                onChange={e => setActiveSheet(excelSheets.find(s => s.name === e.target.value))}
                className="sheet-select-dropdown"
              >
                {excelSheets.map(sheet => (
                  <option key={sheet.name} value={sheet.name}>{sheet.name}</option>
                ))}
              </select>
            </div>
          )}
          <HotTable
            key={`${file?._id || ''}-${activeSheet?.name || ''}`}
            data={tableData}
            colHeaders={headers}
            rowHeaders={true}
            style={isFullscreen ? { width: '100vw', height: '100vh' } : { width: '100%', height: '100%' }}
            autoColumnSize={true}
            colWidths={Array.isArray(headers) ? Array(headers.length).fill(200) : undefined}
            stretchH="all"
            licenseKey="non-commercial-and-evaluation"
            contextMenu={true}
            filters={true}
            dropdownMenu={true}
          />
        </div>
      );
    }
    if (file?.fileType === 'csv') {
      if (loading) return <div className="spreadsheet-loading"><FiLoader className="spinner-icon" /> Loading CSV preview...</div>;
      if (previewError) return <div className="spreadsheet-error">{previewError}</div>;
      if (previewData?.headers) {
        return (
          <div className="spreadsheet-preview-container spreadsheet-preview-scrollable">
            <table className="spreadsheet-table">
              <thead>
                <tr>{previewData.headers.map((header, idx) => <th key={idx}>{header}</th>)}</tr>
              </thead>
              <tbody>
                {previewData.rows?.length ? (
                  previewData.rows.map((row, rIdx) => (
                    <tr key={rIdx}>{row.map((cell, cIdx) => <td key={cIdx}>{cell}</td>)}</tr>
                  ))
                ) : (
                  <tr><td colSpan={previewData.headers.length}>No data found.</td></tr>
                )}
              </tbody>
            </table>
          </div>
        );
      }
      return null;
    }
    if (file?.fileType === 'docx' || file?.fileType === 'doc') {
      if (loading) return <div className="docx-loading"><FiLoader className="spinner-icon" /> Loading document preview...</div>;
      if (previewError) return <div className="docx-error">{previewError}</div>;
      if (previewData) return <div className="docx-preview" dangerouslySetInnerHTML={{ __html: previewData }} />;
      return null;
    }
    return null;
  };

  // Helper to render docx previews
  const renderDocx = () => {
    if (loading) return <div className="docx-loading"><FiLoader className="spinner-icon" /> Loading document preview...</div>;
    if (previewError) return <div className="docx-error">{previewError}</div>;
    if (previewData) return <div className="docx-preview" dangerouslySetInnerHTML={{ __html: previewData }} />;
    return null;
  };

  // Render logic
  return (
    <div className="app-root">
      <Header />
      <main className="main-content file-viewer-main-redesign">
        <div className="file-viewer-header file-viewer-page">
          <div className="file-viewer-header-left">
            {/* Removed back button and file name */}
          </div>
        </div>
        
        {/* Centered Search Bar */}
        <div className="file-viewer-search-container">
          <div className="file-viewer-search-wrapper">
            <FiSearch className="file-viewer-search-icon" />
            <input
              className="file-viewer-search-input"
              type="text"
              placeholder="Search files to view..."
              value={searchTerm}
              onChange={handleSearchChange}
            />
            {searchTerm && (
              <button className="file-viewer-clear-search" onClick={clearSearch}>
                <FiX />
              </button>
            )}
          </div>
        </div>

        {/* Horizontal scroll box for files */}
        <div className="file-viewer-horizontal-scroll file-viewer-horizontal-scroll-large custom-scroll-hide">
          <div className="file-viewer-scroll-title">
            {isSearching ? `Search Results (${scrollBoxFiles.length})` : 'Recently Viewed Files'}
          </div>
          <button className="scroll-arrow left" onClick={() => scrollByAmount(-220)}><FiChevronLeft /></button>
          <div className="file-scroll-inner" ref={scrollRef}>
            {scrollBoxFiles.length > 0 ? (
              scrollBoxFiles.map(f => (
                <FileCard
                  key={f._id}
                  file={f}
                  onView={id => setSelectedFileId(id)}
                  onDownload={handleDownload}
                  selected={f._id === selectedFileId}
                  className="file-viewer-scroll-card"
                />
              ))
            ) : (
              <div className="empty-state">
                {isSearching ? 'No files found matching your search.' : 'No recently viewed files.'}
              </div>
            )}
          </div>
          <button className="scroll-arrow right" onClick={() => scrollByAmount(220)}><FiChevronRight /></button>
        </div>

        {/* Centered preview with overlayed actions */}
        <div className="file-viewer-preview-center file-viewer-preview-center-large">
          <div className={isFullscreen ? 'file-preview fullscreen' : 'file-preview file-preview-large'} ref={previewRef}>
            {/* Overlayed file name and actions */}
            {file && (
              <div className="file-viewer-preview-overlay">
                <div className="file-viewer-preview-title">
                  {file?.originalName || file?.filename || file?.name || 'Untitled'}
                </div>
                <div className="file-viewer-preview-actions">
                  <button className="download-btn small" onClick={() => handleDownload(file?._id, file?.originalName || file?.filename || file?.name)} title="Download File">
                    <FiDownload />
                  </button>
                  <button className="fullscreen-btn with-label" onClick={handleToggleFullscreen} title={isFullscreen ? 'Exit Fullscreen' : 'View in Full-Screen'}>
                    {isFullscreen ? <FiMinimize /> : <FiMaximize />}
                  </button>
                </div>
              </div>
            )}
            {/* Preview content */}
            {loading ? (
              <div className="loading-container"><FiLoader className="spinner-icon" /><p>Loading file...</p></div>
            ) : error ? (
              <div className="empty-state file-preview-error">{error}</div>
            ) : file ? (
              <>
                {file?.fileType === 'pdf' && file?.url && (
                  isMobileDevice() ? (
                    <div className="pdf-mobile-message">
                      <p>PDF preview is not supported on mobile.<br/>Tap below to open the PDF in your browser or download it.</p>
                      <a
                        href={file.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="pdf-mobile-open-btn"
                      >
                        Open PDF
                      </a>
                    </div>
                  ) : (
                    <iframe src={file.url} title="PDF Preview" className="pdf-preview-frame" frameBorder="0" />
                  )
                )}
                {(file?.fileType === 'csv' || file?.fileType === 'excel' || file?.fileType === 'xlsx') && (
                  <div
                    className={`spreadsheet-preview-wrapper${isFullscreen ? ' fullscreen' : ''}`}
                  >
                    {renderSpreadsheet()}
                  </div>
                )}
                {(file?.fileType === 'docx' || file?.fileType === 'doc') && (
                  <div className={`docx-preview-wrapper${isFullscreen ? ' fullscreen' : ''}`} style={{display: 'flex', flexDirection: 'column', height: '100%'}}>
                    <div className="docx-preview" style={{flex: 1, width: '100%', overflow: 'auto'}} dangerouslySetInnerHTML={{ __html: previewData }} />
                  </div>
                )}
                {!['pdf', 'csv', 'excel', 'xlsx', 'docx', 'doc'].includes(file?.fileType) && (
                  <div className="unsupported-preview">
                    <FiFile className="unsupported-file-icon" />
                    <p>Preview not available for this file type.</p>
                  </div>
                )}
              </>
            ) : (
              <div className="file-preview-empty-state">
                Your file will open here.
              </div>
            )}
          </div>
        </div>

        {/* Metadata card below preview */}
        {file && (
          <div className="file-viewer-metadata-card">
            <div className="details-section">
              <h3>File Information</h3>
              <ul>
                <li><FiFolder /><span>Category:</span><strong>{file.category || 'Uncategorized'}</strong></li>
                <li><FiFolder /><span>SubCategory:</span><strong>{file.subCategory || 'N/A'}</strong></li>
                <li><FiCalendar /><span>Year:</span><strong>{file.year || 'N/A'}</strong></li>
                <li><FiInfo /><span>Size:</span><strong>{file.size ? `${(file.size / 1024).toFixed(2)} KB` : 'Unknown'}</strong></li>
              </ul>
            </div>
            {file.description && <div className="description-section"><h3>Description</h3><p>{file.description}</p></div>}
            <div className="actions-section">
              <button className="edit-button" title="Edit file metadata" onClick={handleEditClick}><FiEdit /> Edit File Metadata</button>
              <button className="delete-button" title="Delete this file permanently" onClick={handleDeleteClick} disabled={deleting}><FiTrash2 /> Delete File</button>
            </div>
          </div>
        )}
        <ConfirmModal
          open={showConfirm}
          title="Delete File?"
          message={`Are you sure you want to delete \"${file?.originalName || file?.filename || file?.name}\"? This action cannot be undone.`}
          onConfirm={confirmDelete}
          onCancel={() => setShowConfirm(false)}
          loading={deleting}
          confirmText="Delete"
          cancelText="Cancel"
        />
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
      <Footer />
    </div>
  );
};

export default FileViewer;
