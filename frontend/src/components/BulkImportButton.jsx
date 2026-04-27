import React, { useRef } from 'react';
import moviesAPI from '../services/api.js';

function BulkImportButton() {
    const fileInputRef = useRef();

    const handleFileChange = async (e) => {
        const file = e.target.files[0];
        if (!file) return;
        const formData = new FormData();
        formData.append('file', file);

        try {
            const token = localStorage.getItem('auth_token');
            const headers = {};
            if (token) headers['Authorization'] = `Bearer ${token}`;
            const response = await fetch(
                `${moviesAPI.API_BASE_URL}/api/products/products/bulk-import/`,
                {
                    method: 'POST',
                    body: formData,
                }
            );
            const data = await response.json();
            if (response.ok) {
                alert(data.message || 'Import successful!');
            } else {
                alert(data.error || 'Import failed.');
            }
        } catch (err) {
            alert('Error uploading file.');
        }
    };

    return (
        <div style={{ marginTop: '1rem' }}>
            <button onClick={() => fileInputRef.current.click()} className="nav-link" style={{ width: '100%' }}>
                Bulk Import CSV
            </button>
            <input
                type="file"
                accept=".csv"
                ref={fileInputRef}
                style={{ display: 'none' }}
                onChange={handleFileChange}
            />
        </div>
    );
}

export default BulkImportButton;
