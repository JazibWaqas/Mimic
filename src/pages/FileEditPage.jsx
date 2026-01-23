import React, { useState, useEffect } from 'react';
import Header from '../components/Header.jsx';
import { FiSave, FiArrowLeft, FiFile, FiLoader, FiTrash2, FiEdit } from 'react-icons/fi';
import { useParams, useNavigate } from 'react-router-dom';
import '../styles/FileEdit.css';
import ShinyText from '../components/ShinyText';
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import ConfirmModal from '../components/ConfirmModal';

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

export default function FileEditPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  
  // Form state
  const [fileName, setFileName] = useState('');
  const [description, setDescription] = useState('');
  const [category, setCategory] = useState('');
  const [subCategory, setSubCategory] = useState('');
  const [year, setYear] = useState('');
  const [showConfirm, setShowConfirm] = useState(false);
  const [deleting, setDeleting] = useState(false);

  useEffect(() => {
    const fetchFile = async () => {
      try {
        setLoading(true);
        setError(null);
        
        const response = await fetch(`/api/files/${id}/details`);
        if (!response.ok) {
          throw new Error(response.status === 404 ? 'File not found' : 'Failed to fetch file details');
        }
        
        const fileData = await response.json();
        setFile(fileData);
        
        // Populate form with existing data
        setFileName(fileData.originalName || fileData.filename || fileData.name || '');
        setDescription(fileData.description || '');
        setCategory(fileData.category || '');
        setSubCategory(fileData.subCategory || '');
        setYear(fileData.year ? fileData.year.toString() : '');
        
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    if (id) {
      fetchFile();
    }
  }, [id]);

  const getSubCategories = () => {
    const cat = defaultCategories.find(c => c.name === category);
    return cat ? cat.subCategories : [];
  };

  const handleSave = async (e) => {
    e.preventDefault();
    
    if (!fileName || !category || !year) {
      setError('Please fill in all required fields');
      return;
    }

    try {
      setSaving(true);
      setError(null);

      const response = await fetch(`/api/files/${id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          fileName,
          description,
          category,
          subCategory,
          year: parseInt(year)
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || 'Failed to update file');
      }

      // Navigate back to file viewer
      navigate(`/file-viewer/${id}`);
      
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  };

  const handleCancel = () => {
    navigate(`/file-viewer/${id}`);
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
      setError(error.message);
      setDeleting(false);
    }
  };

  if (loading) {
    return (
      <div className="app-root">
        <Header />
        <main className="main-content">
          <div className="loading-container">
            <FiLoader className="spinner-icon" />
            <p>Loading file details...</p>
          </div>
        </main>
      </div>
    );
  }

  if (error) {
    return (
      <div className="app-root">
        <Header />
        <main className="main-content">
          <div className="error-container">
            <h2>Error Loading File</h2>
            <p>{error}</p>
            <button onClick={() => navigate('/file-index')} className="retry-button">
              Back to Files
            </button>
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className="app-root">
      <Header />
      <main className="main-content file-edit-main-content">
        <div className="edit-card large">
          <div className="edit-header">
            <div className="edit-header-row">
              <button className="back-button" onClick={handleCancel}>
                <FiArrowLeft /> Back
              </button>
              <h2 className="edit-title">
                <ShinyText text="Edit File Metadata" />
              </h2>
            </div>
            
          </div>
          <div className="edit-content-layout">
            {/* Left Column - File Information Display */}
            <div className="file-info-column">
              <div className="file-info-display">
                <div className="file-icon-background">
                  <FiFile className="file-icon" />
                </div>
                <div className="file-details">
                  <h3>{file.originalName || file.filename || file.name || 'Untitled'}</h3>
                  <p><strong>Size:</strong> {file.size ? `${(file.size / 1024).toFixed(2)} KB` : 'Unknown'}</p>
                  <p><strong>Category:</strong> {file.category || 'Anonymous'}</p>
                  <p><strong>File Type:</strong> {file.fileType || 'Unknown'}</p>
                </div>
              </div>
              <div className="actions-section">
                
                <button className="delete-button" title="Delete this file permanently" onClick={handleDelete} disabled={deleting}>
                  <FiTrash2 /> Delete File
                </button>
              </div>
            </div>
            {/* Right Column - Form Fields */}
            <div className="form-column">
              <form className="file-details-form" onSubmit={handleSave}>
                <label htmlFor="fileName">File Name</label>
                <input
                  type="text"
                  id="fileName"
                  placeholder="e.g., Income Statement"
                  value={fileName}
                  onChange={(e) => setFileName(e.target.value)}
                  required
                />
                <label htmlFor="description">Description (Optional)</label>
                <textarea
                  id="description"
                  placeholder="Provide a brief summary or notes about this file..."
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
                <div className="form-actions">
                  <button
                    className="cancel-button"
                    type="button"
                    onClick={handleCancel}
                  >
                    Cancel
                  </button>
                  <button className="save-button" type="submit" disabled={saving}>
                    <FiSave />
                    {saving ? 'Saving...' : 'Save Changes'}
                  </button>
                </div>
              </form>
            </div>
          </div>
          {error && <div className="error-message">{error}</div>}
        </div>
        <ConfirmModal
          open={showConfirm}
          title="Delete File?"
          message={`Are you sure you want to delete "${file?.originalName || file?.filename || file?.name}"? This action cannot be undone.`}
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
    </div>
  );
} 