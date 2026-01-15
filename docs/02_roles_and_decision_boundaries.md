# Stakeholder Roles & Decision Boundaries
## Human-in-the-Loop Governance Model

---

## 1. Purpose of Role Separation

This system is designed to support logistics decisions, not automate them.
Clear role separation ensures:
- Accountability
- Decision transparency
- Safe use of AI recommendations

Each role has **explicit permissions and restrictions**.

---

## 2. Stakeholder Roles Overview

The system supports three primary human roles:

- Seller
- Manager
- Supervisor

AI is treated as an **advisory component**, not a role.

---

## 3. Seller Role

### Responsibilities
- Upload shipment details
- Provide accurate product and delivery information
- View risk indicators and explanations

### Allowed Actions
- Create shipment requests
- View AI-generated risk insights
- View suggested vehicle and warnings

### Explicit Restrictions
- Cannot approve or reject shipments
- Cannot override AI recommendations
- Cannot modify system rules
- Cannot view other sellers’ shipments

### Decision Authority
❌ No final decision authority

---

## 4. Manager Role

### Responsibilities
- Evaluate AI recommendations
- Make dispatch decisions
- Apply real-world operational judgment

### Allowed Actions
- View all shipment details
- Accept, hold, or override AI recommendations
- Provide override justifications
- Select or change delivery vehicle

### Explicit Restrictions
- Cannot change system-wide rules
- Cannot edit historical records
- Cannot bypass explanation requirements

### Decision Authority
✅ Final decision authority at dispatch level

---

## 5. Supervisor Role

### Responsibilities
- Monitor system performance
- Review historical outcomes
- Ensure governance and compliance

### Allowed Actions
- View completed and in-transit shipments
- View AI vs human decision comparisons
- Analyze delivery success rates
- Review override patterns

### Explicit Restrictions
- Cannot create shipments
- Cannot approve or reject individual shipments
- Cannot modify operational decisions

### Decision Authority
❌ No operational decision authority  
✅ Governance and oversight authority only

---

## 6. AI Component (Non-Human)

### Role Definition
AI is an advisory system embedded within the platform.

### Capabilities
- Risk scoring
- Priority classification
- Vehicle feasibility suggestions
- Delay explanations

### Explicit Restrictions
- Cannot auto-approve shipments
- Cannot auto-reject shipments
- Cannot override human decisions
- Cannot operate without explanation

---

## 7. Decision Authority Matrix

| Action / Role | Seller | Manager | Supervisor | AI |
|-------------|--------|---------|------------|----|
| Create shipment | ✅ | ❌ | ❌ | ❌ |
| View risk score | ✅ | ✅ | ✅ | ❌ |
| Approve shipment | ❌ | ✅ | ❌ | ❌ |
| Override AI | ❌ | ✅ | ❌ | ❌ |
| Provide explanation | ❌ | ✅ | ❌ | ❌ |
| View analytics | ❌ | ✅ | ✅ | ❌ |
| Change system rules | ❌ | ❌ | ❌ | ❌ |

---

## 8. Override Ownership & Accountability

- Every override must:
  - Be initiated by a Manager
  - Include a human-readable reason
  - Be logged permanently

- Overrides are reviewed by Supervisors for governance, not punishment.

---

## 9. Human-in-the-Loop Guarantee

At no point does the system:
- Make irreversible decisions
- Hide reasoning from humans
- Remove human authority

Human judgment is always the final checkpoint.

---

End of document.
