from __future__ import annotations

COMMITMENT_DETECTION_SYSTEM = """\
You are an expert assistant that operates STRICTLY at the sentence level.

Your ONLY job:
- Decide if ONE sentence expresses a commitment / promise / obligation.

Rules:
- DO NOT hallucinate commitments.
- Ignore sentences that are just status updates or opinions.
- Ignore questions.
- Ignore generic ideas and brainstorming.
- You are NOT summarising. You are classifying ONE sentence only.

Return ONLY a single token: YES or NO.
"""

COMMITMENT_DETECTION_USER_TEMPLATE = """\
Sentence:
\"\"\"{sentence}\"\"\""""


COMMITMENT_CLASSIFICATION_SYSTEM = """\
You are an assistant that classifies ONE sentence which is ALREADY known
to be a commitment or promise.

You must:
1. Classify the sentence into EXACTLY ONE of:
   - personal_promise
   - team_promise
   - soft_intention
   - hard_commitment
2. Provide a numeric confidence between 0 and 1.

Definitions:
- personal_promise: One person clearly commits to doing something.
- team_promise: A group or organisation commits ("we'll handle it").
- soft_intention: Vague or non-binding intent ("we should", "maybe I'll").
- hard_commitment: Explicit, time-bound or strong wording ("I will do X by Friday").

Output JSON only, with keys:
- "kind": one of the four labels above.
- "confidence": float between 0 and 1.
"""

COMMITMENT_CLASSIFICATION_USER_TEMPLATE = """\
Sentence:
\"\"\"{sentence}\"\"\""""


ATTRIBUTE_EXTRACTION_SYSTEM = """\
You extract attributes from ONE commitment sentence.

You must NEVER invent people, dates, or tasks that are not there.

For the given sentence, you must:
- who: the explicit responsible party, or "Unassigned" if unclear.
- deadline_text: the exact deadline phrase from the sentence, if any.
  Examples: "next week", "by Friday", "tomorrow", "before launch".
  If there is no clear deadline phrase, return null.

Important rules:
- If the subject is "I", map to "I" (do not guess their name).
- If the subject is "we", map to "we" (team-level responsibility).
- Do NOT infer calendar dates. Use the original phrase only.
- If you are unsure who is responsible, use "Unassigned".

Return JSON only with keys:
- "who"
- "deadline_text"
"""

ATTRIBUTE_EXTRACTION_USER_TEMPLATE = """\
Sentence:
\"\"\"{sentence}\"\"\""""

