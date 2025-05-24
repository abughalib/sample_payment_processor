// frontend/src/App.jsx
import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Navbar from "./components/Navbar";
import HomePage from "./pages/HomePage";
import PaymentListPage from "./pages/PaymentListPage";
import PaymentDetailPage from "./pages/PaymentDetailPage";
import CreatePaymentPage from "./pages/CreatePaymentPage";
import RulesManagementPage from "./pages/RulesManagementPage";

function App() {
  return (
    <Router>
      <Navbar />
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/payments" element={<PaymentListPage />} />
        <Route path="/payments/new" element={<CreatePaymentPage />} />
        <Route path="/payments/:documentId" element={<PaymentDetailPage />} />
        <Route path="/rules" element={<RulesManagementPage />} />
      </Routes>
    </Router>
  );
}

export default App;
