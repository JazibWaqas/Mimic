// Google Drive API configuration
// Replace these values with your credentials from Google Cloud Console
const CLIENT_ID = '1021568936448-7bmqj4o53ds8m3clqivehj4iucjs1rei.apps.googleusercontent.com';
const API_KEY = 'AIzaSyCIaswXWkrpeN8irNrJtRB70ySPqiCamPI';
const DISCOVERY_DOCS = ['https://www.googleapis.com/discovery/v1/apis/drive/v3/rest'];
const SCOPES = 'https://www.googleapis.com/auth/drive.readonly https://www.googleapis.com/auth/drive.file';

// State variables
let isInitialized = false;
let tokenClient = null;
let gapiInited = false;
let gisInited = false;
let accessToken = null;
let accessTokenExpiry = null;

// Initialize the Google API client
export const initializeGoogleDrive = async () => {
    if (isInitialized) return true;
    // Load GAPI
    await new Promise((resolve, reject) => {
        if (window.gapi) return resolve();
        const script = document.createElement('script');
        script.src = 'https://apis.google.com/js/api.js';
        script.onload = resolve;
        script.onerror = reject;
        document.body.appendChild(script);
    });
    // Load Picker
    await new Promise((resolve, reject) => {
        window.gapi.load('client:picker', async () => {
            await window.gapi.client.init({ apiKey: API_KEY, discoveryDocs: DISCOVERY_DOCS });
            gapiInited = true;
            resolve();
        });
    });
    // Load GIS
    await new Promise((resolve, reject) => {
        if (window.google && window.google.accounts && window.google.accounts.oauth2) return resolve();
        const script = document.createElement('script');
        script.src = 'https://accounts.google.com/gsi/client';
        script.onload = resolve;
        script.onerror = reject;
        document.body.appendChild(script);
    });
    gisInited = true;
    // Token client
    tokenClient = window.google.accounts.oauth2.initTokenClient({
        client_id: CLIENT_ID,
        scope: SCOPES,
        callback: (tokenResponse) => {
            if (tokenResponse && tokenResponse.access_token) {
                accessToken = tokenResponse.access_token;
                // Google tokens are valid for 1 hour
                accessTokenExpiry = Date.now() + 60 * 60 * 1000;
                localStorage.setItem('googleDriveAccessToken', accessToken);
                localStorage.setItem('googleDriveAccessTokenExpiry', accessTokenExpiry);
            }
        }
    });
    // Restore token if available
    const storedToken = localStorage.getItem('googleDriveAccessToken');
    const storedExpiry = localStorage.getItem('googleDriveAccessTokenExpiry');
    if (storedToken && storedExpiry && Date.now() < parseInt(storedExpiry, 10)) {
        accessToken = storedToken;
        accessTokenExpiry = parseInt(storedExpiry, 10);
    }
    isInitialized = true;
    return true;
};

// Create and show the Google Drive Picker
export const showGoogleDrivePicker = async (callback) => {
    if (!isInitialized || !gapiInited || !gisInited) throw new Error('Google Drive not initialized');
    // Use cached token if valid
    if (accessToken && accessTokenExpiry && Date.now() < accessTokenExpiry) {
        const picker = new window.google.picker.PickerBuilder()
            .addView(window.google.picker.ViewId.DOCS)
            .setOAuthToken(accessToken)
            .setDeveloperKey(API_KEY)
            .setCallback(callback)
            .build();
        picker.setVisible(true);
        return;
    }
    // Otherwise, get a new token
    tokenClient.callback = (tokenResponse) => {
        if (tokenResponse && tokenResponse.access_token) {
            accessToken = tokenResponse.access_token;
            accessTokenExpiry = Date.now() + 60 * 60 * 1000;
            localStorage.setItem('googleDriveAccessToken', accessToken);
            localStorage.setItem('googleDriveAccessTokenExpiry', accessTokenExpiry);
            const picker = new window.google.picker.PickerBuilder()
                .addView(window.google.picker.ViewId.DOCS)
                .setOAuthToken(accessToken)
                .setDeveloperKey(API_KEY)
                .setCallback(callback)
                .build();
            picker.setVisible(true);
        }
    };
    tokenClient.requestAccessToken({ prompt: '' });
};

// List files from Google Drive
export const listFiles = async () => {
    try {
        console.log('Getting auth token for file listing');
        const token = await getAuthToken();
        
        const response = await gapi.client.drive.files.list({
            pageSize: 10,
            fields: 'files(id, name, mimeType, size, createdTime)',
            orderBy: 'createdTime desc'
        });

        console.log('Files listed successfully:', response.result.files);
        return response.result.files;
    } catch (error) {
        console.error('Error listing files:', error);
        throw error;
    }
};

// Download file from Google Drive
export const downloadFile = async (fileId) => {
    if (!fileId) throw new Error('No fileId provided');
    if (!accessToken || !accessTokenExpiry || Date.now() >= accessTokenExpiry) {
        throw new Error('Google Drive access token is missing or expired. Please re-authenticate.');
    }
    const response = await fetch(
        `https://www.googleapis.com/drive/v3/files/${fileId}?alt=media`,
        {
            headers: {
                Authorization: `Bearer ${accessToken}`,
            },
        }
    );
    if (!response.ok) throw new Error('Failed to download file');
    return await response.blob();
};

// Upload file to Google Drive
export const uploadFile = async (file) => {
    try {
        console.log('Getting auth token for file upload');
        const token = await getAuthToken();
        
        const metadata = {
            name: file.name,
            mimeType: file.type
        };

        const form = new FormData();
        form.append('metadata', new Blob([JSON.stringify(metadata)], { type: 'application/json' }));
        form.append('file', file);

        const response = await fetch('https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`
            },
            body: form
        });

        if (!response.ok) {
            throw new Error('Failed to upload file');
        }

        const result = await response.json();
        console.log('File uploaded successfully:', result);
        return result;
    } catch (error) {
        console.error('Error uploading file:', error);
        throw error;
    }
};

// Get file metadata
export const getFileMetadata = async (fileId) => {
  const token = await getAuthToken();
  
  try {
    const response = await window.gapi.client.drive.files.get({
      fileId: fileId,
      fields: 'id, name, mimeType, size, createdTime',
    });
    
    return response.result;
  } catch (error) {
    console.error('Error getting file metadata:', error);
    throw error;
  }
}; 