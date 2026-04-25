import { useEffect, useState } from 'react'
import { BrowserRouter as Router, Routes, Route, useParams } from 'react-router-dom';
import ProductDetail from './pages/ProductDetail.jsx';
import PasswordResetConfirm from './components/PasswordResetConfirm';
import './App.css'
import Search from './components/Search.jsx'
import Spinner from './components/Spinner.jsx'
import MovieCard from './components/MovieCard.jsx'
import Login from './components/Login.jsx'
import Navigation from './components/Navigation.jsx'
import WatchlistPage from './components/WatchlistPage.jsx'
import { useAuth } from './context/AuthContext'
import { WatchlistProvider } from './context/WatchlistContext'
import moviesAPI from './services/api.js'

function PasswordResetConfirmWrapper() {
  const { token } = useParams();
  return <PasswordResetConfirm token={token} />;
}

const App = () => {
  const { isAuthenticated, loading, user, logout } = useAuth();
  const [searchTerm, setSearchTerm] = useState('');
  const [movieList, setMovieList] = useState([]);
  const [errorMessage, setErrorMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [trendingMovies, setTrendingMovies] = useState([]);
  const [currentView, setCurrentView] = useState('home');
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [showWelcome, setShowWelcome] = useState(false);

  const handleHomeClick = () => {
    setSearchTerm('');
    setCurrentView('home');
    setMovieList([]);
  };

  const toggleMobileMenu = () => {
    setIsMobileMenuOpen(!isMobileMenuOpen);
  };

  const fetchMovies = async (query = '') => {
    setIsLoading(true);
    setErrorMessage('');

    try {
      let data;
      
      if (query) {
        // Search movies using Django backend - now gets top 20 movies with advanced sorting
        data = await moviesAPI.searchMovies(query);
        // No additional sorting needed - API handles advanced sorting by popularity/trending + keyword relevance
      } else if (currentView === 'home') {
        // For home, return empty (home doesn't show movies by default)
        setMovieList([]);
        setIsLoading(false);
        return;
      } else {
        // Get movies based on current view - now gets 40 movies
        switch(currentView) {
          case 'top-rated':
            data = await moviesAPI.getTopRatedMovies();
            break;
          // case 'trending':
          //   data = await moviesAPI.getTrendingMovies();
          //   break;
          default:
            data = await moviesAPI.getPopularMovies();
        }
      }

      // Set results - no pagination needed
      const results = data.results || [];
      setMovieList(results);
    } catch (error) {
      console.error(`Error fetching movies: ${error}`);
      setErrorMessage('Error fetching movies. Please check if Django server is running.');
      setMovieList([]);
    } finally {
      setIsLoading(false);
    }
  }

  const loadTrendingMovies = async () => {
    try {
      const data = await moviesAPI.getTrendingMovies();
      
      // Convert to the format expected by the trending section
      const trendingWithImages = data.results?.map(movie => ({
        $id: movie.id,
        title: movie.title,
        poster_url: moviesAPI.getImageUrl(movie.poster_path)
      })) || [];

      setTrendingMovies(trendingWithImages);
    } catch (error) {
      console.error(`Error fetching trending movies: ${error}`);
      // Fallback to empty array
      setTrendingMovies([]);
    }
  }

  // Navigation functions
  const handleViewChange = async (viewName) => {
    setCurrentView(viewName);
    setIsMobileMenuOpen(false); // Close mobile menu
    setSearchTerm(''); // Clear search when changing views
    
    if (viewName === 'home') {
      setMovieList([]);
      return;
    }
    
    // if (viewName === 'watchlist') {
    //   setMovieList([]);
    //   return;
    // }
    
    // For other views (top-rated, trending), fetch movies
    await fetchMovies('');
  };

  // Get dashboard title based on current view
  const getDashboardTitle = () => {
    switch(currentView) {
      case 'home': return 'Discover Products';
      case 'top-rated': return 'Products';
      case 'trending': return 'Trending Now';
      case 'watchlist': return 'Your Watchlist';
      default: return 'Movies Vault';
    }
  };

  // Get section title based on current view
  const getSectionTitle = () => {
    switch(currentView) {
      case 'home': return 'Search Results';
      case 'top-rated': return 'Products';
      case 'trending': return 'Trending Movies';
      case 'watchlist': return 'My Watchlist';
      default: return 'Movies';
    }
  };

  useEffect(() => {
    if (isAuthenticated) {
      fetchMovies(searchTerm); // No page parameter needed
    }
  }, [searchTerm, isAuthenticated]);

  // Add useEffect to handle view changes and load movies for each tab
  useEffect(() => {
    if (isAuthenticated && currentView !== 'home' && currentView !== 'watchlist' && !searchTerm) {
      fetchMovies('');
    }
  }, [currentView, isAuthenticated]);

  useEffect(() => {
    if (isAuthenticated) {
      // loadTrendingMovies();
      // Show welcome message for 3 seconds when user logs in
      setShowWelcome(true);
      const timer = setTimeout(() => {
        setShowWelcome(false);
      }, 3000);
      return () => clearTimeout(timer);
    }
  }, [isAuthenticated]);

  if (loading) {
    return (
      <main>
        <div className="pattern"/>
        <div className="wrapper">
          <Spinner />
        </div>
      </main>
    );
  }


  if (!isAuthenticated) {
    return (
      <Router>
        <Routes>
          <Route path="/reset-password/:token" element={<PasswordResetConfirmWrapper />} />
          <Route path="*" element={<Login />} />
        </Routes>
      </Router>
    );
  }

  return (
    <Router>
      <Routes>
        <Route path="/products/:id" element={
          <div className="product-detail-page">
            <ProductDetail />
          </div>
        } />
        <Route path="*" element={
          <WatchlistProvider>
            <div className="dashboard-container">
              <div className="pattern"/>
              {/* Welcome Message */}
              {showWelcome && user && (
                <div className="welcome-message">
                  <p>Welcome, {user.username}!</p>
                </div>
              )}
              {/* Mobile Header */}
              <div className="mobile-header">
                <div className="mobile-title">
                  <span className="movies-text">{getDashboardTitle()}</span>
                </div>
                <button 
                  className="mobile-menu-btn"
                  onClick={toggleMobileMenu}
                  aria-label="Toggle menu"
                >
                  <span className={`hamburger ${isMobileMenuOpen ? 'open' : ''}`}>
                    <span></span>
                    <span></span>
                    <span></span>
                  </span>
                </button>
              </div>
              {/* Navigation Sidebar */}
              <Navigation 
                onHomeClick={handleHomeClick} 
                onViewChange={handleViewChange}
                currentView={currentView}
                isMobileMenuOpen={isMobileMenuOpen}
                onMobileClose={() => setIsMobileMenuOpen(false)}
              />
              {/* Mobile Menu Overlay */}
              {isMobileMenuOpen && <div className="mobile-overlay" onClick={() => setIsMobileMenuOpen(false)} />}
              {/* Main Content */}
              <div className="dashboard-content">
                <div className="dashboard-main">
                  {/* Page Header */}
                  <div className="page-header">
                    <h2 className="page-subtitle">{getDashboardTitle()}</h2>
                  </div>
                  {/* Search Section - Only show on Home and Watchlist */}
                  {(currentView === 'home' || currentView === 'watchlist') && (
                    <Search 
                      searchTerm={searchTerm} 
                      setSearchTerm={setSearchTerm} 
                      placeholder={currentView === 'watchlist' ? "Search in your watchlist..." : "Search for ..."}
                    />
                  )}
                  {/* Hero Section - Only show on Home when no search term and no search results */}
                  {currentView === 'home' && !searchTerm && movieList.length === 0 && (
                    <section className="hero-section desktop-only">
                      <div className="hero-content">
                        {/* Hero Image */}
                        <div className="hero-image">
                          <img src="/hero.png" alt="Movies Hero" />
                        </div>
                        <p className="hero-subtitle">
                          Explore millions of movies, create your watchlist, and get personalized recommendations
                        </p>
                        {/* Hero Action Buttons */}
                        <div className="hero-buttons">
                          <button 
                            className="hero-btn"
                            onClick={() => handleViewChange('top-rated')}
                          >
                            top-rated
                          </button>
                          <button 
                            className="hero-btn"
                            onClick={() => handleViewChange('trending')}
                          >
                            Trending
                          </button>
                          <button 
                            className="hero-btn"
                            onClick={() => handleViewChange('watchlist')}
                          >
                            My Watchlist
                          </button>
                        </div>
                      </div>
                    </section>
                  )}
                  {/* Movies Section - Show title only if there are movies or loading */}
                  {currentView === 'watchlist' ? (
                    <WatchlistPage />
                  ) : (movieList.length > 0 || isLoading || errorMessage) && (
                    <section className="all-movies">
                      <h2>{getSectionTitle()}</h2>
                    {isLoading ? (
                      <Spinner />
                    ) : errorMessage ? (
                      <p className="text-red-500">{errorMessage}</p>
                    ) : (
                      <>
                        <ul>
                          {movieList.map((product) => (
                            <MovieCard key={product.id} product={product} />
                          ))}
                        </ul>
                      </>
                    )}
                  </section>
                  )}
                </div>
              </div>
            </div>
          </WatchlistProvider>
        } />
      </Routes>
    </Router>
  );
};

export default App;
