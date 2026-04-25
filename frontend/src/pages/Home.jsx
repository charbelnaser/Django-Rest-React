import React from 'react';
import Header from '../components/Common/Header';
import MovieCard from '../components/MovieCard';
import Search from '../components/Search';
import './Home.css';

const Home = () => {
  // Mock data for now
  const trendingMovies = [
    {
      id: 1,
      title: "The Batman",
      poster_path: "/74xTEgt7R36Fpooo50r9T25onhq.jpg",
      vote_average: 8.2,
      release_date: "2022-03-01"
    },
    {
      id: 2,
      title: "Spider-Man: No Way Home",
      poster_path: "/1g0dhYtq4irTY1GPXvft6k4YLjm.jpg",
      vote_average: 8.4,
      release_date: "2021-12-15"
    },
    {
      id: 3,
      title: "Dune",
      poster_path: "/d5NXSklXo0qyIYkgV94XAgMIckC.jpg",
      vote_average: 8.0,
      release_date: "2021-10-21"
    },
    {
      id: 4,
      title: "Top Gun: Maverick",
      poster_path: "/62HCnUTziyWcpDaBO2i1DX17ljH.jpg",
      vote_average: 8.3,
      release_date: "2022-05-24"
    }
  ];

  const topRatedMovies = [
    {
      id: 5,
      title: "The Shawshank Redemption",
      poster_path: "/q6y0Go1tsGEsmtFryDOJo3dEmqu.jpg",
      vote_average: 9.3,
      release_date: "1994-09-23"
    },
    {
      id: 6,
      title: "The Godfather",
      poster_path: "/3bhkrj58Vtu7enYsRolD1fZdja1.jpg",
      vote_average: 9.2,
      release_date: "1972-03-14"
    },
    {
      id: 7,
      title: "The Dark Knight",
      poster_path: "/qJ2tW6WMUDux911r6m7haRef0WH.jpg",
      vote_average: 9.0,
      release_date: "2008-07-16"
    },
    {
      id: 8,
      title: "Pulp Fiction",
      poster_path: "/d5iIlFn5s0ImszYzBPb8JPIfbXD.jpg",
      vote_average: 8.9,
      release_date: "1994-10-14"
    }
  ];

  return (
    <div className="home">
      <Header />
      
      <main className="home-main">
        {/* Hero Section */}
        <section className="hero-section">
          <div className="hero-content">
            <h1>Discover Amazing Movies</h1>
            <p>Explore trending films, track your favorites, and build your personal movie vault</p>
            <Search />
          </div>
        </section>

        {/* Trending Movies */}
        <section className="movies-section">
          <div className="container">
            <div className="section-header">
              <h2>Trending Now</h2>
              <button className="btn btn-secondary">View All</button>
            </div>
            <div className="movies-grid">
              {trendingMovies.map(movie => (
                <MovieCard key={movie.id} movie={movie} />
              ))}
            </div>
          </div>
        </section>

        {/* Products */}
        <section className="movies-section">
          <div className="container">
            <div className="section-header">
              <h2>Products</h2>
              <button className="btn btn-secondary">View All</button>
            </div>
            <div className="movies-grid">
              {topRatedMovies.map(product => (
                <MovieCard key={product.id} product={product} />
              ))}
            </div>
          </div>
        </section>

        {/* Quick Stats */}
        <section className="stats-section">
          <div className="container">
            <div className="stats-grid">
              <div className="stat-card">
                <h3>Movies Watched</h3>
                <span className="stat-number">24</span>
              </div>
              <div className="stat-card">
                <h3>In Watchlist</h3>
                <span className="stat-number">12</span>
              </div>
              <div className="stat-card">
                <h3>Favorites</h3>
                <span className="stat-number">8</span>
              </div>
              <div className="stat-card">
                <h3>This Month</h3>
                <span className="stat-number">6</span>
              </div>
            </div>
          </div>
        </section>
      </main>
    </div>
  );
};

export default Home;
