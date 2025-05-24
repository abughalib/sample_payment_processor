// frontend/src/pages/CreatePaymentPage.jsx
import React, { useState } from "react";
import { uploadPayment } from "../api";

const CreatePaymentPage = () => {
  const [xmlContent, setXmlContent] = useState("");
  const [message, setMessage] = useState<any>(null); // { type: 'success' | 'error', text: '' }
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: any) => {
    e.preventDefault();
    setMessage(null);
    setLoading(true);

    try {
      const response = await uploadPayment(xmlContent);
      setMessage({
        type: "success",
        text: `Payment uploaded successfully! Document ID: ${response.document_id}`,
      });
      setXmlContent(""); // Clear the textarea on success
    } catch (error: any) {
      const errorMessage =
        error.detail || error.message || "An unexpected error occurred.";
      setMessage({
        type: "error",
        text: `Failed to upload payment: ${errorMessage}`,
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <h1>Create New Payment</h1>
      <p>Paste your ISO 20022 `pain.001` XML content below and submit.</p>
      <form onSubmit={handleSubmit}>
        <textarea
          value={xmlContent}
          onChange={(e) => setXmlContent(e.target.value)}
          placeholder={`Paste your pain.001.001.03 XML here...\n\nExample:\n<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pain.001.001.03" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">\n  <CstmrCdtTrfInitn>\n    <GrpHdr>\n      <MsgId>...</MsgId>\n      ...\n    </GrpHdr>\n    ...\n  </CstmrCdtTrfInitn>\n</Document>`}
          required
        ></textarea>
        <button type="submit" disabled={loading}>
          {loading ? "Submitting..." : "Submit Payment"}
        </button>
      </form>

      {message && (
        <div className={`message ${message.type}`}>{message.text}</div>
      )}
    </div>
  );
};

export default CreatePaymentPage;
