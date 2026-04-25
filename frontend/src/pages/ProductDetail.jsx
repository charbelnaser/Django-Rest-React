import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import apiService from '../services/api';
import './ProductDetail.css';

const ProductDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [product, setProduct] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [editMode, setEditMode] = useState(false);
  const [form, setForm] = useState({});

  useEffect(() => {
    const fetchProduct = async () => {
      setLoading(true);
      try {
        const data = await apiService.getMovieDetails(id); // getProducDetails works for products
        setProduct(data);
        setForm(data);
      } catch (err) {
        setError('Failed to load product');
      } finally {
        setLoading(false);
      }
    };
    fetchProduct();
  }, [id]);

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleUpdate = async (e) => {
    e.preventDefault();
    try {
      const url = `${apiService.API_BASE_URL}/api/products/products/${id}/`;
      const response = await fetch(url, {
        method: 'PUT',
        headers: apiService.getHeaders(),
        body: JSON.stringify(form)
      });
      if (!response.ok) throw new Error('Update failed');
      const updated = await response.json();
      setProduct(updated);
      setEditMode(false);
    } catch (err) {
      setError('Failed to update product');
    }
  };

  const handleDelete = async () => {
    if (!window.confirm('Are you sure you want to delete this product?')) return;
    try {
      const url = `${apiService.API_BASE_URL}/api/products/products/${id}/`;
      const response = await fetch(url, {
        method: 'DELETE',
        headers: apiService.getHeaders()
      });
      if (!response.ok) throw new Error('Delete failed');
      navigate('/');
    } catch (err) {
      setError('Failed to delete product');
    }
  };

  if (loading) return <div className="spinner-center"><div className="spinner" /></div>;
  if (error) return <div className="error-message">{error}</div>;
  if (!product) return null;

  return (
    <div className="product-detail-card">
      <button className="back-btn" onClick={() => navigate(-1)}>&larr; Back</button>
      <h2 className="detail-title">Product Detail</h2>
      {editMode ? (
        <form className="product-edit-form" onSubmit={handleUpdate}>
          <div className="form-row">
            <label>Name</label>
            <input name="name" value={form.name || ''} onChange={handleChange} placeholder="Name" required />
          </div>
          <div className="form-row">
            <label>Description</label>
            <textarea name="description" value={form.description || ''} onChange={handleChange} placeholder="Description" rows={3} />
          </div>
          <div className="form-row">
            <label>Price (¤)</label>
            <input name="price" type="number" value={form.price || ''} onChange={handleChange} placeholder="Price" min="0" step="0.01" />
          </div>
          <div className="form-row">
            <label>VAT Rate</label>
            <input name="vat_rate" type="number" value={form.vat_rate || ''} onChange={handleChange} placeholder="VAT Rate" min="0" step="0.01" />
          </div>
          <div className="form-row">
            <label>Expiration Date</label>
            <input name="expiration_date" type="date" value={form.expiration_date || ''} onChange={handleChange} placeholder="Expiration Date" />
          </div>
          <div className="form-row">
            <label>Stock</label>
            <input name="stock" type="number" value={form.stock || ''} onChange={handleChange} placeholder="Stock" min="0" />
          </div>
          <div className="form-row">
            <label>Category</label>
            <input name="category" value={form.category || ''} onChange={handleChange} placeholder="Category" />
          </div>
          <div className="form-row">
            <label>Image URL</label>
            <input name="image_url" value={form.image_url || ''} onChange={handleChange} placeholder="Image URL" />
          </div>
          <div className="form-actions">
            <button className="save-btn" type="submit">Save</button>
            <button className="cancel-btn" type="button" onClick={() => setEditMode(false)}>Cancel</button>
          </div>
        </form>
      ) : (
        <div className="product-info">
          <div className="product-image-wrap">
            <img className="product-image" src={product.image_url} alt={product.name} />
          </div>
          <div className="product-fields">
            <div className="field-row"><span className="field-label">ID:</span> <span>{product.id}</span></div>
            <div className="field-row"><span className="field-label">Name:</span> <span>{product.name}</span></div>
            <div className="field-row"><span className="field-label">Description:</span> <span>{product.description}</span></div>
            <div className="field-row"><span className="field-label">Price:</span> <span>{product.price} ¤</span></div>
            <div className="field-row"><span className="field-label">VAT Rate:</span> <span>{product.vat_rate}</span></div>
            <div className="field-row"><span className="field-label">Expiration Date:</span> <span>{product.expiration_date}</span></div>
            <div className="field-row"><span className="field-label">Stock:</span> <span>{product.stock}</span></div>
            <div className="field-row"><span className="field-label">Category:</span> <span>{product.category}</span></div>
          </div>
          <div className="product-actions">
            <button className="edit-btn" onClick={() => setEditMode(true)}>Edit</button>
            <button className="delete-btn" onClick={handleDelete}>Delete</button>
          </div>
        </div>
      )}
    </div>
  );
};

export default ProductDetail;
