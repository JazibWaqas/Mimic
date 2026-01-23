import React, { useState, useEffect } from 'react';
  import Header from '../components/Header';
  import { FiUploadCloud, FiFile, FiEye, FiDownload } from 'react-icons/fi';
  import { useNavigate } from 'react-router-dom';
  import { initializeGoogleDrive, showGoogleDrivePicker, downloadFile } from '../services/googleDriveService';
  import '../styles/UploadFile.css';
  import { useAuth } from '../App';
  import { useIsMobileScreen } from '../services/deviceUtils';
  import { FaExclamationTriangle } from 'react-icons/fa';
  import { ToastContainer, toast } from 'react-toastify';
  import 'react-toastify/dist/ReactToastify.css';
  
  const defaultCategories = [
      {
          name: 'Financial Statements',
          description: 'Financial reports and statements',
          subCategories: ['Financial Reports', 'Monthly Accounts', 'Trial Balance', 'Other'],
          isDefault: true
      },
      {
          name: 'Income & Donations',
          description: 'Income and donation records',
          subCategories: ['Donations', 'Fee Records', 'Other Income', 'Other'],
          isDefault: true
      },
      {
          name: 'Expenses',
          description: 'Expense records and bills',
          subCategories: ['Operating Expenses', 'Utility Bills', 'Salary Records', 'Other'],
          isDefault: true
      },
      {
          name: 'Bank & Cash',
          description: 'Bank and cash related documents',
          subCategories: ['Bank Statements', 'Cash Books', 'Bank Reconciliations', 'Other'],
          isDefault: true
      },
      {
          name: 'Tax & Compliance',
          description: 'Tax and compliance related documents',
          subCategories: ['Tax Returns', 'Tax Exemptions', 'Regulatory Filings', 'Other'],
          isDefault: true
      },
      {
          name: 'Audit Reports',
          description: 'Internal and external audit reports',
          subCategories: ['External Audit', 'Internal Audit', 'Other'],
          isDefault: true
      },
      {
          name: 'Budgets',
          description: 'Budget planning and tracking documents',
          subCategories: ['Annual Budgets', 'Other'],
          isDefault: true
      },
      {
          name: 'Organizational Documents',
          description: 'Organization related documents',
          subCategories: ['Board Documents', 'Certificates', 'Constitution', 'General', 'Policies', 'Registration Documents', 'Staff Policies', 'Other'],
          isDefault: true
      },
      {
          name: 'Other',
          description: 'Miscellaneous documents',
          subCategories: ['Other'],
          isDefault: true
      }
  ];
  
  export default function UploadFilePage() {
    const [files, setFiles] = useState([]);
    const [description, setDescription] = useState('');
    const [category, setCategory] = useState('');
    const [year, setYear] = useState('');
    const [recentUploads, setRecentUploads] = useState([]);
    const [uploading, setUploading] = useState(false);
    const [error, setError] = useState(null);
    const [isGoogleDriveInitialized, setIsGoogleDriveInitialized] = useState(false);
    const [subCategory, setSubCategory] = useState('');
    const [requiresAuth, setRequiresAuth] = useState(false);
    const navigate = useNavigate();
    const { user } = useAuth();
    const isMobile = useIsMobileScreen();
  
    // Allowed file extensions and MIME types
    const allowedExtensions = [
      '.pdf', '.docx', '.doc', '.csv', '.xls', '.xlsx', '.xlsm', '.xlsb'
    ];
    const allowedMimeTypes = [
      'application/pdf',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document', // .docx
      'application/msword', // .doc
      'text/csv',
      'application/csv',
      'text/x-csv',
      'application/x-csv',
      'text/comma-separated-values',
      'text/x-comma-separated-values',
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', // .xlsx
      'application/vnd.ms-excel', // .xls
      'application/vnd.ms-excel.sheet.macroEnabled.12', // .xlsm
      'application/vnd.ms-excel.sheet.binary.macroEnabled.12' // .xlsb
    ];
  
    useEffect(() => {
      const fetchFiles = async () => {
        try {
          const res = await fetch('/api/files');
          if (!res.ok) throw new Error('Failed to fetch files');
          const data = await res.json();
          const recentFiles = data.sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt)).slice(0, 4);
          setRecentUploads(recentFiles);
        } catch (error) {
          setRecentUploads([]);
        }
      };
      fetchFiles();
    }, []);
  
    useEffect(() => {
      initializeGoogleDrive().then(success => {
        setIsGoogleDriveInitialized(!!success);
      });
    }, []);
  
    const handleFileChange = (e) => {
      const selectedFiles = Array.from(e.target.files);
      const validFiles = selectedFiles.filter(selectedFile => {
        const ext = selectedFile.name.substring(selectedFile.name.lastIndexOf('.')).toLowerCase();
        return allowedExtensions.includes(ext) && allowedMimeTypes.includes(selectedFile.type);
      });
      if (validFiles.length !== selectedFiles.length) {
        setError('Some files are invalid. Only PDF, DOCX, DOC, CSV, XLS, XLSX, XLSM, and XLSB files are allowed.');
      } else {
        setError(null);
      }
      setFiles(validFiles);
    };
  
    const handleDragOver = (e) => e.preventDefault();
    const handleDrop = (e) => {
      e.preventDefault();
      const droppedFiles = Array.from(e.dataTransfer.files);
      const validFiles = droppedFiles.filter(droppedFile => {
        const ext = droppedFile.name.substring(droppedFile.name.lastIndexOf('.')).toLowerCase();
        return allowedExtensions.includes(ext) && allowedMimeTypes.includes(droppedFile.type);
      });
      if (validFiles.length !== droppedFiles.length) {
        setError('Some files are invalid. Only PDF, DOCX, DOC, CSV, XLS, XLSX, XLSM, and XLSB files are allowed.');
      } else {
        setError(null);
      }
      setFiles(validFiles);
    };
  
    const handleGoogleDriveFileSelect = async () => {
      try {
        await showGoogleDrivePicker(async (data) => {
          if (data.action === window.google.picker.Action.PICKED) {
            const pickedFiles = data.docs.filter(pickedFile => pickedFile.id && pickedFile.name);
            if (pickedFiles.length > 0) {
              try {
                const files = await Promise.all(pickedFiles.map(async pickedFile => {
                  const blob = await downloadFile(pickedFile.id);
                  let mimeType = pickedFile.mimeType || blob.type;
                  if (!mimeType || mimeType === 'application/octet-stream') {
                    if (pickedFile.name.endsWith('.pdf')) mimeType = 'application/pdf';
                    else if (pickedFile.name.endsWith('.xlsx')) mimeType = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet';
                    else if (pickedFile.name.endsWith('.xls')) mimeType = 'application/vnd.ms-excel';
                  }
                  return new File([blob], pickedFile.name, { type: mimeType });
                }));
                setFiles(files);
              } catch (err) {
                setError('Failed to download files from Google Drive.');
              }
            }
          }
        });
      } catch (error) {
        setError('Failed to access Google Drive files.');
      }
    };
  
    const handleUpload = async (e) => {
      e.preventDefault();
      if (!files.length) {
        setError('Please select at least one file');
        return;
      }
      if (!category || !year) {
        setError('Please fill in all required fields');
        return;
      }
      try {
        setUploading(true);
        setError(null);
        const formData = new FormData();
        files.forEach(file => formData.append('files', file));
        formData.append('description', description);
        formData.append('category', category);
        formData.append('subCategory', subCategory);
        formData.append('year', year);
        formData.append('requiresAuth', requiresAuth ? 'true' : 'false');
        const res = await fetch('/api/files/upload', {
          method: 'POST',
          body: formData
        });
        if (!res.ok) throw new Error('Upload failed');
        const data = await res.json();
        setFiles([]);
        setDescription('');
        setCategory('');
        setSubCategory('');
        setYear('');
        setRequiresAuth(false);
        navigate('/file-index');
      } catch (error) {
        setError(error.message);
      } finally {
        setUploading(false);
      }
    };
  
    const handleViewFile = async (fileId) => {
      // Find the file object from recentUploads
      const fileObj = recentUploads.find(f => f._id === fileId);
      let headers = {};
      if (fileObj && fileObj.requiresAuth) {
        if (user && user.getIdToken) {
          const token = await user.getIdToken();
          headers['Authorization'] = `Bearer ${token}`;
        }
      }
      // Pass token via query or localStorage for file-viewer page to use
      if (headers['Authorization']) {
        localStorage.setItem('fileAuthToken', headers['Authorization']);
      } else {
        localStorage.removeItem('fileAuthToken');
      }
      navigate(`/file-viewer/${fileId}`);
    };
  
    const handleDownload = async (fileId, fileName) => {
      try {
        // Find the file object from recentUploads
        const fileObj = recentUploads.find(f => f._id === fileId);
        let headers = {};
        // If file requires authentication and user is logged in, send token
        if (fileObj && fileObj.requiresAuth) {
          if (user && user.getIdToken) {
            const token = await user.getIdToken();
            headers['Authorization'] = `Bearer ${token}`;
          }
        }
        const response = await fetch(`/api/files/${fileId}`, { headers });
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
    };
  
    const getSubCategories = () => {
      const cat = defaultCategories.find(c => c.name === category);
      return cat ? cat.subCategories : [];
    };
  
    if (isMobile) {
      return (
        <div style={{
          minHeight: '100vh',
          width: '100vw',
          background: 'linear-gradient(90deg, #85d8ce 0%, #085078,#2f3132 100%)',
          margin: 0,
          padding: 0,
          display: 'flex',
          flexDirection: 'column',
        }}>
          <Header />
          <div style={{
            flex: 1,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#d32f2f',
            fontWeight: 'bold',
            fontSize: '1.35rem',
            textAlign: 'center',
            gap: '1.2rem',
            width: '100%',
          }}>
            <FaExclamationTriangle size={48} style={{ color: '#d32f2f' }} />
            <span>For full access, please log in from a computer as a registered user.</span>
          </div>
        </div>
      );
    }
  
    return (
      <div className="app-root">
        <Header />
        <main className="main-content" style={{ padding: 0 }}>
          <div style={{ display: 'flex', minHeight: 'calc(100vh - 64px)' }}>
            <div className="upload-content-row" style={{ flex: 1, padding: '32px 40px', overflowX: 'auto' }}>
              {!user && (
                <div className="upload-auth-error-card">
                  <FiUploadCloud className="upload-auth-error-icon" />
                  <h2 className="upload-auth-error-title">Sign In Required</h2>
                  <p className="upload-auth-error-message">
                    You must be signed in to upload files.<br />Please log in to access the upload feature.
                  </p>
                  <button
                    className="header-login-btn upload-auth-error-btn"
                    onClick={() => window.scrollTo({top: 0, behavior: 'smooth'}) || document.querySelector('.header-login-btn')?.click()}
                  >
                    Log In
                  </button>
                </div>
              )}
              {user && (
                <div className="upload-card large">
                  <h2 className="upload-title">Upload New Accounting File</h2>
                  <p className="upload-subtitle">
                    Select file, category, and year for accurate organization within your accounting hub.
                  </p>
                  <div
                    className="drop-zone blue"
                    onDragOver={handleDragOver}
                    onDrop={handleDrop}
                    onClick={() => document.getElementById('fileInput').click()}
                  >
                    <input
                      type="file"
                      id="fileInput"
                      style={{ display: 'none' }}
                      onChange={handleFileChange}
                      accept=".pdf,.docx,.doc,.csv,.xls,.xlsx,.xlsm,.xlsb"
                      multiple
                    />
                    <FiUploadCloud className="upload-icon" />
                    <p>
                      <strong>Drag & drop your files here</strong> or click to browse
                    </p>
                    <p className="supported-formats">
                      Supported formats: PDF, DOCX, DOC, XLSX, XLS, XLSM, XLSB, CSV. Max file size: 10MB.
                    </p>
                    {files.length > 0 && (
                      <ul>
                        {files.map((file, idx) => (
                          <li key={idx}>{file.name}</li>
                        ))}
                      </ul>
                    )}
                  </div>
                  <div className="upload-options-row">
                    <button
                      className="google-drive-button"
                      onClick={handleGoogleDriveFileSelect}
                      disabled={!isGoogleDriveInitialized}
                    >
                      <img
                        src="https://www.google.com/drive/static/images/drive/logo-drive.png"
                        alt="Google Drive"
                        className="google-drive-icon"
                      />
                      <span>Import from Google Drive</span>
                    </button>
                  </div>
                  <form className="file-details-form" onSubmit={handleUpload}>
                    <label htmlFor="description">Description (Optional)</label>
                    <textarea
                      id="description"
                      placeholder="Provide a brief summary or notes about these files..."
                      value={description}
                      onChange={(e) => setDescription(e.target.value)}
                    ></textarea>
                    <div className="dropdown-row">
                      <div className="dropdown-wrapper">
                        <label htmlFor="category">Category</label>
                        <select
                          id="category"
                          value={category}
                          onChange={(e) => {
                            setCategory(e.target.value);
                            setSubCategory('');
                          }}
                          required
                        >
                          <option value="">Select a category</option>
                          {defaultCategories.map((cat, idx) => (
                            <option key={idx} value={cat.name}>{cat.name}</option>
                          ))}
                        </select>
                      </div>
                      <div className="dropdown-wrapper">
                        <label htmlFor="year">Year</label>
                        <input
                          type="number"
                          id="year"
                          placeholder="e.g., 2024"
                          value={year}
                          onChange={e => {
                            const val = e.target.value;
                            if (/^\d*$/.test(val)) setYear(val);
                          }}
                          min="1900"
                          max={new Date().getFullYear()}
                          required
                        />
                      </div>
                    </div>
                    <div className="dropdown-wrapper">
                      <label htmlFor="subCategory">Sub Category</label>
                      <select
                        id="subCategory"
                        value={subCategory}
                        onChange={e => setSubCategory(e.target.value)}
                        required
                        disabled={!category}
                      >
                        <option value="">Select a sub category</option>
                        {getSubCategories().map((sub, idx) => (
                          <option key={idx} value={sub}>{sub}</option>
                        ))}
                      </select>
                    </div>
                    <div className="dropdown-wrapper">
                      <label htmlFor="requiresAuth" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontWeight: 500 }}>
                        <input
                          type="checkbox"
                          id="requiresAuth"
                          checked={requiresAuth}
                          onChange={e => setRequiresAuth(e.target.checked)}
                          style={{ marginRight: '0.2rem' }}
                        />
                        Requires Authentication (Private File)
                      </label>
                      <span style={{ fontSize: '0.95rem', color: '#888', marginLeft: '1.7rem' }}>
                        Only logged-in users can view this file if checked.
                      </span>
                    </div>
                    <div className="form-actions">
                      <button
                        className="cancel-button"
                        type="button"
                        onClick={() => {
                          setFiles([]);
                          setDescription('');
                          setCategory('');
                          setYear('');
                          setSubCategory('');
                          setRequiresAuth(false);
                        }}
                      >
                        Cancel
                      </button>
                      <button className="upload-file-button" type="submit" disabled={uploading}>
                        {uploading ? 'Uploading...' : 'Upload Files'}
                      </button>
                    </div>
                  </form>
                  {error && <div className="error-message" style={{marginTop: '16px'}}>{error}</div>}
                </div>
              )}
              <div className="recent-uploads-card large" style={{ minHeight: 320, padding: '1.5rem 1.2rem' }}>
                <h3>Recent Uploads</h3>
                <div className="recent-uploads-list" style={{ overflowX: 'hidden' }}>
                  {recentUploads.length > 0 ? (
                    recentUploads.map((file) => (
                      <div key={file._id} className="recent-upload-item">
                        <div className="file-icon-background">
                          <FiFile className="file-icon" />
                        </div>
                        <div className="file-info">
                          <h3>{file.originalName || file.filename || file.name || 'Untitled'}</h3>
                          <p>Category: {file.category || 'Uncategorized'}</p>
                        </div>
                        <div className="file-actions">
                          <button
                            className="action-button"
                            title="View"
                            onClick={() => handleViewFile(file._id)}
                          >
                            <FiEye />
                          </button>
                          <button
                            className="action-button"
                            title="Download"
                            onClick={() => handleDownload(file._id, file.originalName || file.filename || file.name)}
                          >
                            <FiDownload />
                          </button>
                        </div>
                      </div>
                    ))
                  ) : (
                    <p className="no-files">No recent files uploaded yet.</p>
                  )}
                </div>
              </div>
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