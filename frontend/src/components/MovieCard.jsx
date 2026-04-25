import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useWatchlist } from '../context/WatchlistContext';

const MovieCard = ({ product }) => {
  const navigate = useNavigate();
  // Destructure product fields
  const {
    id,
    name,
    description,
    price,
    vat_rate,
    expiration_date,
    stock,
    category,
    image_url
  } = product;

  // Helper to get image URL
  const getImageUrl = () => {
    if (!image_url) return '/placeholder.png';
    // If image_url is absolute (starts with http), use as is
    if (image_url.startsWith('http')) return image_url;
    // Otherwise, use as relative path
    return image_url;
  };

  return (
    <div className="movie-card" onClick={() => navigate(`/products/${id}`)} style={{ cursor: 'pointer' }}>
      <div className="movie-poster-container">
        <img
          src={getImageUrl()}
          alt={name}
        />
      </div>
      <div className="mt-4">
        <h3>{name}</h3>
        <div className="content">
          <p className="desc">{description}</p>
          <p className="price">Price: {price} $</p>
          <p className="category">Category: {category}</p>
          <p className="stock">Stock: {stock}</p>
          {expiration_date && <p className="exp">Expires: {expiration_date}</p>}
        </div>
      </div>
    </div>
  );
}

export default MovieCard;
