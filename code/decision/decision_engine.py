from config.enums import Status

REPLY_THRESHOLD = 0.3

def decide_status(has_hard_risk, validation_result, top_hybrid_score):
    if has_hard_risk:
        return Status.ESCALATED.value, "Escalated due to sensitive/risk keywords."

    if top_hybrid_score <= 0.0:
        return Status.ESCALATED.value, "No relevant evidence retrieved."

    val_ans = validation_result.get("answerable", "no")
    val_reason = validation_result.get("reasoning", "")

    if top_hybrid_score >= REPLY_THRESHOLD:
        return Status.REPLIED.value, f"Retrieved with score {top_hybrid_score:.2f}."

    if val_ans != "yes":
        return Status.ESCALATED.value, f"Weak retrieval + validation failed: {val_reason}"

    return Status.ESCALATED.value, f"Retrieval score too low ({top_hybrid_score:.2f})."
