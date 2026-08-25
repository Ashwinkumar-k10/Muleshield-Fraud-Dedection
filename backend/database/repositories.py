from sqlalchemy.orm import Session
from backend.database.models import User, Role, Account, Transaction, Case, RiskPrediction, ShapExplanation, InvestigationEvent, AuditLog, Report
from datetime import datetime

class AccountRepository:
    @staticmethod
    def get_by_id(db: Session, account_id: int):
        return db.query(Account).filter(Account.account_id == account_id).first()

    @staticmethod
    def create(db: Session, account_id: int, attributes: dict):
        account = Account(account_id=account_id, attributes=attributes)
        db.add(account)
        db.commit()
        db.refresh(account)
        return account

class CaseRepository:
    @staticmethod
    def get_all(db: Session):
        return db.query(Case).all()

    @staticmethod
    def get_by_account_id(db: Session, account_id: int):
        return db.query(Case).filter(Case.account_id == account_id).first()

    @staticmethod
    def create(db: Session, case_data: dict):
        new_case = Case(
            account_id=case_data["account_id"],
            risk_score=case_data["risk_score"],
            tier=case_data["tier"],
            status=case_data.get("status", "NEW"),
            assigned_analyst=case_data.get("assigned_analyst", "Unassigned"),
            created_at=datetime.utcnow(),
            action=case_data["action"],
            notes=case_data.get("notes", [])
        )
        db.add(new_case)
        db.commit()
        db.refresh(new_case)
        return new_case

    @staticmethod
    def update_status(db: Session, account_id: int, status: str, analyst: str):
        case = db.query(Case).filter(Case.account_id == account_id).first()
        if case:
            case.status = status.upper()
            case.assigned_analyst = analyst
            db.commit()
            db.refresh(case)
        return case

    @staticmethod
    def add_note(db: Session, account_id: int, note: dict):
        case = db.query(Case).filter(Case.account_id == account_id).first()
        if case:
            notes_list = list(case.notes or [])
            notes_list.append(note)
            case.notes = notes_list
            db.commit()
            db.refresh(case)
        return case

class RiskPredictionRepository:
    @staticmethod
    def get_by_account_id(db: Session, account_id: int):
        return db.query(RiskPrediction).filter(RiskPrediction.account_id == account_id).first()

    @staticmethod
    def create(db: Session, pred_data: dict):
        pred = RiskPrediction(
            account_id=pred_data["account_id"],
            risk_score=pred_data["risk_score"],
            tier=pred_data["tier"],
            action=pred_data["action"],
            exceeds_threshold=pred_data.get("exceeds_threshold", False),
            created_at=datetime.utcnow()
        )
        db.add(pred)
        db.commit()
        db.refresh(pred)
        return pred

class ShapExplanationRepository:
    @staticmethod
    def get_by_account_id(db: Session, account_id: int):
        return db.query(ShapExplanation).filter(ShapExplanation.account_id == account_id).first()

    @staticmethod
    def create(db: Session, account_id: int, features: list):
        shap = ShapExplanation(account_id=account_id, features=features, created_at=datetime.utcnow())
        db.add(shap)
        db.commit()
        db.refresh(shap)
        return shap

class InvestigationEventRepository:
    @staticmethod
    def get_by_account_id(db: Session, account_id: int):
        return db.query(InvestigationEvent).filter(InvestigationEvent.account_id == account_id).order_by(InvestigationEvent.timestamp.asc()).all()

    @staticmethod
    def create(db: Session, account_id: int, event_name: str, detail: str, timestamp_str=None):
        timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S UTC") if timestamp_str else datetime.utcnow()
        event = InvestigationEvent(
            account_id=account_id,
            timestamp=timestamp,
            event=event_name,
            detail=detail
        )
        db.add(event)
        db.commit()
        db.refresh(event)
        return event

class AuditLogRepository:
    @staticmethod
    def get_all(db: Session):
        return db.query(AuditLog).order_by(AuditLog.timestamp.desc()).all()

    @staticmethod
    def create(db: Session, log_data: dict):
        timestamp = datetime.strptime(log_data["timestamp"], "%Y-%m-%d %H:%M:%S UTC") if "timestamp" in log_data else datetime.utcnow()
        log = AuditLog(
            timestamp=timestamp,
            actor=log_data["actor"],
            action=log_data["action"],
            case_id=str(log_data["case_id"]),
            status=log_data["status"]
        )
        db.add(log)
        db.commit()
        db.refresh(log)
        return log

class ReportRepository:
    @staticmethod
    def get_by_account_id(db: Session, account_id: int):
        return db.query(Report).filter(Report.account_id == account_id).all()

    @staticmethod
    def create(db: Session, report_data: dict):
        report = Report(
            account_id=report_data["account_id"],
            report_type=report_data["report_type"],
            content=report_data["content"],
            filepath=report_data.get("filepath"),
            created_at=datetime.utcnow()
        )
        db.add(report)
        db.commit()
        db.refresh(report)
        return report

class TransactionRepository:
    @staticmethod
    def get_all(db: Session):
        return db.query(Transaction).all()

    @staticmethod
    def get_by_account_id(db: Session, account_id: int):
        from sqlalchemy import or_
        return db.query(Transaction).filter(or_(Transaction.source_account_id == account_id, Transaction.destination_account_id == account_id)).all()

    @staticmethod
    def create(db: Session, source_id: int, dest_id: int, amount: float, tx_type: str, timestamp=None):
        tx = Transaction(
            source_account_id=source_id,
            destination_account_id=dest_id,
            amount=amount,
            transaction_type=tx_type,
            timestamp=timestamp or datetime.utcnow()
        )
        db.add(tx)
        db.commit()
        db.refresh(tx)
        return tx
