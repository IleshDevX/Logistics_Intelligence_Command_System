"""
End-of-Day Logging & Learning Loop Feeder
Step 17: Compare predictions vs reality, capture learning truth

Purpose:
- Compare predicted vs actual delivery outcomes
- Record delays, failures, and human overrides
- Store decision truth for continuous learning
- Feed clean data into delivery_history.csv

This closes the loop:
Prediction → Action → Outcome → Learning

Philosophy:
"We learn from our mistakes. Every mismatch between prediction and 
reality is a training opportunity for tomorrow's smarter system."
"""

import pandas as pd
from datetime import datetime, date
import os
from typing import Tuple, Optional, Dict, List

# Log file paths
TRACKING_LOG = "logs/tracking_events.csv"
OVERRIDE_LOG = "logs/override_log.csv"
EOD_LOG = "logs/eod_summary.csv"
DELIVERY_HISTORY = "Data/delivery_history.csv"

# ==================== OUTCOME EXTRACTION ====================

def get_final_status(shipment_id: str) -> Tuple[str, int]:
    """
    Extract final delivery status and total delay from tracking events
    
    Args:
        shipment_id: Unique shipment identifier
    
    Returns:
        Tuple of (final_status, delay_minutes)
    """
    try:
        df = pd.read_csv(TRACKING_LOG)
        events = df[df["shipment_id"] == shipment_id]
        
        if events.empty:
            return "UNKNOWN", 0
        
        # Get final status
        final_status = events.iloc[-1]["status"]
        
        # Calculate delay minutes (15 min per DELAY event as heuristic)
        delay_events = events[events["status"].str.contains("DELAY", na=False)]
        delay_minutes = len(delay_events) * 15
        
        # If final status is FAILED_ATTEMPT, add extra delay
        if final_status == "FAILED_ATTEMPT":
            delay_minutes += 60  # 1 hour penalty for failed delivery
        
        return final_status, delay_minutes
    
    except FileNotFoundError:
        return "UNKNOWN", 0
    except Exception as e:
        print(f"Error getting final status for {shipment_id}: {e}")
        return "UNKNOWN", 0

def get_override_info(shipment_id: str) -> Tuple[bool, Optional[str]]:
    """
    Check if shipment had human override and get reason
    
    Args:
        shipment_id: Unique shipment identifier
    
    Returns:
        Tuple of (override_flag, override_reason)
    """
    try:
        df = pd.read_csv(OVERRIDE_LOG)
        record = df[df["shipment_id"] == shipment_id]
        
        if record.empty:
            return False, None
        
        # Get most recent override
        latest = record.iloc[-1]
        return True, latest["override_reason"]
    
    except FileNotFoundError:
        return False, None
    except Exception as e:
        print(f"Error getting override info for {shipment_id}: {e}")
        return False, None

def get_failure_reason(shipment_id: str) -> Optional[str]:
    """
    Extract failure reason if delivery failed
    
    Args:
        shipment_id: Unique shipment identifier
    
    Returns:
        Failure reason or None
    """
    try:
        df = pd.read_csv(TRACKING_LOG)
        events = df[df["shipment_id"] == shipment_id]
        
        # Look for FAILED_ATTEMPT or DELIVERY_DELAY
        failed = events[events["status"] == "FAILED_ATTEMPT"]
        if not failed.empty:
            return failed.iloc[-1]["remarks"]
        
        delayed = events[events["status"] == "DELIVERY_DELAY"]
        if not delayed.empty:
            return delayed.iloc[-1]["remarks"]
        
        return None
    
    except:
        return None

# ==================== PREDICTION VS REALITY ====================

