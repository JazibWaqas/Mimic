import React from 'react';
import { FiEye, FiDownload } from 'react-icons/fi';

export default function FileCard({ file, onView, onDownload, selected, className }) {
  return (
    <div
      className={`file-card${selected ? ' selected' : ''}${className ? ' ' + className : ''}`}
      onClick={onView ? () => onView(file._id) : undefined}
      style={{ cursor: onView ? 'pointer' : undefined }}
    >
      <div className="file-info">
        <h3 className="file-name">
          <span className="file-name-inner">
            <span className="file-name-single">{file.originalName || file.filename || file.name || 'Untitled'}</span>
            <span className="file-name-duplicate">{file.originalName || file.filename || file.name || 'Untitled'}</span>
          </span>
        </h3>
        <p>Category: {file.category || 'Uncategorized'}</p>
        <p>Year: {file.year || 'N/A'}</p>
      </div>
      <div className="file-actions">
        <button
          className="file-view-btn"
          onClick={e => { e.stopPropagation(); onView && onView(file._id); }}
        >
          <FiEye /> View 
        </button>
        <button
          className="file-download-btn"
          onClick={e => { e.stopPropagation(); onDownload && onDownload(file._id, file.originalName || file.filename || file.name); }}
        >
          <FiDownload /> Download 
        </button>
      </div>
    </div>
  );
} 