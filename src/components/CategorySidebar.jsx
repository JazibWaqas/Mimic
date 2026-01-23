// ... existing imports ...
import React, { useState, useEffect, useMemo } from 'react';
import '../styles/CategorySidebar.css';

export default function CategorySidebar({ onSelect }) {
  const [categories, setCategories] = useState([]);
  const [expanded, setExpanded] = useState(null);

  useEffect(() => {
    // Fetch categories from backend
    fetch('/api/categories')
      .then(res => res.json())
      .then(data => setCategories(data))
      .catch(err => {
        setCategories([]);
        // Optionally handle error
      });
  }, []);

  const sortedCategories = useMemo(() => {
    return [...categories].sort((a, b) => a.name.localeCompare(b.name));
  }, [categories]);

  return (
    <div className="category-sidebar-container">
      <h3 className="category-sidebar-title">Categories</h3>
      <ul className="category-list">
        {sortedCategories.map((cat, idx) => (
          <li key={cat.name}>
            <div
              className={`category-name${expanded === idx ? ' expanded' : ''}`}
              onClick={() => setExpanded(expanded === idx ? null : idx)}
            >
              {cat.name}
            </div>
            {expanded === idx && cat.subCategories && (
              <ul className="subcategory-list">
                {cat.subCategories.map((sub) => (
                  <li key={sub}>
                    <button
                      type="button"
                      className="subcategory-btn"
                      onClick={() => onSelect(cat.name, sub,true)}
                    >
                      {sub}
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
}