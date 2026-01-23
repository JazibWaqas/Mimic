import React from 'react';

const Footer = () => (
  <footer>
    <div className="background">
      {/* SVG background can be added here if needed */}
    </div>
    <section>
      <ul className="socials">
        <li><a className="fa-brands fa-x-twitter" href="#" aria-label="Twitter"></a></li>
        <li><a className="fa-brands fa-facebook" href="#" aria-label="Facebook"></a></li>
        <li><a className="fa-brands fa-linkedin" href="#" aria-label="LinkedIn"></a></li>
      </ul>
      <ul className="links">
        <li><a href="#">Home</a></li>
        <li><a href="#">About</a></li>
        <li><a href="#">Portfolio</a></li>
        <li><a href="#">Skills</a></li>
        <li><a href="#">Contact</a></li>
      </ul>
      <p className="legal">© 2024 All rights reserved</p>
    </section>
  </footer>
);

export default Footer; 