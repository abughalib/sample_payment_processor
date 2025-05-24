// frontend/src/components/Navbar.jsx
import React from "react";
import { Link } from "react-router-dom";

const Navbar = () => {
  return (
    <nav>
      <Link to="/">Home</Link>
      <Link to="/payments">Payments List</Link>
      <Link to="/payments/new">Create Payment</Link>
      <Link to="/rules">Rules Management</Link>
    </nav>
  );
};

export default Navbar;
