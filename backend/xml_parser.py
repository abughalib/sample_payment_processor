# backend/xml_parser.py
from lxml import etree
import datetime
from decimal import Decimal

# Path to the XSD schema file (relative to this script)
XSD_SCHEMA_PATH = "pain.001.001.03.xsd"


def load_xsd_schema(xsd_path: str):
    """Loads an XML Schema Definition (XSD) from a given path."""
    try:
        xmlschema_doc = etree.parse(xsd_path)
        xmlschema = etree.XMLSchema(xmlschema_doc)
        return xmlschema
    except etree.XMLSyntaxError as e:
        raise ValueError(f"Error parsing XSD schema: {e}")
    except Exception as e:
        raise Exception(f"Could not load XSD schema from {xsd_path}: {e}")


# Load the schema once when the module is imported
try:
    PAIN_001_SCHEMA = load_xsd_schema(XSD_SCHEMA_PATH)
except (ValueError, Exception) as e:
    print(
        f"CRITICAL ERROR: Could not load XSD schema. XML validation will fail. {e}")
    # Set to None so app can still run, but validation will be skipped or raise errors
    PAIN_001_SCHEMA = None


def validate_xml(xml_content: str) -> bool:
    """Validates the given XML content against the pain.001.001.03 XSD schema."""
    if PAIN_001_SCHEMA is None:
        raise RuntimeError(
            "XSD schema not loaded. Cannot perform XML validation.")
    try:
        parser = etree.XMLParser(schema=PAIN_001_SCHEMA)
        etree.fromstring(xml_content.encode('utf-8'), parser)
        return True
    except etree.XMLSyntaxError as e:
        print(f"XML Validation Error: {e.error_log}")
        raise ValueError(f"XML validation failed: {e.error_log}")
    except Exception as e:
        raise Exception(
            f"An unexpected error occurred during XML validation: {e}")


