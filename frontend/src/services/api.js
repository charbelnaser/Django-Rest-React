// Django Backend API Service
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

class MoviesVaultAPI {
  constructor() {
    this.token = localStorage.getItem('auth_token');
  }

  // Authentication headers with proper JWT token
  getHeaders() {
    const headers = {
      'Content-Type': 'application/json',
    };
    
    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }
    
    return headers;
  }

  // ===== AUTHENTICATION METHODS =====

  // Register user with email/password
  async register(userData) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/auth/register/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(userData)
      });

      if (!response.ok) {
        let error;
        try {
          error = await response.json();
        } catch (parseError) {
          // If JSON parsing fails, create a generic error
          throw new Error(`Registration failed (${response.status})`);
        }
        
        // Extract error message with multiple fallbacks
        const errorMessage = error.error || error.message || error.detail || error.non_field_errors?.[0] || `Registration failed (${response.status})`;
        throw new Error(errorMessage);
      }

      const data = await response.json();
      this.token = data.access;
      localStorage.setItem('auth_token', this.token);
      localStorage.setItem('refresh_token', data.refresh);
      return data;
    } catch (err) {
      // If it's already our custom error, re-throw it
      if (err.message && !err.message.includes('fetch') && !err.message.includes('Failed to fetch')) {
        throw err;
      }
      // Network or other errors
      throw new Error('Network error. Please check your connection.');
    }
  }

  // Login user with email/password
  async login(email, password) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/auth/login/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      });

      if (!response.ok) {
        let error;
        try {
          error = await response.json();
        } catch (parseError) {
          // If JSON parsing fails, create a generic error
          throw new Error(`Login failed (${response.status})`);
        }
        
        // Extract error message with multiple fallbacks
        const errorMessage = error.error || error.message || error.detail || error.non_field_errors?.[0] || `Login failed (${response.status})`;
        throw new Error(errorMessage);
      }

      const data = await response.json();
      this.token = data.access;
      localStorage.setItem('auth_token', this.token);
      localStorage.setItem('refresh_token', data.refresh);
      return data;
    } catch (err) {
      // If it's already our custom error, re-throw it
      if (err.message && !err.message.includes('fetch') && !err.message.includes('Failed to fetch')) {
        throw err;
      }
      // Network or other errors
      throw new Error('Network error. Please check your connection.');
    }
  }

  // Logout user
  async logout() {
    try {
      const refreshToken = localStorage.getItem('refresh_token');
      
      // Always clear local storage first
      this.token = null;
      localStorage.removeItem('auth_token');
      localStorage.removeItem('refresh_token');
      
      // Try to blacklist token on server if refresh token exists
      if (refreshToken) {
        try {
          const response = await fetch(`${API_BASE_URL}/api/auth/logout/`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              // Don't include Authorization header for logout
            },
            body: JSON.stringify({ refresh: refreshToken })
          });
          
          if (response.ok) {
            console.log('Logout successful - token blacklisted');
          } else {
            console.warn('Logout request failed, but local storage cleared');
          }
        } catch (error) {
          console.warn('Logout request failed:', error);
          // Don't throw error - logout should always succeed locally
        }
      }
      
      return { message: 'Logout successful' };
    } catch (error) {
      // Even if everything fails, clear local storage
      this.token = null;
      localStorage.removeItem('auth_token');
      localStorage.removeItem('refresh_token');
      console.warn('Logout error, but local storage cleared:', error);
      return { message: 'Logout successful' };
    }
  }

  // Check if user is authenticated
  isAuthenticated() {
    return !!this.token;
  }

  // ===== WATCHLIST API METHODS =====
  
  // Add movie to watchlist
  async addToWatchlist(movieData) {
    const response = await fetch(`${API_BASE_URL}/api/watchlist/add/`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify({
        movie_id: movieData.id,
        movie_title: movieData.title,
        movie_poster: movieData.poster_path,
        movie_overview: movieData.overview,
        movie_release_date: movieData.release_date,
        movie_rating: movieData.vote_average
      })
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Failed to add to watchlist');
    }

    return await response.json();
  }

  // Remove movie from watchlist
  async removeFromWatchlist(movieId) {
    const response = await fetch(`${API_BASE_URL}/api/watchlist/remove/${movieId}/`, {
      method: 'DELETE',
      headers: this.getHeaders()
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Failed to remove from watchlist');
    }

    return await response.json();
  }

  // Get user's watchlist
  // async getWatchlist(status = null) {
  //   const url = status 
  //     ? `${API_BASE_URL}/api/watchlist/?status=${status}`
  //     : `${API_BASE_URL}/api/watchlist/`;
      
  //   const response = await fetch(url, {
  //     method: 'GET',
  //     headers: this.getHeaders()
  //   });

  //   if (!response.ok) {
  //     const error = await response.json();
  //     throw new Error(error.error || 'Failed to get watchlist');
  //   }

  //   return await response.json();
  // }

  // Check if movie is in watchlist
  async checkWatchlistStatus(movieId) {
    const response = await fetch(`${API_BASE_URL}/api/watchlist/check/${movieId}/`, {
      method: 'GET',
      headers: this.getHeaders()
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Failed to check watchlist status');
    }

    return await response.json();
  }

  // Toggle watch status (watched/want to watch)
  // async toggleWatchStatus(movieId) {
  //   const response = await fetch(`${API_BASE_URL}/api/watchlist/${movieId}/toggle/`, {
  //     method: 'PUT',
  //     headers: this.getHeaders()
  //   });

  //   if (!response.ok) {
  //     const error = await response.json();
  //     throw new Error(error.error || 'Failed to toggle watch status');
  //   }

  //   return await response.json();
  // }

  // Get watchlist statistics
  async getWatchlistStats() {
    const response = await fetch(`${API_BASE_URL}/api/watchlist/stats/`, {
      method: 'GET',
      headers: this.getHeaders()
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Failed to get watchlist stats');
    }

    return await response.json();
  }

  // ===== TMDB MOVIE API METHODS =====

  // Search products - fetch by query from backend
  async searchMovies(query) {
    try {
      const searchResponse = await fetch(
        `${API_BASE_URL}/api/products/products/search/?query=${encodeURIComponent(query)}`,
        { headers: this.getHeaders() }
      );
      if (!searchResponse.ok) {
        throw new Error('Failed to search products');
      }
      const searchData = await searchResponse.json();
      // Return as results array for compatibility
      return {
        results: Array.isArray(searchData) ? searchData : [],
        total_results: Array.isArray(searchData) ? searchData.length : 0,
        total_pages: 1,
        page: 1
      };
    } catch (error) {
      console.error('Search products error:', error);
      throw new Error('Failed to search products');
    }
  }

  // Get popular movies - fetch up to 40 movies (2 pages)
  async getPopularMovies() {
    const allResults = [];
    let totalPages = 1;
    let totalResults = 0;
    
    try {
      // Fetch first 2 pages to get 40 movies
      for (let page = 1; page <= 2; page++) {
        const response = await fetch(
          `${API_BASE_URL}/api/products/popular/?page=${page}`,
          { headers: this.getHeaders() }
        );

        if (!response.ok) {
          throw new Error('Failed to fetch popular movies');
        }

        const data = await response.json();
        
        if (page === 1) {
          totalPages = data.total_pages;
          totalResults = data.total_results;
        }
        
        allResults.push(...data.results);
        
        // Stop if we've reached the end of results or got 40 movies
        if (page >= totalPages || allResults.length >= 40) {
          break;
        }
      }
      
      return {
        results: allResults.slice(0, 40), // Limit to 40 movies
        total_results: totalResults,
        total_pages: 1, // Always return 1 page since we're showing all results
        page: 1
      };
    } catch (error) {
      console.error('Get popular movies error:', error);
      throw new Error('Failed to fetch popular movies');
    }
  }

  // Get trending movies - fetch up to 40 movies (2 pages)
  // async getTrendingMovies() {
  //   const allResults = [];
  //   let totalPages = 1;
  //   let totalResults = 0;
    
  //   try {
  //     // Fetch first 2 pages to get 40 movies
  //     for (let page = 1; page <= 2; page++) {
  //       const response = await fetch(
  //         `${API_BASE_URL}/api/products/trending/?page=${page}`,
  //         { headers: this.getHeaders() }
  //       );

  //       if (!response.ok) {
  //         throw new Error('Failed to fetch trending movies');
  //       }

  //       const data = await response.json();
        
  //       if (page === 1) {
  //         totalPages = data.total_pages;
  //         totalResults = data.total_results;
  //       }
        
  //       allResults.push(...data.results);
        
  //       // Stop if we've reached the end of results or got 40 movies
  //       if (page >= totalPages || allResults.length >= 40) {
  //         break;
  //       }
  //     }
      
  //     return {
  //       results: allResults.slice(0, 40), // Limit to 40 movies
  //       total_results: totalResults,
  //       total_pages: 1, // Always return 1 page since we're showing all results
  //       page: 1
  //     };
  //   } catch (error) {
  //     console.error('Get trending movies error:', error);
  //     throw new Error('Failed to fetch trending movies');
  //   }
  // }

  // Get top rated movies - fetch up to 40 movies (2 pages)
  async getTopRatedMovies() {
    const allResults = [];
    let totalPages = 1;
    let totalResults = 0;
    
    try {
      // Fetch first 2 pages to get 40 movies
      for (let page = 1; page <= 2; page++) {
        const response = await fetch(
          `${API_BASE_URL}/api/products/products/?page=${page}`,
          { headers: this.getHeaders() }
        );

        if (!response.ok) {
          throw new Error('Failed to fetch top rated movies');
        }

        const data = await response.json();
        
        if (page === 1) {
          totalPages = data.total_pages;
          totalResults = data.total_results;
        }
        
        allResults.push(...data.results);
        
        // Stop if we've reached the end of results or got 40 movies
        if (page >= totalPages || allResults.length >= 40) {
          break;
        }
      }
      
      return {
        results: allResults.slice(0, 40), // Limit to 40 movies
        total_results: totalResults,
        total_pages: 1, // Always return 1 page since we're showing all results
        page: 1
      };
    } catch (error) {
      console.error('Get top rated movies error:', error);
      throw new Error('Failed to fetch top rated movies');
    }
  }


  // Get upcoming movies
  async getUpcomingMovies(page = 1) {
    try {
      const response = await fetch(
        `${API_BASE_URL}/api/products/upcoming/?page=${page}`,
        { headers: this.getHeaders() }
      );

      if (!response.ok) {
        throw new Error('Failed to fetch upcoming movies');
      }

      return await response.json();
    } catch (error) {
      console.error('Get upcoming movies error:', error);
      throw error;
    }
  }



  // Get movie details by ID
  async getMovieDetails(movieId) {
    try {
      const response = await fetch(
        `${API_BASE_URL}/api/products/products/${movieId}/`,
        { headers: this.getHeaders() }
      );

     
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Get movie details error:', error);
      throw error;
    }
  }

  // Get full image URL
  getImageUrl(imagePath, size = 'w500') {
    if (!imagePath) return '/no-movie.png';
    return `https://image.tmdb.org/t/p/${size}${imagePath}`;
  }

  // Health check
  async healthCheck() {
    try {
      const response = await fetch(`${API_BASE_URL}/core/health/`);
      return await response.json();
    } catch (error) {
      console.error('Health check failed:', error);
      throw error;
    }
  }
}

// Create and export singleton instance
const apiService = new MoviesVaultAPI();
apiService.API_BASE_URL = API_BASE_URL;
export default apiService;

// Also export with the old name for backward compatibility
export const moviesAPI = apiService;
