import React from 'react';
import '../styles/ShinyText.css';

const ShinyText = ({ text, className = '', speed = 2.5 }) => {
  return (
    <span
      className={`shiny-text ${className}`}
      style={{ animationDuration: `${speed}s` }}
    >
      {text}
    </span>
  );
};

export default ShinyText;