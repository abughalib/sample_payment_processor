-- Table for the main payment document
CREATE TABLE IF NOT EXISTS payment_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    msg_id VARCHAR(35) NOT NULL, -- Corresponds to /Document/CstmrCdtTrfInitn/GrpHdr/MsgId
    cre_dt_tm TIMESTAMP WITH TIME ZONE NOT NULL, -- Corresponds to /Document/CstmrCdtTrfInitn/GrpHdr/CreDtTm
    nb_of_txs INTEGER NOT NULL, -- Corresponds to /Document/CstmrCdtTrfInitn/GrpHdr/NbOfTxs
    ctrl_sum NUMERIC(18, 2) NOT NULL, -- Corresponds to /Document/CstmrCdtTrfInitn/GrpHdr/CtrlSum
    initg_pty_org_id_id VARCHAR(35), -- Corresponds to /Document/CstmrCdtTrfInitn/GrpHdr/InitgPty/Id/OrgId/Othr/Id
    xml_content TEXT NOT NULL, -- To store the full XML for auditing/reprocessing if needed
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Table for Payment Information blocks (PmtInf)
-- A single pain.001 can contain multiple PmtInf blocks
CREATE TABLE IF NOT EXISTS payment_information (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL REFERENCES payment_documents(id) ON DELETE CASCADE,
    pmt_inf_id VARCHAR(35) NOT NULL, -- Corresponds to /Document/CstmrCdtTrfInitn/PmtInf/PmtInfId
    pmt_mtd VARCHAR(3) NOT NULL, -- Corresponds to /Document/CstmrCdtTrfInitn/PmtInf/PmtMtd
    reqd_exctn_dt DATE NOT NULL, -- Corresponds to /Document/CstmrCdtTrfInitn/PmtInf/ReqdExctnDt

    -- Debtor information
    dbtr_nm VARCHAR(140) NOT NULL, -- Corresponds to /Document/CstmrCdtTrfInitn/PmtInf/Dbtr/Nm
    dbtr_org_id_id VARCHAR(35), -- Corresponds to /Document/CstmrCdtTrfInitn/PmtInf/Dbtr/Id/OrgId/Othr/Id
    dbtr_ctry_of_res CHAR(2), -- Corresponds to /Document/CstmrCdtTrfInitn/PmtInf/Dbtr/CtryOfRes

    -- Debtor Account
    dbtr_acct_iban VARCHAR(34), -- Corresponds to /Document/CstmrCdtTrfInitn/PmtInf/DbtrAcct/Id/IBAN

    -- Debtor Agent (Bank)
    dbtr_agt_fin_instn_id_bic VARCHAR(11), -- Corresponds to /Document/CstmrCdtTrfInitn/PmtInf/DbtrAgt/FinInstnId/BIC

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Table for Credit Transfer Transaction Information blocks (CdtTrfTxInf)
-- A single PmtInf can contain multiple CdtTrfTxInf blocks
CREATE TABLE IF NOT EXISTS credit_transfer_transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    payment_info_id UUID NOT NULL REFERENCES payment_information(id) ON DELETE CASCADE,

    -- Payment Identification
    pmt_id_instr_id VARCHAR(35), -- Corresponds to /Document/CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/PmtId/InstrId
    pmt_id_end_to_end_id VARCHAR(35) NOT NULL, -- Corresponds to /Document/CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/PmtId/EndToEndId

    -- Payment Type Information
    pmt_tp_inf_svc_lvl_cd VARCHAR(4), -- Corresponds to /Document/CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/PmtTpInf/SvcLvl/Cd
    pmt_tp_inf_ctgy_purp_cd VARCHAR(4), -- Corresponds to /Document/CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/PmtTpInf/CtgyPurp/Cd

    -- Amount
    instd_amt NUMERIC(18, 2) NOT NULL, -- Corresponds to /Document/CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/Amt/InstdAmt
    instd_amt_ccy CHAR(3) NOT NULL, -- Corresponds to /Document/CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/Amt/InstdAmt @Ccy

    -- Creditor Agent (Bank)
    cdtr_agt_fin_instn_id_clrsysmmbid_clrsysid_cd VARCHAR(35), -- Corresponds to /Document/CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/CdtrAgt/FinInstnId/ClrSysMmbId/ClrSysId/Cd
    cdtr_agt_fin_instn_id_clrsysmmbid_mmbid VARCHAR(35), -- Corresponds to /Document/CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/CdtrAgt/FinInstnId/ClrSysMmbId/MmbId

    -- Creditor
    cdtr_nm VARCHAR(140) NOT NULL, -- Corresponds to /Document/CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/Cdtr/Nm

    -- Creditor Account
    cdtr_acct_othr_id VARCHAR(35), -- Corresponds to /Document/CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/CdtrAcct/Id/Othr/Id
    cdtr_acct_othr_schme_nm_cd VARCHAR(4), -- Corresponds to /Document/CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/CdtrAcct/Id/Othr/SchmeNm/Cd

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Table for Payment Status (Audit Trail)
-- Each row represents a state change for a payment document
CREATE TABLE IF NOT EXISTS payment_status_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL REFERENCES payment_documents(id) ON DELETE CASCADE,
    status VARCHAR(50) NOT NULL, -- e.g., 'RECEIVED', 'PARSED', 'VALIDATED', 'RULE_APPLIED', 'FAILED'
    details TEXT, -- Additional details about the status, e.g., error messages
    changed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    -- Add 'changed_by' if user management is introduced later
);

-- Table for Rules Engine
CREATE TABLE IF NOT EXISTS rules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    rule_name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    field_to_check VARCHAR(100) NOT NULL, -- e.g., 'instd_amt', 'cdtr_nm', 'pmt_id_end_to_end_id'
    operator VARCHAR(10) NOT NULL, -- e.g., '=', '>', '<', 'LIKE', 'IN'
    value_to_match TEXT NOT NULL, -- The value to compare against (e.g., '100.00', 'TESTCOMPANY', 'SEK')
    action_field VARCHAR(100) NOT NULL, -- The field to change (e.g., 'instd_amt', 'cdtr_nm')
    action_value TEXT NOT NULL, -- The new value for the action_field
    is_active BOOLEAN DEFAULT TRUE,
    priority INTEGER DEFAULT 1, -- For ordering rule application
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexing for performance
CREATE INDEX IF NOT EXISTS idx_payment_documents_msg_id ON payment_documents (msg_id);
CREATE INDEX IF NOT EXISTS idx_payment_documents_cre_dt_tm ON payment_documents (cre_dt_tm);
CREATE INDEX IF NOT EXISTS idx_payment_info_pmt_inf_id ON payment_information (pmt_inf_id);
CREATE INDEX IF NOT EXISTS idx_payment_info_reqd_exctn_dt ON payment_information (reqd_exctn_dt);
CREATE INDEX IF NOT EXISTS idx_transactions_end_to_end_id ON credit_transfer_transactions (pmt_id_end_to_end_id);
CREATE INDEX IF NOT EXISTS idx_transactions_instd_amt_ccy ON credit_transfer_transactions (instd_amt_ccy);
CREATE INDEX IF NOT EXISTS idx_status_history_document_id ON payment_status_history (document_id);
CREATE INDEX IF NOT EXISTS idx_rules_field_to_check ON rules (field_to_check);
CREATE INDEX IF NOT EXISTS idx_rules_action_field ON rules (action_field);