// frontend/src/pages/PaymentListPage.jsx
import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { getPayments } from '../api';

const PaymentListPage = () => {
  const [payments, setPayments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchPayments = async () => {
      try {
        const data = await getPayments();
        setPayments(data);
      } catch (err) {
        setError(err.message || 'Failed to fetch payments.');
      } finally {
        setLoading(false);
      }
    };
    fetchPayments();
  }, []);

  if (loading) {
    return <div className="container">Loading payments...</div>;
  }

  if (error) {
    return <div className="container message error">Error: {error}</div>;
  }

  return (
    <div className="container">
      <h1>All Payments</h1>
      {payments.length === 0 ? (
        <p>No payments found. <Link to="/payments/new">Create one now!</Link></p>
      ) : (
        <table>
          <thead>
            <tr>
              <th>Message ID</th>
              <th>Creation Date/Time</th>
              <th>Number of Txns</th>
              <th>Control Sum</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {payments.map((payment) => (
              <tr key={payment.id}>
                <td>{payment.msg_id}</td>
                <td>{new Date(payment.cre_dt_tm).toLocaleString()}</td>
                <td>{payment.nb_of_txs}</td>
                <td>{payment.ctrl_sum}</td>
                <td>
                  <Link to={`/payments/${payment.id}`}>View Details</Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
};

export default PaymentListPage;
