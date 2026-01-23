import React, { useState, useEffect, lazy, Suspense } from 'react';
import { FiLoader } from 'react-icons/fi';

const MammothViewer = ({ fileId }) => {
    const [html, setHtml] = useState('');
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        const renderDocx = async () => {
            setLoading(true);
            setError('');
            try {
                // Dynamically import mammoth
                const mammoth = await import('mammoth/mammoth.browser.js');

                const response = await fetch(`/api/files/${fileId}/view`);
                if (!response.ok) {
                    throw new Error('Failed to fetch document for preview.');
                }
                const arrayBuffer = await response.arrayBuffer();
                const result = await mammoth.convertToHtml({ arrayBuffer });
                setHtml(result.value);
            } catch (err) {
                console.error("Error rendering docx:", err);
                setError('Could not display the document.');
            } finally {
                setLoading(false);
            }
        };

        if (fileId) {
            renderDocx();
        }
    }, [fileId]);

    if (loading) {
        return (
            <div className="viewer-loading">
                <FiLoader className="spinner-icon" />
                <p>Preparing document preview...</p>
            </div>
        );
    }

    if (error) {
        return <div className="viewer-error">{error}</div>;
    }

    return <div className="docx-preview" dangerouslySetInnerHTML={{ __html: html }} />;
};

export default MammothViewer; 