def mismatch_detected(predicted_decision: str, actual_status: str, override_flag: bool) -> bool:
    """
    Determine if prediction mismatched reality
    
    Args:
        predicted_decision: AI's decision (DISPATCH/DELAY/RESCHEDULE)
        actual_status: Final delivery status
        override_flag: Was there human override?
    
    Returns:
        bool: True if significant mismatch
    
    Logic:
    - DISPATCH prediction but delivery failed → MISMATCH
    - DISPATCH prediction but major delay → MISMATCH
    - DELAY prediction but delivered normally → ACCEPTABLE (cautious AI is OK)
    - Human override present → NO MISMATCH (human took control)
    """
    # If human overrode, don't blame AI
    if override_flag:
        return False
    
    # AI said DISPATCH but delivery failed
    if predicted_decision == "DISPATCH" and actual_status in ["FAILED_ATTEMPT", "PACKING_DELAY", "DELIVERY_DELAY"]:
        return True
    
    # AI said DISPATCH but never delivered
    if predicted_decision == "DISPATCH" and actual_status != "DELIVERED":
        return True
    
    # AI said RESCHEDULE but we delivered anyway (maybe address was OK)
    if predicted_decision == "RESCHEDULE" and actual_status == "DELIVERED":
        return True
    
    # AI was cautious (DELAY) but delivered fine → NOT a mismatch (we tolerate caution)
    if predicted_decision == "DELAY" and actual_status == "DELIVERED":
        return False
    
    return False

def calculate_prediction_accuracy(predicted_decision: str, actual_status: str) -> float:
    """
    Calculate prediction accuracy score (0-100)
    
    Args:
        predicted_decision: AI decision
        actual_status: Actual outcome
    
    Returns:
        float: Accuracy score
    """
    # Perfect prediction
    if predicted_decision == "DISPATCH" and actual_status == "DELIVERED":
        return 100.0
    
    # Acceptable caution
    if predicted_decision == "DELAY" and actual_status == "DELIVERED":
        return 80.0
    
    # Missed prediction
    if predicted_decision == "DISPATCH" and actual_status != "DELIVERED":
        return 20.0
    
    # Reschedule suggested and was needed
    if predicted_decision == "RESCHEDULE" and actual_status in ["FAILED_ATTEMPT", "DELIVERY_DELAY"]:
        return 90.0
    
    return 50.0

# ==================== EOD RECORD LOGGING ====================

def log_end_of_day(
    shipment_id: str,
    predicted_risk_score: float,
    predicted_decision: str,
    predicted_risk_bucket: str = "UNKNOWN"
) -> Dict:
    """
    Log end-of-day record comparing prediction vs reality
    
    Args:
        shipment_id: Unique shipment identifier
        predicted_risk_score: AI's risk score (0-100)
        predicted_decision: AI's decision (DISPATCH/DELAY/RESCHEDULE)
        predicted_risk_bucket: Risk bucket (LOW/MEDIUM/HIGH)
    
    Returns:
        dict: EOD record
    """
    # Get actual outcomes
    actual_status, delay_minutes = get_final_status(shipment_id)
    override_flag, override_reason = get_override_info(shipment_id)
    failure_reason = get_failure_reason(shipment_id)
    
    # Calculate mismatch
    mismatch = mismatch_detected(predicted_decision, actual_status, override_flag)
    accuracy = calculate_prediction_accuracy(predicted_decision, actual_status)
    
    # Build EOD record
    record = {
        "shipment_id": shipment_id,
        "log_date": date.today().isoformat(),
        "log_timestamp": datetime.utcnow().isoformat(),
        
        # Predictions
        "predicted_risk_score": predicted_risk_score,
        "predicted_risk_bucket": predicted_risk_bucket,
        "predicted_decision": predicted_decision,
        
        # Actuals
        "actual_status": actual_status,
        "delay_minutes": delay_minutes,
        "failure_reason": failure_reason if failure_reason else "",
        
        # Human factors
        "override_flag": override_flag,
        "override_reason": override_reason if override_reason else "",
        
        # Learning metrics
        "mismatch_flag": mismatch,
        "prediction_accuracy": accuracy,
        
        # Derived insights
        "was_successful": actual_status == "DELIVERED",
        "had_delay": delay_minutes > 0,
        "ai_was_cautious": predicted_decision in ["DELAY", "RESCHEDULE"]
    }
    
    # Ensure logs directory exists
    os.makedirs("logs", exist_ok=True)
    
    # Append to EOD log
    try:
        df = pd.read_csv(EOD_LOG)
        df = pd.concat([df, pd.DataFrame([record])], ignore_index=True)
    except FileNotFoundError:
        df = pd.DataFrame([record])
    
    df.to_csv(EOD_LOG, index=False)
    
    return record

# ==================== BATCH EOD PROCESSING ====================

