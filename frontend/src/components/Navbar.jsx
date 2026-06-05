import { NavLink } from 'react-router-dom';
import { useState } from 'react';
import { Menu, X } from 'lucide-react';
import Logo from './Logo';

export default function Navbar() {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <nav className="navbar">
      <div className="container">
        <NavLink to="/" className="navbar-brand">
          <Logo height={42} useGradient={true} />
        </NavLink>

        <button
          className="navbar-toggle"
          onClick={() => setIsOpen(!isOpen)}
          aria-label="Toggle navigation"
        >
          {isOpen ? <X size={22} /> : <Menu size={22} />}
        </button>

        <div className={`navbar-links ${isOpen ? 'open' : ''}`}>
          <NavLink to="/" end onClick={() => setIsOpen(false)}>Home</NavLink>
          <NavLink to="/dashboard" onClick={() => setIsOpen(false)}>Dashboard</NavLink>
          <NavLink to="/disease" onClick={() => setIsOpen(false)}>Disease Risk</NavLink>
          <NavLink to="/irrigation" onClick={() => setIsOpen(false)}>Irrigation</NavLink>
          <NavLink to="/about" onClick={() => setIsOpen(false)}>About</NavLink>
        </div>
      </div>
    </nav>
  );
}
