// frontend/src/pages/HomePage.jsx
import React from 'react';
import { Link } from 'react-router-dom';

const HomePage = () => {
    return (
        <div className="container">
            <h1>Welcome to the ISO Payment Engine</h1>
            <p>This is a demo application to process ISO 20022 `pain.001` payment messages.</p>
            <p>You can:</p>
            <ul>
                <li><Link to="/payments/new">Submit a new payment XML</Link></li>
                <li><Link to="/payments">View a list of all processed payments</Link></li>
            </ul>
        </div>
    );
};

export default HomePage;
