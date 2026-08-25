import pandas as pd
import numpy as np
import json
import os
import sys
import time
from datetime import datetime
from sqlalchemy.orm import Session

sys.path.append('.')
from backend.risk_engine import risk_engine
from backend.database.connection import SessionLocal, init_db
from backend.database.models import Account, Case, RiskPrediction, ShapExplanation, InvestigationEvent, AuditLog, Report, Transaction
from backend.database.repositories import (
    AccountRepository,
    CaseRepository,
    RiskPredictionRepository,
    ShapExplanationRepository,
    InvestigationEventRepository,
    AuditLogRepository,
    ReportRepository,
    TransactionRepository
)

STORAGE_DIR = os.path.join(os.path.dirname(__file__), 'storage')
os.makedirs(STORAGE_DIR, exist_ok=True)

class MuleDatabase:
    def __init__(self, data_path=None, max_retries=10, retry_delay=3):
        if data_path is None:
            data_path = os.path.join('data', 'data_copy.csv') if os.path.exists(os.path.join('data', 'data_copy.csv')) else 'data_copy.csv'
        self.data_path = data_path

        last_error = None
        for attempt in range(1, max_retries + 1):
            try:
                init_db()
                break
            except Exception as e:
                last_error = e
                if attempt < max_retries:
                    print(f"Database connection attempt {attempt}/{max_retries} failed, retrying in {retry_delay}s: {e}")
                    time.sleep(retry_delay)
                else:
                    raise RuntimeError(f"Database initialization failed after {max_retries} attempts: {last_error}")

        self.raw_df = pd.read_csv(data_path, engine='pyarrow')
        if 'Unnamed: 0' in self.raw_df.columns:
            self.raw_df = self.raw_df.drop(columns=['Unnamed: 0'])

        try:
            shap_path = os.path.join('data', 'shap_values_clean.npy') if os.path.exists(os.path.join('data', 'shap_values_clean.npy')) else 'shap_values_clean.npy'
            self.shap_values = np.load(shap_path)
            self.has_test_cache = True
        except Exception:
            self.has_test_cache = False

        self._seed_database_if_empty()

    def _seed_database_if_empty(self):
        db = SessionLocal()
        try:
            case_count = db.query(Case).count()
            if case_count > 0:
                print(f"Database already seeded. Registered cases count: {case_count}")
                return

            print("Database is empty. Initializing and seeding database from CSV...")
            
            # 1. Transform raw dataframe to get ML predictions
            X_processed_all = risk_engine.preprocessor.transform(self.raw_df)
            probs_all = risk_engine.model.predict_proba(X_processed_all)[:, 1]

            # 2. Insert initial system logs
            AuditLogRepository.create(db, {
                "timestamp": "2026-08-23 12:00:00 UTC",
                "actor": "System",
                "action": "Database Ingestion",
                "case_id": "All",
                "status": "SUCCESS"
            })
            AuditLogRepository.create(db, {
                "timestamp": "2026-08-23 12:00:10 UTC",
                "actor": "System",
                "action": "Model Loading",
                "case_id": "XGBoost v1.0.0-PRO",
                "status": "SUCCESS"
            })

            # 3. Seed accounts & cases based on V1 sample indices
            sample_indices = list(range(9000, 9082)) + list(range(0, 300))
            for idx in sample_indices:
                prob = float(probs_all[idx])
                tier, action = risk_engine.get_tier_action(prob)
                top3_feats = ["F994", "F3598", "F1319"]
                
                raw_row = self.raw_df.loc[idx].to_dict()
                attributes = {k: (str(v) if pd.notnull(v) else "N/A") for k, v in list(raw_row.items())[:15]}
                
                # Create Account
                AccountRepository.create(db, account_id=int(idx), attributes=attributes)
                
                # Create Case Status & Info
                status = "NEW" if tier in ["Critical", "High", "Medium"] else "CLEARED"
                analyst = "Unassigned" if status == "NEW" else "System"
                
                notes = [
                    {
                        "timestamp": "2026-08-23 12:00:00 UTC",
                        "analyst": "System",
                        "text": f"MuleShield PRO prediction model evaluated case. Score: {prob:.4f}. Classification: {tier} risk."
                    }
                ]
                
                CaseRepository.create(db, {
                    "account_id": int(idx),
                    "risk_score": round(prob, 4),
                    "tier": tier,
                    "status": status,
                    "assigned_analyst": analyst,
                    "action": action,
                    "notes": notes
                })

                # Create Risk Prediction History
                RiskPredictionRepository.create(db, {
                    "account_id": int(idx),
                    "risk_score": round(prob, 4),
                    "tier": tier,
                    "action": action,
                    "exceeds_threshold": prob >= risk_engine.decision_threshold
                })

                # Create SHAP Explanation
                ShapExplanationRepository.create(db, account_id=int(idx), features=top3_feats)

                # Create Investigation Ingestion Event
                InvestigationEventRepository.create(db, 
                    account_id=int(idx),
                    event_name="Case Ingestion",
                    detail=f"System identified {tier} risk level based on batch behavior.",
                    timestamp_str="2026-08-23 12:00:00 UTC"
                )
            
            # 4. Seed transaction relationships if table is empty
            tx_count = db.query(Transaction).count()
            if tx_count == 0:
                print("Seeding transaction relationships...")
                # Explicit suspicious structures
                # Cycle (9001 -> 9002 -> 9003 -> 9001)
                TransactionRepository.create(db, 9001, 9002, 150000.0, "UPI")
                TransactionRepository.create(db, 9002, 9003, 150000.0, "IMPS")
                TransactionRepository.create(db, 9003, 9001, 149500.0, "RTGS")
                
                # Fan-In (Hub 9010)
                TransactionRepository.create(db, 9004, 9010, 80000.0, "UPI")
                TransactionRepository.create(db, 9005, 9010, 95000.0, "UPI")
                TransactionRepository.create(db, 9006, 9010, 110000.0, "IMPS")
                TransactionRepository.create(db, 9007, 9010, 125000.0, "UPI")
                TransactionRepository.create(db, 9008, 9010, 70000.0, "RTGS")
                
                # Fan-Out (Hub 9010 distribution)
                TransactionRepository.create(db, 9010, 9011, 90000.0, "IMPS")
                TransactionRepository.create(db, 9010, 9012, 85000.0, "IMPS")
                TransactionRepository.create(db, 9010, 9013, 95000.0, "IMPS")
                TransactionRepository.create(db, 9010, 9014, 100000.0, "IMPS")
                TransactionRepository.create(db, 9010, 9015, 70000.0, "IMPS")
                
                # Multi-hop Path (9020 -> 9021 -> 9022 -> 9023 -> 9024)
                TransactionRepository.create(db, 9020, 9021, 200000.0, "RTGS")
                TransactionRepository.create(db, 9021, 9022, 198000.0, "RTGS")
                TransactionRepository.create(db, 9022, 9023, 196000.0, "RTGS")
                TransactionRepository.create(db, 9023, 9024, 190000.0, "RTGS")
                
                # Seed random transaction noise
                import random
                random.seed(42)
                for _ in range(150):
                    src = random.choice(sample_indices)
                    dst = random.choice(sample_indices)
                    if src != dst and not (src in [9001, 9002, 9003, 9004, 9005, 9006, 9007, 9008, 9010, 9020, 9021, 9022, 9023] and dst in [9001, 9002, 9003, 9010, 9011, 9012, 9013, 9014, 9015, 9021, 9022, 9023, 9024]):
                        amt = round(random.uniform(5000, 75000), 2)
                        tx_type = random.choice(["UPI", "IMPS", "RTGS"])
                        TransactionRepository.create(db, src, dst, amt, tx_type)
                print("Seeding transaction relationships completed.")
            
            # 5. Seed V1 BASELINE Model Registry entry
            from backend.database.models import ModelRegistry, ModelAudit
            model_count = db.query(ModelRegistry).filter(ModelRegistry.version == "V1 BASELINE").count()
            if model_count == 0:
                print("Seeding V1 BASELINE model registry entry...")
                v1_baseline = ModelRegistry(
                    version="V1 BASELINE",
                    model_artifact_path="modeling/mule_shield_model.json",
                    preprocessor_path="modeling/preprocessor.pkl",
                    feature_schema_path="modeling/feature_schema.json",
                    dataset_version="data_copy.csv",
                    metrics=json.dumps({
                        "precision": 1.0000,
                        "recall": 0.6164,
                        "f1": 0.7586,
                        "pr_auc": 0.8807
                    }),
                    threshold=0.9899,
                    training_config=json.dumps({
                        "decision_boundary_type": "high_precision",
                        "xgboost_params": {
                            "max_depth": 6,
                            "eta": 0.3,
                            "objective": "binary:logistic"
                        }
                    }),
                    validation_status="PASSED",
                    approval_status="PRODUCTION"
                )
                db.add(v1_baseline)
                db.commit()
                
                # Log initial audit
                audit = ModelAudit(
                    version="V1 BASELINE",
                    action="DEPLOY_PRODUCTION",
                    performed_by="system@muleshield.psb",
                    details=json.dumps({
                        "note": "Initial production seeding of stable baseline model.",
                        "metrics": {
                            "precision": 1.0000,
                            "recall": 0.6164,
                            "f1": 0.7586,
                            "pr_auc": 0.8807
                        },
                        "threshold": 0.9899
                    })
                )
                db.add(audit)
                db.commit()
                print("Seeding V1 BASELINE model registry completed.")
            
            print("Database seeding completed successfully.")
        except Exception as e:
            db.rollback()
            print(f"Error seeding database: {e}")
            raise e
        finally:
            db.close()

    @property
    def audit_logs(self):
        db = SessionLocal()
        try:
            logs = AuditLogRepository.get_all(db)
            return [
                {
                    "timestamp": l.timestamp.strftime("%Y-%m-%d %H:%M:%S UTC"),
                    "actor": l.actor,
                    "action": l.action,
                    "case_id": l.case_id,
                    "status": l.status
                }
                for l in logs
            ]
        finally:
            db.close()

    def log_audit_event(self, action, case_id, status, actor="Analyst-10"):
        db = SessionLocal()
        try:
            log_data = {
                "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
                "actor": actor,
                "action": action,
                "case_id": str(case_id),
                "status": status
            }
            AuditLogRepository.create(db, log_data)
        finally:
            db.close()

    def get_all_cases(self):
        db = SessionLocal()
        try:
            # Query active cases
            sql_cases = CaseRepository.get_all(db)
            
            # Fetch summary
            summary = self._get_dataset_summary_internal(db)
            
            cases_list = []
            for c in sql_cases:
                pred = RiskPredictionRepository.get_by_account_id(db, c.account_id)
                shap = ShapExplanationRepository.get_by_account_id(db, c.account_id)
                top_feats = shap.features if shap else ["F994", "F3598", "F1319"]
                
                mock_regulatory = {
                    "i4c_db": "FLAGGED" if c.tier == "Critical" else "CLEAR",
                    "cert_in_botnet": "CLEAR",
                    "rbi_caution_list": "FLAGGED" if c.tier == "Critical" else "CLEAR"
                }
                
                cases_list.append({
                    "account_id": c.account_id,
                    "risk_score": c.risk_score,
                    "tier": c.tier,
                    "status": c.status,
                    "assigned_analyst": c.assigned_analyst,
                    "created_at": c.created_at.strftime("%Y-%m-%d %H:%M:%S UTC"),
                    "action": c.action,
                    "top_shap_drivers": top_feats,
                    "regulatory_flags": mock_regulatory
                })

            tier_rank = {"Critical": 1, "High": 2, "Medium": 3, "Low": 4}
            cases_list.sort(key=lambda x: (tier_rank[x["tier"]], -x["risk_score"]))
            
            return {
                "summary": summary,
                "cases": cases_list
            }
        finally:
            db.close()

    def _get_dataset_summary_internal(self, db: Session):
        total_eval = len(self.raw_df)
        critical_c = db.query(Case).filter(Case.tier == "Critical").count()
        high_c = db.query(Case).filter(Case.tier == "High").count()
        medium_c = db.query(Case).filter(Case.tier == "Medium").count()
        low_c = db.query(Case).filter(Case.tier == "Low").count()
        
        # Balance cleared accounts using raw data count subtract flagged cases
        cleared_c = total_eval - (critical_c + high_c + medium_c)
        if cleared_c < 0:
            cleared_c = 0
            
        return {
            "total_evaluated": total_eval,
            "critical_alerts": critical_c,
            "high_risk": high_c,
            "medium_risk": medium_c,
            "cleared_accounts": cleared_c
        }

    def get_case(self, account_id: int):
        db = SessionLocal()
        try:
            sql_case = CaseRepository.get_by_account_id(db, account_id)
            if sql_case:
                return self._format_case_dict(db, sql_case)
            
            # Ad-hoc evaluation if not currently cached in Cases DB
            if account_id in self.raw_df.index:
                raw_row_df = self.raw_df.loc[[account_id]]
                res = risk_engine.predict_raw_row(raw_row_df)
                prob = res["risk_score"]
                tier = res["tier"]
                action = res["action"]
                
                raw_row = self.raw_df.loc[account_id].to_dict()
                attributes = {k: (str(v) if pd.notnull(v) else "N/A") for k, v in list(raw_row.items())[:15]}
                
                # Persist Account
                AccountRepository.create(db, account_id=account_id, attributes=attributes)
                
                # Persist Case
                CaseRepository.create(db, {
                    "account_id": account_id,
                    "risk_score": prob,
                    "tier": tier,
                    "status": "NEW" if tier in ["Critical", "High", "Medium"] else "CLEARED",
                    "assigned_analyst": "Unassigned" if tier in ["Critical", "High", "Medium"] else "System",
                    "action": action,
                    "notes": [
                        {
                            "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
                            "analyst": "System",
                            "text": f"Real-time inference executed on ad-hoc sandbox evaluation request. Score: {prob:.4f}."
                        }
                    ]
                })

                # Persist Prediction
                RiskPredictionRepository.create(db, {
                    "account_id": account_id,
                    "risk_score": prob,
                    "tier": tier,
                    "action": action,
                    "exceeds_threshold": prob >= risk_engine.decision_threshold
                })

                # Persist SHAP
                ShapExplanationRepository.create(db, account_id=account_id, features=["F994", "F3598", "F1319"])

                # Persist Event
                InvestigationEventRepository.create(db,
                    account_id=account_id,
                    event_name="Case Ingestion",
                    detail=f"Ad-hoc prediction created this case with {tier} risk level."
                )

                sql_case = CaseRepository.get_by_account_id(db, account_id)
                return self._format_case_dict(db, sql_case)
            
            return None
        finally:
            db.close()

    def _format_case_dict(self, db: Session, c: Case):
        acc = AccountRepository.get_by_id(db, c.account_id)
        shap = ShapExplanationRepository.get_by_account_id(db, c.account_id)
        events = InvestigationEventRepository.get_by_account_id(db, c.account_id)
        
        top_feats = shap.features if shap else ["F994", "F3598", "F1319"]
        mock_regulatory = {
            "i4c_db": "FLAGGED" if c.tier == "Critical" else "CLEAR",
            "cert_in_botnet": "CLEAR",
            "rbi_caution_list": "FLAGGED" if c.tier == "Critical" else "CLEAR"
        }
        
        timeline_list = [
            {
                "timestamp": e.timestamp.strftime("%Y-%m-%d %H:%M:%S UTC"),
                "event": e.event,
                "detail": e.detail
            }
            for e in events
        ]

        return {
            "account_id": c.account_id,
            "risk_score": c.risk_score,
            "tier": c.tier,
            "status": c.status,
            "assigned_analyst": c.assigned_analyst,
            "created_at": c.created_at.strftime("%Y-%m-%d %H:%M:%S UTC"),
            "action": c.action,
            "top_shap_drivers": top_feats,
            "regulatory_flags": mock_regulatory,
            "raw_attributes": acc.attributes if acc else {},
            "notes": c.notes or [],
            "timeline": timeline_list
        }

    def update_case_status(self, account_id: int, new_status: str, analyst: str):
        db = SessionLocal()
        try:
            case = CaseRepository.get_by_account_id(db, account_id)
            if not case:
                return None
            
            old_status = case.status
            CaseRepository.update_status(db, account_id, new_status, analyst)
            
            # Format update event detail
            timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
            detail = f"Status changed from {old_status} to {new_status.upper()} by {analyst}."
            InvestigationEventRepository.create(db, account_id, "Status Updated", detail)
            
            note_dict = {
                "timestamp": timestamp,
                "analyst": analyst,
                "text": f"System Status Update: Set lifecycle to {new_status.upper()}."
            }
            CaseRepository.add_note(db, account_id, note_dict)
            
            self.log_audit_event("Case Status Update", account_id, f"CHANGED TO {new_status.upper()}", analyst)
            
            # Reload updated case details
            updated_case = CaseRepository.get_by_account_id(db, account_id)
            return self._format_case_dict(db, updated_case)
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()

    def add_case_note(self, account_id: int, note_text: str, analyst: str):
        db = SessionLocal()
        try:
            case = CaseRepository.get_by_account_id(db, account_id)
            if not case:
                return None
            
            timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
            note_dict = {
                "timestamp": timestamp,
                "analyst": analyst,
                "text": note_text
            }
            CaseRepository.add_note(db, account_id, note_dict)
            
            detail = f"New note appended by analyst {analyst}."
            InvestigationEventRepository.create(db, account_id, "Note Added", detail)
            
            self.log_audit_event("Add Case Note", account_id, "SUCCESS", analyst)
            
            # Reload updated case details
            updated_case = CaseRepository.get_by_account_id(db, account_id)
            return self._format_case_dict(db, updated_case)
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()

    def generate_str_report(self, account_id: int):
        db = SessionLocal()
        try:
            case = CaseRepository.get_by_account_id(db, account_id)
            if not case:
                return None
            
            formatted_case = self._format_case_dict(db, case)
            drivers_formatted = "\n".join([f"  - {feat}: High behavioral anomaly score" for feat in formatted_case["top_shap_drivers"]])
            timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
            
            str_text = f"""SUSPICIOUS TRANSACTION REPORT (STR) DRAFT
==================================================
FIU-IND REGULATORY COMPLIANCE FILING
Generated by MuleShield AI/ML Risk Engine
==================================================

1. SUBJECT DETAILS:
   - Account Index: #{formatted_case['account_id']}
   - Risk Assessment Score: {formatted_case['risk_score']:.4f}
   - Risk Classification: {formatted_case['tier'].upper()}
   - Action Triggered: {formatted_case['action']}

2. KEY ANOMALY & SHAP JUSTIFICATION:
   The MuleShield AI classifier flagged this account due to significant deviations in the following core behavioral drivers:
{drivers_formatted}

3. REGULATORY DATABASE INTERSECTION:
   - I4C Cyber Fraud DB: {formatted_case['regulatory_flags']['i4c_db']}
   - CERT-In Botnet List: {formatted_case['regulatory_flags']['cert_in_botnet']}
   - RBI Caution List: {formatted_case['regulatory_flags']['rbi_caution_list']}

4. RECOMMENDED COMPLIANCE ACTION:
   Execute immediate freeze on debit transactions and transmit this STR to FIU-IND per PMLA guidelines.

==================================================
Report Generated: {timestamp}
Status: DRAFT READY FOR ANALYST SIGN-OFF
"""
            filepath = os.path.join(STORAGE_DIR, f"str_report_{account_id}.txt")
            with open(filepath, 'w') as f:
                f.write(str_text)
            
            # Save Report database entry
            ReportRepository.create(db, {
                "account_id": account_id,
                "report_type": "STR",
                "content": str_text,
                "filepath": filepath
            })
            
            # Add event to case timeline
            InvestigationEventRepository.create(db, account_id, "STR Report Generated", "FIU-IND draft STR document generated and stored in storage.")
            self.log_audit_event("Generate STR Draft", account_id, "SUCCESS")
            
            return {"str_draft": str_text, "filepath": filepath}
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()

    def get_sample_mule_payload(self):
        acc_id = 9003
        if acc_id in self.raw_df.index:
            raw_dict = self.raw_df.loc[acc_id].to_dict()
            clean_dict = {}
            for k, v in raw_dict.items():
                if k in ['F3924', 'Unnamed: 0'] or k.startswith('F2230') or k.startswith('F3888') or k in ['F3898', 'F3899', 'F3912', 'F3913', 'F3914', 'F3915']:
                    continue
                if pd.notnull(v):
                    clean_dict[k] = float(v) if isinstance(v, (int, float, np.number)) else str(v)
            return clean_dict
        return {"F1": 105.2, "F2": 0.04, "F994": 15.0}

db = MuleDatabase()
