// frontend/src/api.js
import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json", // Default for most requests
  },
});

export const uploadPayment = async (xmlContent: string) => {
  try {
    const response = await api.post("/payments/upload", xmlContent, {
      headers: {
        "Content-Type": "application/xml", // Specific for XML upload
      },
    });
    return response.data;
  } catch (error: any) {
    console.error(
      "Error uploading payment:",
      error.response?.data || error.message
    );
    throw error.response?.data || new Error("Failed to upload payment");
  }
};

export const getPayments = async () => {
  try {
    const response = await api.get("/payments", {
      headers: {
        accept: "application/json",
      },
    });
    return response.data;
  } catch (error: any) {
    console.error(
      "Error fetching payments:",
      error.response?.data || error.message
    );
    throw error.response?.data || new Error("Failed to fetch payments");
  }
};

export const getPaymentDetails = async (documentId: string) => {
  try {
    const response = await api.get(`/payments/${documentId}`);
    return response.data;
  } catch (error: any) {
    console.error(
      `Error fetching payment details for ${documentId}:`,
      error.response?.data || error.message
    );
    throw (
      error.response?.data ||
      new Error(`Failed to fetch payment details for ${documentId}`)
    );
  }
};

// Basic Rules API (for future use, if you add rules management UI)
export const getRules = async () => {
  try {
    const response = await api.get("/rules");
    return response.data;
  } catch (error: any) {
    console.error(
      "Error fetching rules:",
      error.response?.data || error.message
    );
    throw error.response?.data || new Error("Failed to fetch rules");
  }
};

export const createRule = async (ruleData: string) => {
  try {
    const response = await api.post("/rules", ruleData);
    return response.data;
  } catch (error: any) {
    console.error(
      "Error creating rule:",
      error.response?.data || error.message
    );
    throw error.response?.data || new Error("Failed to create rule");
  }
};

export const updateRule = async (ruleId: string, ruleData: string) => {
  try {
    const response = await api.put(`/rules/${ruleId}`, ruleData);
    return response.data;
  } catch (error: any) {
    console.error(
      `Error updating rule ${ruleId}:`,
      error.response?.data || error.message
    );
    throw error.response?.data || new Error(`Failed to update rule ${ruleId}`);
  }
};

export const deleteRule = async (ruleId: string) => {
  try {
    await api.delete(`/rules/${ruleId}`);
    return true;
  } catch (error: any) {
    console.error(
      `Error deleting rule ${ruleId}:`,
      error.response?.data || error.message
    );
    throw error.response?.data || new Error(`Failed to delete rule ${ruleId}`);
  }
};
