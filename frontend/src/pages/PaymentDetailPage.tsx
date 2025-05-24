// frontend/src/pages/PaymentDetailPage.jsx
import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { getPaymentDetails } from '../api';

const PaymentDetailPage = () => {
  const { documentId } = useParams();
  const [payment, setPayment] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchPaymentDetails = async () => {
      try {
        const data = await getPaymentDetails(documentId);
        setPayment(data);
      } catch (err) {
        setError(err.detail || err.message || `Failed to fetch payment details for ${documentId}.`);
      } finally {
        setLoading(false);
      }
    };
    fetchPaymentDetails();
  }, [documentId]);

  if (loading) {
    return <div className="container">Loading payment details...</div>;
  }

  if (error) {
    return <div className="container message error">Error: {error}</div>;
  }

  if (!payment) {
    return <div className="container">Payment not found.</div>;
  }

  return (
    <div className="container">
      <h1>Payment Details: {payment.msg_id}</h1>
      <p><strong>Document ID:</strong> {payment.id}</p>
      <p><strong>Creation Date/Time:</strong> {new Date(payment.cre_dt_tm).toLocaleString()}</p>
      <p><strong>Number of Transactions:</strong> {payment.nb_of_txs}</p>
      <p><strong>Control Sum:</strong> {payment.ctrl_sum}</p>
      <p><strong>Initiating Party Org ID:</strong> {payment.initg_pty_org_id_id}</p>
      <p><strong>Created At:</strong> {new Date(payment.created_at).toLocaleString()}</p>
      <p><strong>Updated At:</strong> {new Date(payment.updated_at).toLocaleString()}</p>

      <h2>Payment Information Blocks ({payment.payment_info.length})</h2>
      {payment.payment_info.length > 0 ? (
        payment.payment_info.map((pi, piIndex) => (
          <div key={pi.id} style={{ marginBottom: '1.5rem', border: '1px solid #eee', padding: '1rem', borderRadius: '5px' }}>
            <h3>Payment Info Block #{piIndex + 1} ({pi.pmt_inf_id})</h3>
            <p><strong>Method:</strong> {pi.pmt_mtd}</p>
            <p><strong>Required Execution Date:</strong> {new Date(pi.reqd_exctn_dt).toLocaleDateString()}</p>
            <h4>Debtor:</h4>
            <p><strong>Name:</strong> {pi.dbtr_nm}</p>
            <p><strong>Org ID:</strong> {pi.dbtr_org_id_id}</p>
            <p><strong>Country:</strong> {pi.dbtr_ctry_of_res}</p>
            <p><strong>Account (IBAN):</strong> {pi.dbtr_acct_iban}</p>
            <p><strong>Debtor Agent (BIC):</strong> {pi.dbtr_agt_fin_instn_id_bic}</p>

            <h4>Credit Transfer Transactions ({pi.credit_transfers.length})</h4>
            {pi.credit_transfers.length > 0 ? (
              pi.credit_transfers.map((ctt, cttIndex) => (
                <div key={ctt.id} style={{ marginLeft: '1rem', border: '1px solid #f9f9f9', padding: '0.8rem', borderRadius: '4px', marginBottom: '1rem' }}>
                  <h5>Transaction #{cttIndex + 1} ({ctt.pmt_id_end_to_end_id})</h5>
                  <p><strong>Instruction ID:</strong> {ctt.pmt_id_instr_id}</p>
                  <p><strong>Amount:</strong> {ctt.instd_amt} {ctt.instd_amt_ccy}</p>
                  <p><strong>Service Level:</strong> {ctt.pmt_tp_inf_svc_lvl_cd}</p>
                  <p><strong>Category Purpose:</strong> {ctt.pmt_tp_inf_ctgy_purp_cd}</p>
                  <p><strong>Creditor Name:</strong> {ctt.cdtr_nm}</p>
                  <p><strong>Creditor Account ID:</strong> {ctt.cdtr_acct_othr_id} ({ctt.cdtr_acct_othr_schme_nm_cd})</p>
                  <p><strong>Creditor Agent (Clearing System ID):</strong> {ctt.cdtr_agt_fin_instn_id_clrsysmmbid_clrsysid_cd}</p>
                  <p><strong>Creditor Agent (Member ID):</strong> {ctt.cdtr_agt_fin_instn_id_clrsysmmbid_mmbid}</p>
                </div>
              ))
            ) : (
              <p>No credit transfer transactions for this payment information block.</p>
            )}
          </div>
        ))
      ) : (
        <p>No payment information blocks found.</p>
      )}

      <h2>Audit Trail</h2>
      {payment.status_history.length > 0 ? (
        <table>
          <thead>
            <tr>
              <th>Timestamp</th>
              <th>Status</th>
              <th>Details</th>
            </tr>
          </thead>
          <tbody>
            {payment.status_history
              .sort((a, b) => new Date(a.changed_at) - new Date(b.changed_at)) // Sort by time
              .map((statusEntry) => (
                <tr key={statusEntry.id}>
                  <td>{new Date(statusEntry.changed_at).toLocaleString()}</td>
                  <td>{statusEntry.status}</td>
                  <td>{statusEntry.details || 'N/A'}</td>
                </tr>
              ))}
          </tbody>
        </table>
      ) : (
        <p>No audit trail entries for this payment.</p>
      )}

      <h2>Full XML Content</h2>
      <pre>{payment.xml_content}</pre>
    </div>
  );
};

export default PaymentDetailPage;
