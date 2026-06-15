import subprocess
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
CHECKER_PATH = BASE_DIR / "logic" / "checker.pl"


def run_prolog_query(query: str) -> str:
    """
    Runs a Prolog query against checker.pl and returns printed output.
    """

    command = [
        "swipl",
        "-q",
        "-s",
        str(CHECKER_PATH),
        "-g",
        query,
    ]

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"Prolog error:\n{result.stderr}"
        )

    return result.stdout.strip()


def classify_formula(formula: str) -> str:
    """
    Classifies a propositional formula as:
    valid, unsatisfiable, or contingent.
    """

    query = f"classify({formula}, Answer), write(Answer), halt."
    return run_prolog_query(query)

def equivalent_formulas(formula_a: str, formula_b: str) -> bool:
    query = (
        f"(equivalent({formula_a}, {formula_b}) "
        f"-> write(true); write(false)), halt."
    )
    return run_prolog_query(query) == "true"


def entails_formula(premises: list[str], conclusion: str) -> bool:
    premises_text = "[" + ",".join(premises) + "]"
    query = (
        f"(entails({premises_text}, {conclusion}) "
        f"-> write(true); write(false)), halt."
    )
    return run_prolog_query(query) == "true"


def consistent_with_formula(formula: str, sentence_set: list[str]) -> bool:
    set_text = "[" + ",".join(sentence_set) + "]"
    query = (
        f"(consistent_with({formula}, {set_text}) "
        f"-> write(true); write(false)), halt."
    )
    return run_prolog_query(query) == "true"

if __name__ == "__main__":
    print("Classification tests:")
    print(classify_formula("or(imp(p,q), imp(q,p))"))
    print(classify_formula("and(p, not(p))"))
    print(classify_formula("and(imp(p,q), imp(p,not(q)))"))

    print("\nEquivalence test:")
    print(equivalent_formulas(
        "imp(p, imp(q,r))",
        "imp(and(p,q), r)"
    ))

    print("\nEntailment test:")
    print(entails_formula(
        ["imp(p,r)"],
        "imp(p, or(q,r))"
    ))

    print("\nConsistency test:")
    print(consistent_with_formula(
        "not(r)",
        ["imp(p,r)", "imp(q,r)", "or(p,q)"]
    ))