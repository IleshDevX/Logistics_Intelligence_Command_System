"""
Step 18: Learning Loop (Daily Improvement Engine)
===================================================

Philosophy:
- Adjust slowly, safely, explainably
- Cap changes to ±5 points per day
- Learn from high-risk failures and low-risk successes
- Measure human override effectiveness
- Improve address confidence logic

This is NOT black-box retraining.
This is controlled, explainable weight adjustment.
"""

import json
import pandas as pd
import os
from datetime import datetime
from typing import Dict, Any, List, Tuple

# File paths
WEIGHT_FILE = "configs/risk_weights.json"
EOD_LOG = "logs/eod_summary.csv"
ADDRESS_DATA = "data/addresses.csv"
LEARNING_LOG = "logs/learning_history.csv"

# Learning parameters
MAX_WEIGHT_CHANGE = 5  # Maximum change per day
MIN_WEIGHT = 5  # Minimum weight value
MAX_WEIGHT = 30  # Maximum weight value


def load_risk_weights() -> Dict[str, Any]:
    """Load current risk weights from config file."""
    if not os.path.exists(WEIGHT_FILE):
        # Initialize with default weights
        default_weights = {
            "cod_risk": 15,
            "address_risk": 15,
            "weather_risk": 20,
            "area_risk": 15,
            "weight_risk": 10,
            "last_updated": datetime.now().isoformat(),
            "update_count": 0,
            "adjustment_history": []
        }
        os.makedirs(os.path.dirname(WEIGHT_FILE), exist_ok=True)
        with open(WEIGHT_FILE, "w") as f:
            json.dump(default_weights, f, indent=2)
        return default_weights
    
    with open(WEIGHT_FILE, "r") as f:
        return json.load(f)


def save_risk_weights(weights: Dict[str, Any]):
    """Save updated risk weights to config file."""
    with open(WEIGHT_FILE, "w") as f:
        json.dump(weights, f, indent=2)