def run_eod_for_all(shipments_df: pd.DataFrame) -> List[Dict]:
    """
    Run end-of-day logging for all shipments (batch job)
    
    Args:
        shipments_df: DataFrame with shipment data
    
    Returns:
        List of EOD records
    """
    results = []
    
    for _, row in shipments_df.iterrows():
        try:
            record = log_end_of_day(
                shipment_id=row.get("shipment_id", row.get("Shipment_ID")),
                predicted_risk_score=row.get("current_risk_score", 0),
                predicted_decision=row.get("ai_decision", "UNKNOWN"),
                predicted_risk_bucket=row.get("risk_bucket", "UNKNOWN")
            )
            results.append(record)
        except Exception as e:
            print(f"Error processing {row.get('shipment_id', 'UNKNOWN')}: {e}")
            continue
    
    return results

def run_eod_for_shipment_ids(shipment_ids: List[str]) -> List[Dict]:
    """
    Run end-of-day logging for specific shipment IDs
    
    Args:
        shipment_ids: List of shipment IDs to process
    
    Returns:
        List of EOD records
    """
    results = []
    
    for shipment_id in shipment_ids:
        try:
            # Try to get predictions from tracking or use defaults
            record = log_end_of_day(
                shipment_id=shipment_id,
                predicted_risk_score=50,  # Default if unknown
                predicted_decision="DISPATCH"  # Default if unknown
            )
            results.append(record)
        except Exception as e:
            print(f"Error processing {shipment_id}: {e}")
            continue
    
    return results

# ==================== LEARNING ANALYTICS ====================

def get_eod_statistics() -> Dict:
    """
    Get statistics from end-of-day logs for learning insights
    
    Returns:
        dict: Statistics about predictions vs reality
    """
    try:
        df = pd.read_csv(EOD_LOG)
        
        if len(df) == 0:
            return {"message": "No EOD data available"}
        
        stats = {
            "total_shipments": len(df),
            "successful_deliveries": len(df[df["was_successful"] == True]),
            "delivery_success_rate": (len(df[df["was_successful"] == True]) / len(df) * 100),
            
            "total_delays": len(df[df["had_delay"] == True]),
            "avg_delay_minutes": df["delay_minutes"].mean(),
            
            "total_overrides": len(df[df["override_flag"] == True]),
            "override_rate": (len(df[df["override_flag"] == True]) / len(df) * 100),
            
            "total_mismatches": len(df[df["mismatch_flag"] == True]),
            "mismatch_rate": (len(df[df["mismatch_flag"] == True]) / len(df) * 100),
            
            "avg_prediction_accuracy": df["prediction_accuracy"].mean(),
            
            "ai_caution_count": len(df[df["ai_was_cautious"] == True]),
            
            "decision_distribution": df["predicted_decision"].value_counts().to_dict(),
            "status_distribution": df["actual_status"].value_counts().to_dict()
        }
        
        return stats
    
    except FileNotFoundError:
        return {"message": "No EOD data available"}
    except Exception as e:
        return {"error": str(e)}

def get_learning_insights() -> List[str]:
    """
    Generate actionable learning insights from EOD data
    
    Returns:
        List of insight strings
    """
    try:
        df = pd.read_csv(EOD_LOG)
        insights = []
        
        if len(df) == 0:
            return ["No data available for learning insights"]
        
        # High mismatch rate
        mismatch_rate = len(df[df["mismatch_flag"] == True]) / len(df) * 100
        if mismatch_rate > 20:
            insights.append(f"⚠️ HIGH MISMATCH RATE ({mismatch_rate:.1f}%): Risk model needs recalibration")
        
        # Override patterns
        override_rate = len(df[df["override_flag"] == True]) / len(df) * 100
        if override_rate > 10:
            insights.append(f"🔄 HIGH OVERRIDE RATE ({override_rate:.1f}%): AI may be too conservative or missing context")
        
        # Delays despite DISPATCH
        dispatch_delayed = df[(df["predicted_decision"] == "DISPATCH") & (df["had_delay"] == True)]
        if len(dispatch_delayed) > 0:
            rate = len(dispatch_delayed) / len(df[df["predicted_decision"] == "DISPATCH"]) * 100
            insights.append(f"⏰ {rate:.1f}% of DISPATCH decisions had delays: Consider stricter thresholds")
        
        # Successful cautious predictions
        cautious_success = df[(df["ai_was_cautious"] == True) & (df["was_successful"] == True)]
        if len(cautious_success) > len(df) * 0.3:
            insights.append("✅ AI is being overly cautious: Many DELAY/RESCHEDULE predictions delivered fine")
        
        # Failed deliveries
        failed_rate = len(df[df["actual_status"] == "FAILED_ATTEMPT"]) / len(df) * 100
        if failed_rate > 5:
            insights.append(f"❌ FAILED DELIVERY RATE ({failed_rate:.1f}%): Address intelligence needs improvement")
        
        if not insights:
            insights.append("✅ System performing well: Low mismatch rate, good prediction accuracy")
        
        return insights
    
    except:
        return ["Unable to generate insights - insufficient data"]

