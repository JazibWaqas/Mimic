import React, { useState, useEffect, lazy, Suspense } from 'react';
import { FiLoader } from 'react-icons/fi';

// Lazy load HotTable
const HotTable = lazy(() =>
    import('@handsontable/react').then(module => ({ default: module.HotTable }))
);

const SpreadsheetViewer = ({ fileId, fileType }) => {
    const [sheets, setSheets] = useState([]);
    const [activeSheet, setActiveSheet] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        const renderSpreadsheet = async () => {
            setLoading(true);
            setError('');
            try {
                // Dynamically import libraries
                const XLSX = await import('xlsx');
                await import('handsontable/dist/handsontable.full.min.css');

                const response = await fetch(`/api/files/${fileId}/view`);
                if (!response.ok) {
                    throw new Error('Failed to fetch spreadsheet for preview.');
                }
                const arrayBuffer = await response.arrayBuffer();
                const workbook = XLSX.read(arrayBuffer, { type: 'array' });

                const sheetData = workbook.SheetNames.map((sheetName) => {
                    const sheet = workbook.Sheets[sheetName];
                    const data = XLSX.utils.sheet_to_json(sheet, { header: 1, defval: '' });
                    return { name: sheetName, data };
                });

                if (sheetData.length === 0 || sheetData[0].data.length === 0) {
                    setError('No data found in this file.');
                } else {
                    setSheets(sheetData);
                    setActiveSheet(sheetData[0]);
                }

            } catch (err) {
                console.error("Error rendering spreadsheet:", err);
                setError('Could not display the spreadsheet.');
            } finally {
                setLoading(false);
            }
        };

        const renderCsv = async () => {
            setLoading(true);
            setError('');
             try {
                const previewResponse = await fetch(`/api/files/${fileId}/preview`);
                if (!previewResponse.ok) {
                    throw new Error('Failed to load CSV preview data.');
                }
                const previewData = await previewResponse.json();
                 if (!previewData.headers || previewData.headers.length === 0) {
                    setError('No data found in this file.');
                    return;
                }
                const data = [previewData.headers, ...previewData.rows];
                const csvSheet = [{ name: 'CSV Data', data }];
                setSheets(csvSheet);
                setActiveSheet(csvSheet[0]);

            } catch (err) {
                 console.error("Error rendering csv:", err);
                 setError('Could not display the CSV file.');
            } finally {
                setLoading(false);
            }
        };

        if (fileId && fileType === 'csv') {
            renderCsv();
        } else if (fileId) {
            renderSpreadsheet();
        }

    }, [fileId, fileType]);


    if (loading) {
        return (
            <div className="viewer-loading">
                <FiLoader className="spinner-icon" />
                <p>Preparing spreadsheet preview...</p>
            </div>
        );
    }

    if (error) {
        return <div className="viewer-error">{error}</div>;
    }
    
    if (!activeSheet || !activeSheet.data || activeSheet.data.length === 0) {
        return <div className="viewer-error">No data to display in this sheet.</div>;
    }

    const headers = activeSheet.data[0];
    const tableData = activeSheet.data.slice(1);

    return (
        <div className="spreadsheet-preview-container handsontable-container">
            {sheets.length > 1 && (
                <div className="sheet-select-row">
                    <label htmlFor="sheetSelect" className="sheet-select-label">Sheet:</label>
                    <select
                        id="sheetSelect"
                        value={activeSheet.name}
                        onChange={(e) =>
                            setActiveSheet(sheets.find((s) => s.name === e.target.value))
                        }
                        className="sheet-select-dropdown"
                    >
                        {sheets.map((sheet) => (
                            <option key={sheet.name} value={sheet.name}>{sheet.name}</option>
                        ))}
                    </select>
                </div>
            )}
            <Suspense fallback={<div className="viewer-loading"><FiLoader className="spinner-icon" /><p>Loading Table...</p></div>}>
                 <HotTable
                    data={tableData}
                    colHeaders={headers}
                    rowHeaders={true}
                    width="100%"
                    height="100%"
                    colWidths={160}
                    autoColumnSize={true}
                    licenseKey="non-commercial-and-evaluation"
                    contextMenu={true}
                    filters={true}
                    dropdownMenu={true}
                    readOnly
                />
            </Suspense>
        </div>
    );
};

export default SpreadsheetViewer; 