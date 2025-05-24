# backend/database.py
from sqlalchemy import (
    create_engine,
    Column,
    String,
    Integer,
    Numeric,
    Date,
    TIMESTAMP,
    Boolean,
    ForeignKey,
    TEXT,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.sql import func
import uuid

# Database connection details
DATABASE_URL = "postgresql+psycopg2://username:password@localhost/payments"

# Create a SQLAlchemy engine
engine = create_engine(DATABASE_URL)

# Create a declarative base
Base = declarative_base()

# Create a sessionmaker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class PaymentDocument(Base):
    __tablename__ = "payment_documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    msg_id = Column(String(35), nullable=False)
    cre_dt_tm = Column(TIMESTAMP(timezone=True), nullable=False)
    nb_of_txs = Column(Integer, nullable=False)
    ctrl_sum = Column(Numeric(18, 2), nullable=False)
    initg_pty_org_id_id = Column(String(35))
    xml_content = Column(TEXT, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), default=func.now())
    updated_at = Column(
        TIMESTAMP(timezone=True), default=func.now(), onupdate=func.now()
    )

    payment_info = relationship(
        "PaymentInformation", back_populates="document", cascade="all, delete-orphan"
    )
    status_history = relationship(
        "PaymentStatusHistory", back_populates="document", cascade="all, delete-orphan"
    )


class PaymentInformation(Base):
    __tablename__ = "payment_information"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(
        UUID(as_uuid=True),
        ForeignKey("payment_documents.id", ondelete="CASCADE"),
        nullable=False,
    )
    pmt_inf_id = Column(String(35), nullable=False)
    pmt_mtd = Column(String(3), nullable=False)
    reqd_exctn_dt = Column(Date, nullable=False)
    dbtr_nm = Column(String(140), nullable=False)
    dbtr_org_id_id = Column(String(35))
    dbtr_ctry_of_res = Column(String(2))
    dbtr_acct_iban = Column(String(34))
    dbtr_agt_fin_instn_id_bic = Column(String(11))
    created_at = Column(TIMESTAMP(timezone=True), default=func.now())
    updated_at = Column(
        TIMESTAMP(timezone=True), default=func.now(), onupdate=func.now()
    )

    document = relationship("PaymentDocument", back_populates="payment_info")
    credit_transfers = relationship(
        "CreditTransferTransaction",
        back_populates="payment_info",
        cascade="all, delete-orphan",
    )


class CreditTransferTransaction(Base):
    __tablename__ = "credit_transfer_transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    payment_info_id = Column(
        UUID(as_uuid=True),
        ForeignKey("payment_information.id", ondelete="CASCADE"),
        nullable=False,
    )
    pmt_id_instr_id = Column(String(35))
    pmt_id_end_to_end_id = Column(String(35), nullable=False)
    pmt_tp_inf_svc_lvl_cd = Column(String(4))
    pmt_tp_inf_ctgy_purp_cd = Column(String(4))
    instd_amt = Column(Numeric(18, 2), nullable=False)
    instd_amt_ccy = Column(String(3), nullable=False)
    cdtr_agt_fin_instn_id_clrsysmmbid_clrsysid_cd = Column(String(35))
    cdtr_agt_fin_instn_id_clrsysmmbid_mmbid = Column(String(35))
    cdtr_nm = Column(String(140), nullable=False)
    cdtr_acct_othr_id = Column(String(35))
    cdtr_acct_othr_schme_nm_cd = Column(String(4))
    created_at = Column(TIMESTAMP(timezone=True), default=func.now())
    updated_at = Column(
        TIMESTAMP(timezone=True), default=func.now(), onupdate=func.now()
    )

    payment_info = relationship("PaymentInformation", back_populates="credit_transfers")


class PaymentStatusHistory(Base):
    __tablename__ = "payment_status_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(
        UUID(as_uuid=True),
        ForeignKey("payment_documents.id", ondelete="CASCADE"),
        nullable=False,
    )
    status = Column(String(50), nullable=False)
    details = Column(TEXT)
    changed_at = Column(TIMESTAMP(timezone=True), default=func.now())

    document = relationship("PaymentDocument", back_populates="status_history")


class Rule(Base):
    __tablename__ = "rules"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    rule_name = Column(String(100), nullable=False, unique=True)
    description = Column(TEXT)
    field_to_check = Column(String(100), nullable=False)
    operator = Column(String(10), nullable=False)
    value_to_match = Column(TEXT, nullable=False)
    action_field = Column(String(100), nullable=False)
    action_value = Column(TEXT, nullable=False)
    is_active = Column(Boolean, default=True)
    priority = Column(Integer, default=1)
    created_at = Column(TIMESTAMP(timezone=True), default=func.now())
    updated_at = Column(
        TIMESTAMP(timezone=True), default=func.now(), onupdate=func.now()
    )


def create_db_tables():
    Base.metadata.create_all(bind=engine)


# Dependency to get a DB session


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
