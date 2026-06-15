let currentProblemId = null;

async function generateProblem() {
  const response = await fetch("http://127.0.0.1:5001/generate-classification-problem");
  const problem = await response.json();

  currentProblemId = problem.id;

  document.getElementById("question").innerText = problem.question;
  document.getElementById("formula").innerText = problem.formula_display;
  document.getElementById("choices").style.display = "block";
  document.getElementById("result").innerText = "";
}

async function submitAnswer(answer) {
  const response = await fetch("http://127.0.0.1:5001/check-answer", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      id: currentProblemId,
      student_answer: answer
    })
  });

  const result = await response.json();

  if (result.correct) {
    document.getElementById("result").innerText =
      `Correct! Explanation: ${result.explanation}`;
  } else {
    document.getElementById("result").innerText =
      `Incorrect. Correct answer: ${result.correct_answer}. Explanation: ${result.explanation}`;
  }
}