def update_risk_weights() -> Dict[str, Any]:
    """
    Update risk weights based on EOD outcomes.
    
    Learning Rules:
    1. If high-risk shipments (>60) fail → increase relevant weights
    2. If low-risk shipments (<30) succeed → reduce weights slightly
    3. Cap changes to ±5 per day
    4. Maintain weights between 5 and 30
    
    Returns:
        Updated weights dictionary with adjustments
    """
    if not os.path.exists(EOD_LOG):
        return {"error": "No EOD data available for learning"}
    
    eod = pd.read_csv(EOD_LOG)
    
    if eod.empty:
        return {"error": "EOD data is empty"}
    
    # Load current weights
    weights = load_risk_weights()
    original_weights = {
        "cod_risk": weights["cod_risk"],
        "address_risk": weights["address_risk"],
        "weather_risk": weights["weather_risk"],
        "area_risk": weights["area_risk"],
        "weight_risk": weights["weight_risk"]
    }
    
    adjustments = {
        "cod_risk": 0,
        "address_risk": 0,
        "weather_risk": 0,
        "area_risk": 0,
        "weight_risk": 0
    }
    
    # Rule 1: High-risk failures → increase weights
    high_risk_failures = eod[
        (eod["predicted_risk_score"] > 60) &
        (eod["actual_status"] != "DELIVERED")
    ]
    
    if len(high_risk_failures) > 0:
        # Increase address and weather risk (most common failure factors)
        adjustment = min(len(high_risk_failures), MAX_WEIGHT_CHANGE)
        adjustments["address_risk"] += adjustment
        adjustments["weather_risk"] += adjustment
    
    # Rule 2: Low-risk successes → reduce weights slightly
    low_risk_success = eod[
        (eod["predicted_risk_score"] < 30) &
        (eod["actual_status"] == "DELIVERED")
    ]
    
    if len(low_risk_success) > 5:  # Only reduce if we have enough evidence
        # Reduce weight risk slightly (least impactful factor)
        adjustment = -min(len(low_risk_success) // 5, MAX_WEIGHT_CHANGE)
        adjustments["weight_risk"] += adjustment
    
    # Rule 3: Learn from mismatches (AI missed risks)
    missed_risks = eod[
        (eod["mismatch_flag"] == True) &
        (eod["predicted_decision"] == "DISPATCH") &
        (eod["actual_status"] != "DELIVERED")
    ]
    
    if len(missed_risks) > 0:
        # Increase all weights slightly to be more cautious
        adjustment = min(len(missed_risks), MAX_WEIGHT_CHANGE)
        adjustments["cod_risk"] += adjustment
        adjustments["area_risk"] += adjustment
    
    # Apply adjustments with caps
    for key in ["cod_risk", "address_risk", "weather_risk", "area_risk", "weight_risk"]:
        new_value = weights[key] + adjustments[key]
        weights[key] = max(MIN_WEIGHT, min(MAX_WEIGHT, new_value))
    
    # Update metadata
    weights["last_updated"] = datetime.now().isoformat()
    weights["update_count"] = weights.get("update_count", 0) + 1
    
    # Log adjustment
    adjustment_record = {
        "timestamp": datetime.now().isoformat(),
        "high_risk_failures": len(high_risk_failures),
        "low_risk_successes": len(low_risk_success),
        "missed_risks": len(missed_risks),
        "adjustments": adjustments,
        "new_weights": {k: weights[k] for k in ["cod_risk", "address_risk", "weather_risk", "area_risk", "weight_risk"]}
    }
    
    if "adjustment_history" not in weights:
        weights["adjustment_history"] = []
    weights["adjustment_history"].append(adjustment_record)
    
    # Keep only last 30 adjustments
    if len(weights["adjustment_history"]) > 30:
        weights["adjustment_history"] = weights["adjustment_history"][-30:]
    
    # Save updated weights
    save_risk_weights(weights)
    
    return {
        "original_weights": original_weights,
        "adjustments": adjustments,
        "updated_weights": {k: weights[k] for k in ["cod_risk", "address_risk", "weather_risk", "area_risk", "weight_risk"]},
        "learning_signals": {
            "high_risk_failures": len(high_risk_failures),
            "low_risk_successes": len(low_risk_success),
            "missed_risks": len(missed_risks)
        }
    }


def improve_address_scoring() -> Dict[str, Any]:
    """
    Analyze address confidence scoring effectiveness.
    
    Learning Rule:
    - If low-confidence addresses (<60) still delivered successfully
    → Address scoring is too pessimistic
    → Return adjustment factor
    
    Returns:
        Address learning insights
    """
    if not os.path.exists(EOD_LOG) or not os.path.exists(ADDRESS_DATA):
        return {"error": "Required data files not available"}
    
    eod = pd.read_csv(EOD_LOG)
    addresses = pd.read_csv(ADDRESS_DATA)
    
    # Merge EOD with address data
    merged = eod.merge(addresses, on="shipment_id", how="inner")
    
    if merged.empty:
        return {"error": "No matching address data"}
    
    # Find successful deliveries with low address confidence
    successful_low_conf = merged[
        (merged["address_confidence_score"] < 60) &
        (merged["actual_status"] == "DELIVERED")
    ]
    
    # Find failed deliveries with high address confidence
    failed_high_conf = merged[
        (merged["address_confidence_score"] > 80) &
        (merged["actual_status"] != "DELIVERED")
    ]
    
    # Calculate adjustment factor
    improvement_factor = min(len(successful_low_conf) * 2, 10)
    pessimism_factor = -min(len(failed_high_conf) * 2, 10)
    
    net_adjustment = improvement_factor + pessimism_factor
    
    # Analyze by area type
    area_analysis = merged.groupby("area_type").agg({
        "was_successful": "mean",
        "address_confidence_score": "mean"
    }).round(2).to_dict()
    
    return {
        "address_confidence_adjustment": net_adjustment,
        "successful_low_confidence": len(successful_low_conf),
        "failed_high_confidence": len(failed_high_conf),
        "affected_shipments": len(successful_low_conf) + len(failed_high_conf),
        "recommendation": "INCREASE_CONFIDENCE" if net_adjustment > 0 else "DECREASE_CONFIDENCE" if net_adjustment < 0 else "NO_CHANGE",
        "area_analysis": area_analysis
    }


def analyze_override_effectiveness() -> Dict[str, Any]:
    """
    Analyze human override success rate.
    
    Critical Question: Did humans outperform AI?
    
    Metrics:
    - Total overrides
    - Successful overrides (delivered)
    - Override success rate
    - Comparison with AI success rate
    
    Returns:
        Override effectiveness analysis
    """
    if not os.path.exists(EOD_LOG):
        return {"error": "No EOD data available"}
    
    eod = pd.read_csv(EOD_LOG)
    
    # Analyze overrides
    overrides = eod[eod["override_flag"] == True]
    
    if overrides.empty:
        return {
            "total_overrides": 0,
            "successful_overrides": 0,
            "override_success_rate": None,
            "message": "No overrides in this period"
        }
    
    successful_overrides = overrides[overrides["actual_status"] == "DELIVERED"]
    override_success_rate = len(successful_overrides) / len(overrides)
    
    # Compare with AI decisions (no override)
    ai_decisions = eod[eod["override_flag"] == False]
    if not ai_decisions.empty:
        ai_success_rate = len(ai_decisions[ai_decisions["actual_status"] == "DELIVERED"]) / len(ai_decisions)
    else:
        ai_success_rate = None
    
    # Analyze override reasons
    override_reasons = overrides["override_reason"].value_counts().head(5).to_dict()
    
    # Performance comparison
    if ai_success_rate is not None:
        performance_gap = override_success_rate - ai_success_rate
        if performance_gap > 0.1:
            insight = "Humans outperforming AI - Consider incorporating override patterns"
        elif performance_gap < -0.1:
            insight = "AI outperforming humans - Review override criteria"
        else:
            insight = "Human and AI performance balanced"
    else:
        insight = "Insufficient AI data for comparison"
    
    return {
        "total_overrides": len(overrides),
        "successful_overrides": len(successful_overrides),
        "override_success_rate": round(override_success_rate, 2),
        "ai_success_rate": round(ai_success_rate, 2) if ai_success_rate is not None else None,
        "performance_gap": round(performance_gap, 2) if ai_success_rate is not None else None,
        "top_override_reasons": override_reasons,
        "insight": insight
    }


def get_learning_statistics() -> Dict[str, Any]:
    """
    Get comprehensive learning loop statistics.
    
    Returns:
        Overall learning metrics
    """
    if not os.path.exists(EOD_LOG):
        return {"error": "No EOD data available"}
    
    eod = pd.read_csv(EOD_LOG)
    
    if eod.empty:
        return {"error": "EOD data is empty"}
    
    total_shipments = len(eod)
    successful = len(eod[eod["was_successful"] == True])
    mismatches = len(eod[eod["mismatch_flag"] == True])
    overrides = len(eod[eod["override_flag"] == True])
    avg_accuracy = eod["prediction_accuracy"].mean()
    
    # Risk bucket performance
    risk_performance = eod.groupby("predicted_risk_bucket").agg({
        "was_successful": "mean",
        "prediction_accuracy": "mean"
    }).round(2).to_dict()
    
    # Decision performance
    decision_performance = eod.groupby("predicted_decision").agg({
        "was_successful": "mean",
        "had_delay": "mean"
    }).round(2).to_dict()
    
    return {
        "total_shipments": total_shipments,
        "success_rate": round(successful / total_shipments, 2),
        "mismatch_rate": round(mismatches / total_shipments, 2),
        "override_rate": round(overrides / total_shipments, 2),
        "avg_prediction_accuracy": round(avg_accuracy, 2),
        "risk_bucket_performance": risk_performance,
        "decision_performance": decision_performance
    }


def log_learning_cycle(results: Dict[str, Any]):
    """
    Log learning cycle execution for audit trail.
    
    Args:
        results: Complete learning loop results
    """
    os.makedirs("logs", exist_ok=True)
    
    # Create learning history log
    if not os.path.exists(LEARNING_LOG):
        df = pd.DataFrame(columns=[
            "timestamp", "weight_updates", "address_adjustment", 
            "override_effectiveness", "total_shipments", "learning_signals"
        ])
        df.to_csv(LEARNING_LOG, index=False)
    
    # Append new record
    record = {
        "timestamp": datetime.now().isoformat(),
        "weight_updates": json.dumps(results.get("updated_weights", {})),
        "address_adjustment": results.get("address_learning", {}).get("address_confidence_adjustment", 0),
        "override_effectiveness": results.get("override_metrics", {}).get("override_success_rate", 0),
        "total_shipments": results.get("learning_statistics", {}).get("total_shipments", 0),
        "learning_signals": json.dumps(results.get("updated_weights", {}).get("learning_signals", {}))
    }
    
    df = pd.read_csv(LEARNING_LOG)
    df = pd.concat([df, pd.DataFrame([record])], ignore_index=True)
    df.to_csv(LEARNING_LOG, index=False)


def run_learning_loop() -> Dict[str, Any]:
    """
    Execute complete learning loop.
    
    Steps:
    1. Update risk weights based on failures/successes
    2. Improve address confidence logic
    3. Analyze human override effectiveness
    4. Generate learning statistics
    5. Log learning cycle
    
    Returns:
        Complete learning loop results
    """
    print("🧠 RUNNING LEARNING LOOP...")
    print("=" * 60)
    
    # Step 1: Update risk weights
    print("\n1️⃣ Updating Risk Weights...")
    weight_results = update_risk_weights()
    
    if "error" not in weight_results:
        print(f"   ✅ Weights adjusted based on:")
        print(f"      - {weight_results['learning_signals']['high_risk_failures']} high-risk failures")
        print(f"      - {weight_results['learning_signals']['low_risk_successes']} low-risk successes")
        print(f"      - {weight_results['learning_signals']['missed_risks']} missed risks")
    else:
        print(f"   ⚠️  {weight_results['error']}")
    
    # Step 2: Improve address scoring
    print("\n2️⃣ Analyzing Address Confidence...")
    address_results = improve_address_scoring()
    
    if "error" not in address_results:
        print(f"   ✅ Address scoring analysis:")
        print(f"      - Adjustment factor: {address_results['address_confidence_adjustment']}")
        print(f"      - Successful low-confidence: {address_results['successful_low_confidence']}")
        print(f"      - Failed high-confidence: {address_results['failed_high_confidence']}")
        print(f"      - Recommendation: {address_results['recommendation']}")
    else:
        print(f"   ⚠️  {address_results['error']}")
    
    # Step 3: Analyze overrides
    print("\n3️⃣ Analyzing Human Override Effectiveness...")
    override_results = analyze_override_effectiveness()
    
    if "error" not in override_results:
        print(f"   ✅ Override analysis:")
        print(f"      - Total overrides: {override_results['total_overrides']}")
        if override_results['total_overrides'] > 0:
            print(f"      - Success rate: {override_results['override_success_rate']}")
            if override_results.get('ai_success_rate'):
                print(f"      - AI success rate: {override_results['ai_success_rate']}")
                print(f"      - Performance gap: {override_results['performance_gap']}")
            print(f"      - Insight: {override_results['insight']}")
    else:
        print(f"   ⚠️  {override_results['error']}")
    
    # Step 4: Learning statistics
    print("\n4️⃣ Generating Learning Statistics...")
    stats = get_learning_statistics()
    
    if "error" not in stats:
        print(f"   ✅ Overall performance:")
        print(f"      - Total shipments analyzed: {stats['total_shipments']}")
        print(f"      - Success rate: {stats['success_rate']}")
        print(f"      - Mismatch rate: {stats['mismatch_rate']}")
        print(f"      - Avg prediction accuracy: {stats['avg_prediction_accuracy']}")
    else:
        print(f"   ⚠️  {stats['error']}")
    
    # Compile results
    results = {
        "updated_weights": weight_results,
        "address_learning": address_results,
        "override_metrics": override_results,
        "learning_statistics": stats,
        "execution_timestamp": datetime.now().isoformat()
    }
    
    # Step 5: Log learning cycle
    log_learning_cycle(results)
    
    print("\n" + "=" * 60)
    print("✅ LEARNING LOOP COMPLETE")
    print("=" * 60)
    
    return results


def get_learning_history(last_n: int = 10) -> pd.DataFrame:
    """
    Get recent learning cycle history.
    
    Args:
        last_n: Number of recent cycles to retrieve
        
    Returns:
        DataFrame with learning history
    """
    if not os.path.exists(LEARNING_LOG):
        return pd.DataFrame()
    
    df = pd.read_csv(LEARNING_LOG)
    return df.tail(last_n)


def get_weight_evolution() -> Dict[str, List[Tuple[str, Dict[str, int]]]]:
    """
    Get weight evolution over time.
    
    Returns:
        Weight evolution history
    """
    weights = load_risk_weights()
    
    if "adjustment_history" not in weights:
        return {"evolution": []}
    
    evolution = []
    for record in weights["adjustment_history"]:
        evolution.append({
            "timestamp": record["timestamp"],
            "weights": record["new_weights"],
            "signals": record.get("learning_signals", {})
        })
    
    return {"evolution": evolution}


if __name__ == "__main__":
    # Run learning loop
    results = run_learning_loop()
    
    # Print summary
    print("\n📊 LEARNING LOOP SUMMARY")
    print("=" * 60)
    print(json.dumps(results, indent=2, default=str))
