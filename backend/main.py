# backend/main.py
from decimal import Decimal
from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import Dict, Any
import logging

from init_db import create_db_tables


from database import (
    PaymentDocument,
    PaymentInformation,
    CreditTransferTransaction,
    PaymentStatusHistory,
    Rule,
    get_db,
)
from xml_parser import validate_xml, parse_pain_001_xml

# Initialize FastAPI app
app = FastAPI(title="ISO Payment Engine Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(level=logging.INFO, filename="trace.log")
logger = logging.getLogger(__name__)


# --- Database Initialization ---
@app.on_event("startup")
async def startup_event():
    logger.info("Creating database tables if they don't exist...")
    create_db_tables()
    logger.info("Database tables checked/created.")


def log_status(db: Session, document_id: str, status: str, details: str = None):
    """Logs a status change for a payment document."""
    try:
        new_status = PaymentStatusHistory(
            document_id=document_id, status=status, details=details
        )
        db.add(new_status)
        db.commit()
        db.refresh(new_status)
        logger.info(
            f"Document {document_id}: Status changed to {status}. Details: {details}"
        )
    except Exception as e:
        logger.error(
            f"Failed to log status for document {document_id}: {status}. Error: {e}"
        )
        db.rollback()


# --- Rules Application (Placeholder - will expand later) ---
def apply_rules_to_payment(db: Session, payment_doc_id: str):
    """
    Fetches active rules and applies them to the given payment document and its
    associated transactions. Logs changes in the audit trail.
    """
    logger.info(f"Applying rules for payment document ID: {payment_doc_id}")
    rules = db.query(Rule).filter(Rule.is_active == True).order_by(Rule.priority).all()

    # Fetch the entire payment document structure for rule application
    payment_document = (
        db.query(PaymentDocument).filter(PaymentDocument.id == payment_doc_id).first()
    )
    if not payment_document:
        logger.warning(
            f"Payment document {payment_doc_id} not found for rule application."
        )
        return

    # Load related data eagerly for easier access
    db.refresh(payment_document)

    changes_made = []

    for rule in rules:
        # Apply rules to CreditTransferTransactions
        for payment_info in payment_document.payment_info:
            for transaction in payment_info.credit_transfers:
                # Dynamically access the field to check
                field_value = getattr(transaction, rule.field_to_check, None)
                if field_value is not None:
                    # Check the condition based on the operator
                    condition_met = False
                    if rule.operator == "=" and str(field_value) == rule.value_to_match:
                        condition_met = True
                    elif rule.operator == ">" and Decimal(field_value) > Decimal(
                        rule.value_to_match
                    ):
                        condition_met = True
                    elif rule.operator == "<" and Decimal(field_value) < Decimal(
                        rule.value_to_match
                    ):
                        condition_met = True
                    elif rule.operator == "LIKE" and rule.value_to_match in str(
                        field_value
                    ):
                        condition_met = True

                    if condition_met:
                        # Apply the action
                        original_value = getattr(transaction, rule.action_field, None)
                        setattr(
                            transaction, rule.action_field, Decimal(rule.action_value)
                        )
                        db.add(transaction)  # Stage the change
                        changes_made.append(
                            f"Transaction {transaction.id}: Changed {rule.action_field} from {original_value} to {rule.action_value}"
                        )

    if changes_made:
        try:
            db.commit()
            log_status(db, payment_doc_id, "RULES_APPLIED", "\n".join(changes_made))
        except Exception as e:
            db.rollback()
            log_status(
                db,
                payment_doc_id,
                "RULE_APPLICATION_FAILED",
                f"Error applying rules: {e}",
            )
            logger.error(f"Error applying rules for {payment_doc_id}: {e}")
    else:
        log_status(
            db,
            payment_doc_id,
            "RULES_CHECKED",
            "No active rules applied or no conditions met.",
        )

    logger.info(f"Finished applying rules for payment document ID: {payment_doc_id}")


# --- API Endpoints ---


@app.post("/payments/upload", status_code=status.HTTP_201_CREATED)
async def upload_payment(request: Request, db: Session = Depends(get_db)):
    """
    Receives an ISO 20022 pain.001.001.03 XML message, validates it,
    parses its content, and stores it in the database.
    """
    logger.info("Received request to upload payment.")
    xml_content = await request.body()
    xml_content_str = xml_content.decode("utf-8")

    payment_doc_id = None  # Initialize to None for error handling

    try:
        # 1. XML Validation
        logger.info("Attempting XML validation...")
        validate_xml(xml_content_str)
        logger.info("XML validation successful.")

        # 2. Parse XML
        logger.info("Parsing XML content...")
        parsed_data = parse_pain_001_xml(xml_content_str)
        logger.info("XML parsing successful.")

        # 3. Store in Database
        logger.info("Storing parsed data in database...")
        payment_doc_data = parsed_data["payment_document"]
        payment_doc_data["xml_content"] = xml_content_str  # Ensure full XML is stored

        db_payment_doc = PaymentDocument(**payment_doc_data)
        db.add(db_payment_doc)
        db.flush()  # Flush to get the ID for related objects
        payment_doc_id = db_payment_doc.id  # Get the generated UUID

        log_status(
            db, payment_doc_id, "RECEIVED", "Payment XML received and validated."
        )
        log_status(db, payment_doc_id, "PARSED", "XML content successfully parsed.")

        for pi_data in parsed_data["payment_information"]:
            db_payment_info = PaymentInformation(**pi_data, document_id=payment_doc_id)
            db.add(db_payment_info)
            db.flush()  # Flush to get the ID for related objects

            # Link credit transfer transactions to the current payment_info
            for ctt_data in parsed_data[
                "credit_transfer_transactions"
            ]:  # This logic assumes 1-to-1 or common CTTs.
                # A more robust parser would link CTTs directly to their parent PmtInf during parsing.
                # For now, it will attach *all* CTTs to *each* PmtInf.
                # We'll refine this in the React part by making sure the parsing is accurate.
                db_credit_transfer = CreditTransferTransaction(
                    **ctt_data, payment_info_id=db_payment_info.id
                )
                db.add(db_credit_transfer)
        db.commit()
        db.refresh(db_payment_doc)  # Refresh to load relationships after commit
        log_status(
            db,
            payment_doc_id,
            "STORED",
            "Payment data successfully stored in database.",
        )

        # 4. Apply Rules (synchronously for demo, consider async for production)
        apply_rules_to_payment(db, payment_doc_id)

        return {
            "message": "Payment processed successfully",
            "document_id": payment_doc_id,
        }

    except ValueError as e:
        logger.error(f"Payment processing failed due to validation error: {e}")
        if payment_doc_id:
            log_status(db, payment_doc_id, "VALIDATION_FAILED", str(e))
            db.rollback()  # Rollback any partial inserts if validation failed mid-way
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"XML validation failed: {e}",
        )
    except IntegrityError as e:
        logger.error(f"Database integrity error: {e}")
        if payment_doc_id:
            log_status(
                db, payment_doc_id, "DB_ERROR", f"Database integrity error: {e.args[0]}"
            )
            db.rollback()
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Database error: {e.args[0]}",
        )
    except Exception as e:
        logger.exception("An unexpected error occurred during payment processing.")
        if payment_doc_id:
            log_status(
                db, payment_doc_id, "PROCESSING_FAILED", f"Unexpected error: {e}"
            )
            db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {e}",
        )


