// frontend/src/pages/RulesManagementPage.jsx
import React, { useState, useEffect } from "react";
import { getRules, createRule } from "../api"; // Import createRule

const RulesManagementPage = () => {
  const [rules, setRules] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [message, setMessage] = useState(null); // For success/error messages after rule creation

  // State for the new rule form
  const [newRule, setNewRule] = useState({
    rule_name: "",
    description: "",
    field_to_check: "",
    operator: "=", // Default operator
    value_to_match: "",
    action_field: "",
    action_value: "",
    is_active: true,
    priority: 1,
  });

  const fetchRules = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getRules();
      setRules(data);
    } catch (err) {
      setError(err.detail || err.message || "Failed to fetch rules.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRules();
  }, []);

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setNewRule((prevRule) => ({
      ...prevRule,
      [name]: type === "checkbox" ? checked : value,
    }));
  };

  const handleCreateRule = async (e) => {
    e.preventDefault();
    setMessage(null);
    try {
      await createRule(newRule);
      setMessage({ type: "success", text: "Rule created successfully!" });
      setNewRule({
        // Reset form
        rule_name: "",
        description: "",
        field_to_check: "",
        operator: "=",
        value_to_match: "",
        action_field: "",
        action_value: "",
        is_active: true,
        priority: 1,
      });
      fetchRules(); // Refresh the list of rules
    } catch (err) {
      const errorMessage =
        err.detail || err.message || "Failed to create rule.";
      setMessage({
        type: "error",
        text: `Error creating rule: ${errorMessage}`,
      });
    }
  };

  if (loading) {
    return <div className="container">Loading rules...</div>;
  }

  if (error) {
    return <div className="container message error">Error: {error}</div>;
  }

  return (
    <div className="container">
      <h1>Rules Management</h1>

      <h2>Add New Rule</h2>
      <form
        onSubmit={handleCreateRule}
        style={{
          marginBottom: "2rem",
          display: "grid",
          gridTemplateColumns: "1fr 1fr",
          gap: "1rem",
        }}
      >
        <div>
          <label>Rule Name:</label>
          <input
            type="text"
            name="rule_name"
            value={newRule.rule_name}
            onChange={handleInputChange}
            required
          />
        </div>
        <div>
          <label>Description:</label>
          <input
            type="text"
            name="description"
            value={newRule.description}
            onChange={handleInputChange}
          />
        </div>
        <div>
          <label>Field to Check:</label>
          <input
            type="text"
            name="field_to_check"
            value={newRule.field_to_check}
            onChange={handleInputChange}
            required
          />
        </div>
        <div>
          <label>Operator:</label>
          <select
            name="operator"
            value={newRule.operator}
            onChange={handleInputChange}
            required
          >
            <option value="=">=</option>
            <option value=">">&gt;</option>
            <option value="<">&lt;</option>
            <option value="LIKE">LIKE</option>
            {/* Add more operators as supported by your backend logic */}
          </select>
        </div>
        <div>
          <label>Value to Match:</label>
          <input
            type="text"
            name="value_to_match"
            value={newRule.value_to_match}
            onChange={handleInputChange}
            required
          />
        </div>
        <div>
          <label>Action Field:</label>
          <input
            type="text"
            name="action_field"
            value={newRule.action_field}
            onChange={handleInputChange}
            required
          />
        </div>
        <div>
          <label>Action Value:</label>
          <input
            type="text"
            name="action_value"
            value={newRule.action_value}
            onChange={handleInputChange}
            required
          />
        </div>
        <div>
          <label>Is Active:</label>
          <input
            type="checkbox"
            name="is_active"
            checked={newRule.is_active}
            onChange={handleInputChange}
          />
        </div>
        <div>
          <label>Priority:</label>
          <input
            type="number"
            name="priority"
            value={newRule.priority}
            onChange={handleInputChange}
            required
          />
        </div>
        <div style={{ gridColumn: "span 2" }}>
          <button type="submit">Create Rule</button>
        </div>
      </form>

      {message && (
        <div className={`message ${message.type}`}>{message.text}</div>
      )}

      <h2>Existing Rules</h2>
      {rules.length === 0 ? (
        <p>No rules defined yet.</p>
      ) : (
        <table>
          <thead>
            <tr>
              <th>Name</th>
              <th>Description</th>
              <th>Condition</th>
              <th>Action</th>
              <th>Active</th>
              <th>Priority</th>
              <th>Created At</th>
            </tr>
          </thead>
          <tbody>
            {rules.map((rule) => (
              <tr key={rule.id}>
                <td>{rule.rule_name}</td>
                <td>{rule.description}</td>
                <td>
                  {rule.field_to_check} {rule.operator} "{rule.value_to_match}"
                </td>
                <td>
                  Set {rule.action_field} to "{rule.action_value}"
                </td>
                <td>{rule.is_active ? "Yes" : "No"}</td>
                <td>{rule.priority}</td>
                <td>{new Date(rule.created_at).toLocaleString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
};

export default RulesManagementPage;
