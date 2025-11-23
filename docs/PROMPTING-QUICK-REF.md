# SecAI Radar Prompting Quick Reference

> **Quick reference card** for common prompting patterns. See `PROMPTING-GUIDE.md` for full details.

---

## 🎯 Common Patterns

### Scoring Logic Development
```
Apply Chain of Verification (3 phases) to implement scoring for [scenario].
- Phase 1: Draft implementation
- Phase 2: List 3+ edge cases/errors (math, logic, security)
- Phase 3: Revised version with fixes + unit tests
```

### Security Architecture Review
```
Apply Adversarial Prompting to review [design]:
Attack from: security, scoring accuracy, compliance, operational, UX perspectives.
For each weakness: describe, likelihood, impact, mitigation.
```

### Validation Logic
```
Apply Strategic Edge-Case Learning:
- Learn 3 rejection examples + 1 pass example
- Evaluate new sample
- Identify pattern match and reasoning
```

### Feature Implementation
```
Use Meta-Prompting:
1. Design optimal prompt (role, input, output, verification)
2. Execute with SecAI Radar context
3. Apply Chain of Verification
4. Apply Multi-Persona review
```

### Troubleshooting
```
Apply Zero-to-Chain-of-Thought:
1. Problem statement
2. Relevant components/data
3. Likely causes (3)
4. Evidence needed
5. Recommendation
6. Validation steps
```

### Documentation
```
Apply Over-Instruction Template:
Do NOT summarize. Include:
- Implementation details with code
- Edge cases and failure modes
- Historical context
- Compliance/security notes
```

---

## 🚨 High-Risk Tasks (Default to Multiple Patterns)

**Scoring Algorithm Changes:**
1. Chain of Verification
2. Edge-case learning
3. Adversarial review

**Security/Architecture:**
1. Adversarial review
2. Multi-persona
3. Chain of Verification

**Validation Logic:**
1. Edge-case learning
2. Chain of Verification
3. Reasoning scaffold

---

## 📋 Quality Checklist

Before completion:
- [ ] Scoring: Math verified, edge cases tested, explainable
- [ ] Security: Tenant isolation, auth enforced, input validated
- [ ] Compliance: Evidence handling, audit trail
- [ ] Validation: Schema + business rules, clear errors
- [ ] Documentation: ADRs/wiki updated
- [ ] Tests: Unit + integration
- [ ] Explainability: Traceable scores

---

## 💡 Starter Commands

**For Scoring:**
> Apply Chain of Verification to [task]. Include edge cases and tests.

**For Security:**
> Apply Adversarial Prompting to review [design]. Attack from 5 perspectives.

**For Features:**
> Use Meta-Prompting to design and implement [feature]. Then verify and review.

**For Bugs:**
> Apply Zero-to-Chain-of-Thought to troubleshoot [issue]. Include causes, evidence, fixes.

**For Docs:**
> Apply Over-Instruction Template to document [topic]. No summarization.

---

## 🔗 Key Context Files

- **Architecture:** `docs/SEC_AI_Radar_Brief.md`
- **Scoring Policy:** `docs/adr/0004-scoring-policy-and-thresholds.md`
- **Evidence:** `docs/adr/0005-evidence-handling-and-retention.md`
- **Code:** `api/shared/scoring.py`, `api/shared/validate_seeds.py`

---

**Full Guide:** See `PROMPTING-GUIDE.md` for complete details and templates.

