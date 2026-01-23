import React from 'react';

export default function ConfirmModal({ open, title = 'Are you sure?', message = '', onConfirm, onCancel, confirmText = 'Delete', cancelText = 'Cancel', loading = false }) {
  if (!open) return null;
  return (
    <div
      style={{
        position: 'fixed',
        top: 24,
        right: 24,
        zIndex: 4000,
        minWidth: 320,
        maxWidth: 380,
        background: '#14213d',
        color: '#fff',
        borderRadius: 10,
        boxShadow: '0 4px 24px rgba(2, 6, 16, 0.18)',
        padding: '1.1rem 1.3rem 1rem 1.3rem',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'flex-start',
        animation: 'modal-fade-in 0.35s cubic-bezier(0.4, 0.2, 0.2, 1)',
      }}
    >
      <div style={{ fontWeight: 700, fontSize: '1.08rem', color: '#f7bf47', marginBottom: 6 }}>{title}</div>
      {message && <div style={{ marginBottom: 14, fontSize: '1.01rem', color: '#fff' }}>{message}</div>}
      <div style={{ display: 'flex', gap: 10, width: '100%', justifyContent: 'flex-end' }}>
        <button
          type="button"
          onClick={onCancel}
          disabled={loading}
          style={{
            background: '#232b3e',
            color: '#fff',
            border: 'none',
            borderRadius: 6,
            padding: '7px 18px',
            fontWeight: 600,
            fontSize: '1rem',
            cursor: 'pointer',
            opacity: loading ? 0.7 : 1,
            transition: 'background 0.2s',
          }}
        >
          {cancelText}
        </button>
        <button
          type="button"
          onClick={onConfirm}
          disabled={loading}
          style={{
            background: '#dc2626',
            color: '#fff',
            border: 'none',
            borderRadius: 6,
            padding: '7px 18px',
            fontWeight: 600,
            fontSize: '1rem',
            cursor: 'pointer',
            opacity: loading ? 0.7 : 1,
            transition: 'background 0.2s',
          }}
        >
          {loading ? 'Deleting...' : confirmText}
        </button>
      </div>
    </div>
  );
} 