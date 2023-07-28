import React from 'react';

function Header() {
  return (
    <nav className="navbar mb-3">
      <span>
        <img
          className="logo"
          alt="Beans Logo"
          src="/img/beans-white.svg"
        />
        <span className="logo-font">
          Beans
        </span>
      </span>
      <img
        alt="Yelp Logo"
        src="https://s3-media0.fl.yelpcdn.com/assets/public/yelp_logo_www_home.yji-7d24f1680fdb98ca54a82c26cdbdc7bd.svg"
      />
    </nav>
  );
}

export default Header;
