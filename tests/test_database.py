import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# Add root folder to python path to import models
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.database.connection import Base
from backend.database.models import User, Role, Account, Transaction, Case, RiskPrediction, ShapExplanation, InvestigationEvent, AuditLog, Report
from backend.database.repositories import (
    AccountRepository,
    CaseRepository,
    RiskPredictionRepository,
    ShapExplanationRepository,
    InvestigationEventRepository,
    AuditLogRepository,
    ReportRepository
)

class TestMuleShieldDatabase(unittest.TestCase):
    def setUp(self):
        """
        Creates an isolated in-memory SQLite database instance for isolated unit tests.
        """
        self.engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.db = SessionLocal()
        Base.metadata.create_all(bind=self.engine)

    def tearDown(self):
        """
        Closes and drops the database tables.
        """
        self.db.close()
        Base.metadata.drop_all(bind=self.engine)

    def test_database_connection(self):
        """
        Tests database connection validation.
        """
        connection = self.engine.connect()
        self.assertFalse(connection.closed)
        connection.close()

    def test_user_and_role_crud(self):
        """
        Tests CRUD operations for Users and Roles.
        """
        # Create user
        new_user = User(email="analyst_test@muleshield.psb", password_hash="hashed_pw_123", role="ANALYST")
        self.db.add(new_user)
        self.db.commit()

        # Read user
        db_user = self.db.query(User).filter(User.email == "analyst_test@muleshield.psb").first()
        self.assertIsNotNone(db_user)
        self.assertEqual(db_user.role, "ANALYST")

        # Update role
        db_user.role = "SENIOR_ANALYST"
        self.db.commit()
        
        # Verify update
        updated_user = self.db.query(User).filter(User.email == "analyst_test@muleshield.psb").first()
        self.assertEqual(updated_user.role, "SENIOR_ANALYST")

        # Delete user
        self.db.delete(updated_user)
        self.db.commit()
        deleted_user = self.db.query(User).filter(User.email == "analyst_test@muleshield.psb").first()
        self.assertIsNone(deleted_user)

    def test_account_and_case_persistence(self):
        """
        Tests Account and Case model repository persistence.
        """
        account_id = 12345
        attributes = {"F994": 15.2, "F3598": 1.2}
        
        # Create Account
        account = AccountRepository.create(self.db, account_id=account_id, attributes=attributes)
        self.assertIsNotNone(account)
        self.assertEqual(account.account_id, account_id)
        
        # Create Case
        case_data = {
            "account_id": account_id,
            "risk_score": 0.9924,
            "tier": "Critical",
            "status": "NEW",
            "assigned_analyst": "Unassigned",
            "action": "Immediate freeze+STR",
            "notes": []
        }
        case = CaseRepository.create(self.db, case_data)
        self.assertIsNotNone(case)
        self.assertEqual(case.risk_score, 0.9924)
        self.assertEqual(case.status, "NEW")

        # Read Case
        db_case = CaseRepository.get_by_account_id(self.db, account_id)
        self.assertIsNotNone(db_case)
        
        # Update Case Status
        CaseRepository.update_status(self.db, account_id, "UNDER REVIEW", "Analyst-10")
        updated_case = CaseRepository.get_by_account_id(self.db, account_id)
        self.assertEqual(updated_case.status, "UNDER REVIEW")
        self.assertEqual(updated_case.assigned_analyst, "Analyst-10")

        # Add note entry
        note_dict = {
            "timestamp": "2026-08-23 15:00:00 UTC",
            "analyst": "Analyst-10",
            "text": "Reviewing ledger spikes."
        }
        CaseRepository.add_note(self.db, account_id, note_dict)
        c_with_note = CaseRepository.get_by_account_id(self.db, account_id)
        self.assertEqual(len(c_with_note.notes), 1)
        self.assertEqual(c_with_note.notes[0]["text"], "Reviewing ledger spikes.")

    def test_transaction_persistence(self):
        """
        Tests ledger transaction records persistence.
        """
        account_id = 99999
        AccountRepository.create(self.db, account_id=account_id, attributes={})

        transaction = Transaction(
            account_id=account_id,
            amount=50000.0,
            transaction_type="UPI_INFLOW",
            timestamp=datetime.utcnow()
        )
        self.db.add(transaction)
        self.db.commit()

        db_tx = self.db.query(Transaction).filter(Transaction.account_id == account_id).first()
        self.assertIsNotNone(db_tx)
        self.assertEqual(db_tx.amount, 50000.0)

    def test_prediction_and_shap_persistence(self):
        """
        Tests inference history and TreeSHAP attribution persistence.
        """
        account_id = 88888
        AccountRepository.create(self.db, account_id=account_id, attributes={})

        # Save Prediction
        pred_data = {
            "account_id": account_id,
            "risk_score": 0.8845,
            "tier": "High",
            "action": "Analyst investigation",
            "exceeds_threshold": False
        }
        pred = RiskPredictionRepository.create(self.db, pred_data)
        self.assertIsNotNone(pred)
        self.assertEqual(pred.tier, "High")

        # Read Prediction
        db_pred = RiskPredictionRepository.get_by_account_id(self.db, account_id)
        self.assertEqual(db_pred.risk_score, 0.8845)

        # Save SHAP
        shap = ShapExplanationRepository.create(self.db, account_id=account_id, features=["F994", "F3598"])
        self.assertIsNotNone(shap)
        self.assertEqual(len(shap.features), 2)

        # Read SHAP
        db_shap = ShapExplanationRepository.get_by_account_id(self.db, account_id)
        self.assertIn("F994", db_shap.features)

    def test_audit_logs_persistence(self):
        """
        Tests operations audit logs persistence.
        """
        log_data = {
            "timestamp": "2026-08-23 12:00:00 UTC",
            "actor": "System",
            "action": "Case Investigation Closed",
            "case_id": "9003",
            "status": "SUCCESS"
        }
        log = AuditLogRepository.create(self.db, log_data)
        self.assertIsNotNone(log)
        self.assertEqual(log.actor, "System")

        # Read Audit Logs
        logs = AuditLogRepository.get_all(self.db)
        self.assertTrue(len(logs) > 0)
        self.assertEqual(logs[0].action, "Case Investigation Closed")

if __name__ == "__main__":
    unittest.main()
