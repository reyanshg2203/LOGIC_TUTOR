from flask import Flask, request, jsonify
from flask_cors import CORS
import uuid
from llm_generator import generate_classification_candidate
from formula_display import formula_to_display

from prolog_bridge import (
    classify_formula,
    equivalent_formulas,
    entails_formula,
    consistent_with_formula,
)

app = Flask(__name__)
CORS(app)

PROBLEMS = {}


@app.route("/")
def home():
    return jsonify({
        "message": "Logic Tutor backend is running!"
    })


@app.route("/generate-classification-problem", methods=["GET"])
@app.route("/generate-classification-problem", methods=["GET"])
def generate_classification_problem():
    """
    Claude generates a candidate problem.
    Pydantic validates the structure.
    Prolog validates the logical answer.
    Only verified problems are shown to the student.
    """

    max_attempts = 5

    for attempt in range(max_attempts):
        try:
            candidate = generate_classification_candidate()

            formula = candidate.formula
            display = formula_to_display(formula)
            claimed_answer = candidate.claimed_answer

            verified_answer = classify_formula(formula)

            print("Candidate:", formula)
            print("LLM claimed:", claimed_answer)
            print("Prolog verified:", verified_answer)

        except Exception as e:
            print(f"Generation attempt {attempt + 1} failed: {e}")
            continue

        if verified_answer == claimed_answer:
            problem_id = str(uuid.uuid4())

            PROBLEMS[problem_id] = {
                "type": "classification",
                "formula": formula,
                "display": display,
                "correct_answer": verified_answer,
                "explanation": candidate.explanation,
                "difficulty": candidate.difficulty,
            }

            return jsonify({
                "id": problem_id,
                "type": "classification",
                "question": "Classify the following formula as valid, contingent, or unsatisfiable.",
                "formula_display": display,
                "choices": ["valid", "contingent", "unsatisfiable"],
                "difficulty": candidate.difficulty,
            })

        print("Rejected because LLM answer did not match Prolog.")

    return jsonify({
        "error": "Could not generate a verified problem after several attempts."
    }), 500


@app.route("/check-answer", methods=["POST"])
def check_answer():
    data = request.get_json()

    problem_id = data.get("id")
    student_answer = data.get("student_answer")

    if problem_id not in PROBLEMS:
        return jsonify({
            "error": "Problem not found."
        }), 404

    problem = PROBLEMS[problem_id]
    correct_answer = problem["correct_answer"]

    return jsonify({
    "correct": student_answer == correct_answer,
    "student_answer": student_answer,
    "correct_answer": correct_answer,
    "explanation": problem.get("explanation", "")
})



@app.route("/verify-classification", methods=["POST"])
def verify_classification():
    """
    This route lets us directly ask:
    What is the classification of this formula?
    """

    data = request.get_json()
    formula = data.get("formula")

    if not formula:
        return jsonify({
            "error": "Missing formula."
        }), 400

    answer = classify_formula(formula)

    return jsonify({
        "formula": formula,
        "classification": answer
    })


@app.route("/verify-equivalence", methods=["POST"])
def verify_equivalence():
    data = request.get_json()

    formula_a = data.get("formula_a")
    formula_b = data.get("formula_b")

    if not formula_a or not formula_b:
        return jsonify({
            "error": "Missing formula_a or formula_b."
        }), 400

    result = equivalent_formulas(formula_a, formula_b)

    return jsonify({
        "formula_a": formula_a,
        "formula_b": formula_b,
        "equivalent": result
    })


@app.route("/verify-entailment", methods=["POST"])
def verify_entailment():
    data = request.get_json()

    premises = data.get("premises")
    conclusion = data.get("conclusion")

    if not premises or not conclusion:
        return jsonify({
            "error": "Missing premises or conclusion."
        }), 400

    result = entails_formula(premises, conclusion)

    return jsonify({
        "premises": premises,
        "conclusion": conclusion,
        "entails": result
    })


@app.route("/verify-consistency", methods=["POST"])
def verify_consistency():
    data = request.get_json()

    formula = data.get("formula")
    sentence_set = data.get("sentence_set")

    if not formula or sentence_set is None:
        return jsonify({
            "error": "Missing formula or sentence_set."
        }), 400

    result = consistent_with_formula(formula, sentence_set)

    return jsonify({
        "formula": formula,
        "sentence_set": sentence_set,
        "consistent": result
    })


if __name__ == "__main__":
    app.run(debug=True, port=5001)