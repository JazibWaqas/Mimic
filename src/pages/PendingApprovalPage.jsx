import React from 'react';
import { FiClock, FiMail } from 'react-icons/fi';
import { signOutUser } from '../services/firebase';

const PendingApprovalPage = () => (
  <div style={{
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    minHeight: '100vh',
    background: 'var(--color-bg, #F9F9FF)',
    color: 'var(--color-text, #1A1A1A)',
    padding: '2rem'
  }}>
    <FiClock style={{ fontSize: '4rem', color: 'var(--color-primary, #00897B)', marginBottom: '1.5rem' }} />
    <h1 style={{ fontSize: '2.5rem', marginBottom: '1rem' }}>Approval Pending</h1>
    <p style={{ fontSize: '1.2rem', textAlign: 'center', maxWidth: '500px' }}>
      Your account has been created but is waiting for an administrator to grant you access.
    </p>
    <p style={{ marginTop: '0.5rem', fontSize: '1.2rem' }}>
      An email has been sent to the site administrator.
    </p>
    <button 
        onClick={signOutUser}
        style={{
            marginTop: '2rem',
            padding: '0.7em 1.5em',
            background: 'var(--color-primary, #00897B)',
            color: '#fff',
            border: 'none',
            borderRadius: '6px',
            fontSize: '1rem',
            cursor: 'pointer'
        }}
    >
        Log Out & Return to Site
    </button>
    <div style={{ marginTop: '2rem', display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#666' }}>
      <FiMail />
      <span>auraxkhidmat@gmail.com</span>
    </div>
  </div>
);

export default PendingApprovalPage; 