def get_top_mismatch_patterns() -> pd.DataFrame:
    """
    Identify common patterns in prediction mismatches
    
    Returns:
        DataFrame with mismatch patterns
    """
    try:
        df = pd.read_csv(EOD_LOG)
        mismatches = df[df["mismatch_flag"] == True]
        
        if len(mismatches) == 0:
            return pd.DataFrame(columns=["pattern", "count"])
        
        # Group by prediction and actual
        patterns = mismatches.groupby(["predicted_decision", "actual_status"]).size().reset_index(name="count")
        patterns = patterns.sort_values("count", ascending=False)
        
        return patterns
    
    except:
        return pd.DataFrame(columns=["pattern", "count"])

# ==================== DELIVERY HISTORY FEEDER ====================

def update_delivery_history(eod_records: List[Dict]):
    """
    Feed EOD data into delivery_history.csv for long-term learning
    
    Args:
        eod_records: List of EOD records to append
    """
    try:
        # Load existing delivery history
        try:
            history_df = pd.read_csv(DELIVERY_HISTORY)
        except FileNotFoundError:
            # Create new if doesn't exist
            history_df = pd.DataFrame()
        
        # Convert EOD records to history format
        new_records = []
        for record in eod_records:
            history_record = {
                "Shipment_ID": record["shipment_id"],
                "Delivery_Date": record["log_date"],
                "Actual_Status": record["actual_status"],
                "Delay_Minutes": record["delay_minutes"],
                "Override_Applied": record["override_flag"],
                "Prediction_Accuracy": record["prediction_accuracy"],
                "Risk_Score_At_Dispatch": record["predicted_risk_score"]
            }
            new_records.append(history_record)
        
        # Append to history
        new_df = pd.DataFrame(new_records)
        history_df = pd.concat([history_df, new_df], ignore_index=True)
        
        # Save
        history_df.to_csv(DELIVERY_HISTORY, index=False)
        
        print(f"✅ Updated delivery_history.csv with {len(new_records)} records")
    
    except Exception as e:
        print(f"⚠️ Error updating delivery history: {e}")

# ==================== LEARNING LOOP FEEDBACK ====================

def get_learning_recommendations() -> Dict:
    """
    Generate specific recommendations for system improvement
    
    Returns:
        dict: Recommendations for each component
    """
    stats = get_eod_statistics()
    
    if "message" in stats or "error" in stats:
        return {
            "risk_engine": [],
            "address_intelligence": [],
            "weather_impact": [],
            "decision_gate": [],
            "vehicle_selector": [],
            "note": "Insufficient data for recommendations"
        }
    
    recommendations = {
        "risk_engine": [],
        "address_intelligence": [],
        "weather_impact": [],
        "decision_gate": [],
        "vehicle_selector": []
    }
    
    # Risk engine recommendations
    if stats.get("mismatch_rate", 0) > 15:
        recommendations["risk_engine"].append("Recalibrate risk weights - high prediction error rate")
    if stats.get("avg_prediction_accuracy", 0) < 75:
        recommendations["risk_engine"].append("Consider adding more risk factors or refining existing ones")
    
    # Address intelligence recommendations
    try:
        df = pd.read_csv(EOD_LOG)
        address_failures = df[df["failure_reason"].str.contains("address", case=False, na=False)]
        if len(address_failures) > len(df) * 0.1:
            recommendations["address_intelligence"].append("High address-related failures - improve landmark detection")
    except:
        pass
    
    # Decision gate recommendations
    if stats.get("override_rate", 0) > 15:
        recommendations["decision_gate"].append("High override rate - AI thresholds may be miscalibrated")
    
    return recommendations

if __name__ == "__main__":
    # Example usage
    print("End-of-Day Logger initialized")
    print(f"Logs directory: {os.path.abspath('logs')}")