@app.get("/payments")
def get_all_payments(db: Session = Depends(get_db)):
    """Retrieves a list of all payment documents."""
    payments = db.query(PaymentDocument).all()
    # Convert SQLAlchemy objects to dicts for Pydantic serialization (FastAPI handles this well)
    return payments


@app.get("/payments/{document_id}")
def get_payment_details(document_id: str, db: Session = Depends(get_db)):
    """Retrieves detailed information for a specific payment document, including related transactions and audit trail."""
    payment_doc = (
        db.query(PaymentDocument).filter(PaymentDocument.id == document_id).first()
    )
    if not payment_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Payment document not found"
        )

    # Eagerly load related data for the response
    payment_info_list = (
        db.query(PaymentInformation)
        .filter(PaymentInformation.document_id == document_id)
        .all()
    )
    for pi in payment_info_list:
        pi.credit_transfers  # Access to load them

    status_history_list = (
        db.query(PaymentStatusHistory)
        .filter(PaymentStatusHistory.document_id == document_id)
        .order_by(PaymentStatusHistory.changed_at)
        .all()
    )

    # Convert to dictionary for a more structured JSON response
    response_data = {
        **payment_doc.__dict__,
        "payment_info": [
            {
                **pi.__dict__,
                "credit_transfers": [ctt.__dict__ for ctt in pi.credit_transfers],
            }
            for pi in payment_info_list
        ],
        "status_history": [sh.__dict__ for sh in status_history_list],
    }
    # Remove _sa_instance_state from dicts for cleaner output
    for key in ["_sa_instance_state", "document"]:
        response_data.pop(key, None)
    for pi in response_data["payment_info"]:
        pi.pop("_sa_instance_state", None)
        pi.pop("document", None)  # Remove backref if it exists
        for ctt in pi["credit_transfers"]:
            ctt.pop("_sa_instance_state", None)
            ctt.pop("payment_info", None)
    for sh in response_data["status_history"]:
        sh.pop("_sa_instance_state", None)
        sh.pop("document", None)

    return response_data


@app.get("/rules")
def get_all_rules(db: Session = Depends(get_db)):
    """Retrieves all defined rules."""
    rules = db.query(Rule).all()
    return rules


@app.post("/rules", status_code=status.HTTP_201_CREATED)
def create_rule(rule_data: Dict[str, Any], db: Session = Depends(get_db)):
    """Creates a new rule."""
    try:
        new_rule = Rule(**rule_data)
        db.add(new_rule)
        db.commit()
        db.refresh(new_rule)
        return new_rule
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Rule with this name already exists.",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create rule: {e}",
        )


@app.put("/rules/{rule_id}")
def update_rule(rule_id: str, rule_data: Dict[str, Any], db: Session = Depends(get_db)):
    """Updates an existing rule."""
    rule = db.query(Rule).filter(Rule.id == rule_id).first()
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Rule not found"
        )
    for key, value in rule_data.items():
        setattr(rule, key, value)
    db.commit()
    db.refresh(rule)
    return rule


@app.delete("/rules/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_rule(rule_id: str, db: Session = Depends(get_db)):
    """Deletes a rule."""
    rule = db.query(Rule).filter(Rule.id == rule_id).first()
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Rule not found"
        )
    db.delete(rule)
    db.commit()
    return
