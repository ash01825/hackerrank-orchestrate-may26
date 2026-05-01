from config.enums import Status

REPLY_THRESHOLD = 0.3  # hybrid score above this = replied (trusts retrieval over LLM confidence)

def decide_status(has_hard_risk, validation_result, top_hybrid_score):
    # 1. Hard risk keywords → always escalate
    if has_hard_risk:
        return Status.ESCALATED.value, "Escalated due to sensitive/risk keywords."

    # 2. No retrieval at all → handled upstream (deflection)
    if top_hybrid_score <= 0.0:
        return Status.ESCALATED.value, "No relevant evidence retrieved."

    val_ans = validation_result.get("answerable", "no")
    val_conf = float(validation_result.get("confidence", 0.0))
    val_reason = validation_result.get("reasoning", "")

    # 3. Strong retrieval → trust it, reply regardless of LLM confidence variance
    if top_hybrid_score >= REPLY_THRESHOLD:
        return Status.REPLIED.value, f"Retrieved with score {top_hybrid_score:.2f}."

    # 4. Weak retrieval + LLM says not answerable → escalate
    if val_ans != "yes":
        return Status.ESCALATED.value, f"Weak retrieval + validation failed: {val_reason}"

    # 5. Weak retrieval but LLM says yes → escalate (don't risk it)
    return Status.ESCALATED.value, f"Retrieval score too low ({top_hybrid_score:.2f})."