def parse_pain_001_xml(xml_content: str) -> dict:
    """
    Parses a pain.001.001.03 XML message and extracts relevant data.
    Returns a dictionary structured for database insertion.
    """
    root = etree.fromstring(xml_content.encode('utf-8'))

    # Define XML namespaces
    ns = {
        'doc': 'urn:iso:std:iso:20022:tech:xsd:pain.001.001.03',
        'xsi': 'http://www.w3.org/2001/XMLSchema-instance'
    }

    data = {
        "payment_document": {},
        "payment_information": [],
        "credit_transfer_transactions": []
    }

    # Extract Group Header details
    grpHdr = root.find('doc:CstmrCdtTrfInitn/doc:GrpHdr', ns)
    if grpHdr is not None:
        data["payment_document"]["msg_id"] = grpHdr.find(
            'doc:MsgId', ns).text if grpHdr.find('doc:MsgId', ns) is not None else None
        data["payment_document"]["cre_dt_tm"] = datetime.datetime.fromisoformat(grpHdr.find(
            'doc:CreDtTm', ns).text) if grpHdr.find('doc:CreDtTm', ns) is not None else None
        data["payment_document"]["nb_of_txs"] = int(grpHdr.find(
            'doc:NbOfTxs', ns).text) if grpHdr.find('doc:NbOfTxs', ns) is not None else None
        data["payment_document"]["ctrl_sum"] = Decimal(grpHdr.find(
            'doc:CtrlSum', ns).text) if grpHdr.find('doc:CtrlSum', ns) is not None else None
        data["payment_document"]["initg_pty_org_id_id"] = grpHdr.find(
            'doc:InitgPty/doc:Id/doc:OrgId/doc:Othr/doc:Id', ns).text if grpHdr.find('doc:InitgPty/doc:Id/doc:OrgId/doc:Othr/doc:Id', ns) is not None else None
        # Store the full XML content
        data["payment_document"]["xml_content"] = xml_content

    # Extract Payment Information (PmtInf) blocks
    pmt_infs = root.findall('doc:CstmrCdtTrfInitn/doc:PmtInf', ns)
    for pmtInf in pmt_infs:
        pi_data = {}
        pi_data["pmt_inf_id"] = pmtInf.find('doc:PmtInfId', ns).text if pmtInf.find(
            'doc:PmtInfId', ns) is not None else None
        pi_data["pmt_mtd"] = pmtInf.find('doc:PmtMtd', ns).text if pmtInf.find(
            'doc:PmtMtd', ns) is not None else None
        pi_data["reqd_exctn_dt"] = datetime.date.fromisoformat(pmtInf.find(
            'doc:ReqdExctnDt', ns).text) if pmtInf.find('doc:ReqdExctnDt', ns) is not None else None

        dbtr = pmtInf.find('doc:Dbtr', ns)
        if dbtr is not None:
            pi_data["dbtr_nm"] = dbtr.find('doc:Nm', ns).text if dbtr.find(
                'doc:Nm', ns) is not None else None
            pi_data["dbtr_org_id_id"] = dbtr.find('doc:Id/doc:OrgId/doc:Othr/doc:Id', ns).text if dbtr.find(
                'doc:Id/doc:OrgId/doc:Othr/doc:Id', ns) is not None else None
            pi_data["dbtr_ctry_of_res"] = dbtr.find('doc:CtryOfRes', ns).text if dbtr.find(
                'doc:CtryOfRes', ns) is not None else None

        dbtrAcct = pmtInf.find('doc:DbtrAcct', ns)
        if dbtrAcct is not None:
            pi_data["dbtr_acct_iban"] = dbtrAcct.find(
                'doc:Id/doc:IBAN', ns).text if dbtrAcct.find('doc:Id/doc:IBAN', ns) is not None else None

        dbtrAgt = pmtInf.find('doc:DbtrAgt', ns)
        if dbtrAgt is not None:
            pi_data["dbtr_agt_fin_instn_id_bic"] = dbtrAgt.find(
                'doc:FinInstnId/doc:BIC', ns).text if dbtrAgt.find('doc:FinInstnId/doc:BIC', ns) is not None else None

        data["payment_information"].append(pi_data)

        # Extract Credit Transfer Transaction Information (CdtTrfTxInf) blocks for each PmtInf
        cdt_trf_tx_infs = pmtInf.findall('doc:CdtTrfTxInf', ns)
        for cdtTrfTxInf in cdt_trf_tx_infs:
            ctt_data = {}
            ctt_data["pmt_id_instr_id"] = cdtTrfTxInf.find(
                'doc:PmtId/doc:InstrId', ns).text if cdtTrfTxInf.find('doc:PmtId/doc:InstrId', ns) is not None else None
            ctt_data["pmt_id_end_to_end_id"] = cdtTrfTxInf.find(
                'doc:PmtId/doc:EndToEndId', ns).text if cdtTrfTxInf.find('doc:PmtId/doc:EndToEndId', ns) is not None else None

            pmtTpInf = cdtTrfTxInf.find('doc:PmtTpInf', ns)
            if pmtTpInf is not None:
                ctt_data["pmt_tp_inf_svc_lvl_cd"] = pmtTpInf.find(
                    'doc:SvcLvl/doc:Cd', ns).text if pmtTpInf.find('doc:SvcLvl/doc:Cd', ns) is not None else None
                ctt_data["pmt_tp_inf_ctgy_purp_cd"] = pmtTpInf.find(
                    'doc:CtgyPurp/doc:Cd', ns).text if pmtTpInf.find('doc:CtgyPurp/doc:Cd', ns) is not None else None

            instdAmt = cdtTrfTxInf.find('doc:Amt/doc:InstdAmt', ns)
            if instdAmt is not None:
                ctt_data["instd_amt"] = Decimal(
                    instdAmt.text) if instdAmt.text is not None else None
                ctt_data["instd_amt_ccy"] = instdAmt.get('Ccy')

            cdtrAgt = cdtTrfTxInf.find('doc:CdtrAgt', ns)
            if cdtrAgt is not None:
                ctt_data["cdtr_agt_fin_instn_id_clrsysmmbid_clrsysid_cd"] = cdtrAgt.find(
                    'doc:FinInstnId/doc:ClrSysMmbId/doc:ClrSysId/doc:Cd', ns).text if cdtrAgt.find('doc:FinInstnId/doc:ClrSysMmbId/doc:ClrSysId/doc:Cd', ns) is not None else None
                ctt_data["cdtr_agt_fin_instn_id_clrsysmmbid_mmbid"] = cdtrAgt.find(
                    'doc:FinInstnId/doc:ClrSysMmbId/doc:MmbId', ns).text if cdtrAgt.find('doc:FinInstnId/doc:ClrSysMmbId/doc:MmbId', ns) is not None else None

            cdtr = cdtTrfTxInf.find('doc:Cdtr', ns)
            if cdtr is not None:
                ctt_data["cdtr_nm"] = cdtr.find('doc:Nm', ns).text if cdtr.find(
                    'doc:Nm', ns) is not None else None

            cdtrAcct = cdtTrfTxInf.find('doc:CdtrAcct', ns)
            if cdtrAcct is not None:
                ctt_data["cdtr_acct_othr_id"] = cdtrAcct.find(
                    'doc:Id/doc:Othr/doc:Id', ns).text if cdtrAcct.find('doc:Id/doc:Othr/doc:Id', ns) is not None else None
                ctt_data["cdtr_acct_othr_schme_nm_cd"] = cdtrAcct.find(
                    'doc:Id/doc:Othr/doc:SchmeNm/doc:Cd', ns).text if cdtrAcct.find('doc:Id/doc:Othr/doc:SchmeNm/doc:Cd', ns) is not None else None

            data["credit_transfer_transactions"].append(ctt_data)

    return data
