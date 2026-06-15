import json
import os
import random
from typing import Literal

from anthropic import Anthropic
from dotenv import load_dotenv
from pydantic import BaseModel, Field, ValidationError


load_dotenv()

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


class ClassificationProblem(BaseModel):
    formula: str = Field(
        description="Formula in Prolog term syntax, e.g. imp(p,q)"
    )
    display: str = Field(
        description="Human-readable formula using symbols, e.g. p ⇒ q"
    )
    claimed_answer: Literal["valid", "contingent", "unsatisfiable"]
    explanation: str = Field(
        description="Brief explanation for the answer"
    )
    difficulty: Literal["easy", "medium", "hard"]


SYSTEM_PROMPT = """
You generate propositional logic practice problems for an Intro to Logic student.

Use ONLY this formula syntax in the formula field:
- Variables: p, q, r
- Negation: not(p)
- Conjunction: and(p,q)
- Disjunction: or(p,q)
- Implication: imp(p,q)
- Biconditional: iff(p,q)

Generate only classification problems where the student must classify the formula as:
valid, contingent, or unsatisfiable.

Rules:
- formula MUST be valid Prolog term syntax.
- formula MUST NOT contain symbols like ∧, ∨, ¬, ⇒, ⇔.
- display may use symbols.
- claimed_answer must be one of: valid, contingent, unsatisfiable.
- Keep the problem appropriate for a beginner learning propositional logic.
"""


def generate_classification_candidate() -> ClassificationProblem:
    schema = ClassificationProblem.model_json_schema()

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=600,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": f"""
Generate one ADVANCED propositional logic classification practice problem.

Random nonce: {random.randint(1, 1_000_000)}

The student must classify the formula as:
valid, contingent, or unsatisfiable.

Minimum difficulty requirements:
- Use 3 or 4 propositional variables chosen from p, q, r, s.
- Use at least 6 logical connectives total.
- Use at least one biconditional: iff(...,...)
- Use at least one implication nested inside another larger expression.
- Use at least one negation applied to a variable or subformula.
- Use at least one conjunction and one disjunction.
- The formula should be comparable in difficulty to:
  - iff(or(imp(not(r), and(not(p), not(q))), s), imp(or(p,q), or(r,s)))
  - iff(and(p, imp(q,r)), imp(or(not(p), q), and(p,r)))
- Do NOT copy those examples exactly.
- Avoid simple named laws like excluded middle, non-contradiction, or basic contraposition.
- Avoid formulas where the answer is visually obvious.
- The problem should require multiple truth-table rows or careful logical simplification.
- The claimed_answer may be valid, contingent, or unsatisfiable.
- Keep the explanation concise but specific.
"""

            }
        ],
        tools=[
            {
                "name": "make_classification_problem",
                "description": "Create one propositional logic classification problem.",
                "input_schema": schema,
            }
        ],
        tool_choice={
            "type": "tool",
            "name": "make_classification_problem"
        },
    )

    for block in response.content:
        if block.type == "tool_use" and block.name == "make_classification_problem":
            return ClassificationProblem.model_validate(block.input)

    raise ValueError("Claude did not return a classification problem tool call.")


if __name__ == "__main__":
    try:
        problem = generate_classification_candidate()
        print(problem.model_dump_json(indent=2))
    except ValidationError as e:
        print("Pydantic validation failed:")
        print(e)