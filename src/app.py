import os
from typing import Dict

from flask import Flask, redirect, render_template, request, url_for

from .people_search import PeopleSearch

app = Flask(__name__, template_folder="templates")

# A single in-memory store for demo purposes.
people_search = PeopleSearch()


def _ensure_user(name: str):
    if not name:
        raise ValueError("A user name is required")
    try:
        people_search.get_user(name)
    except KeyError:
        people_search.add_user(name)


def _seed_demo_data():
    demo_people = {
        "Alex": {
            "Are you a morning person?": True,
            "Do you like pets?": True,
            "Are you looking for a long-term relationship?": True,
        },
        "Jordan": {
            "Are you a morning person?": False,
            "Do you like pets?": False,
            "Do you enjoy outdoor activities?": True,
        },
        "Taylor": {
            "Are you a morning person?": True,
            "Do you like pets?": True,
            "Do you want kids in the future?": False,
        },
    }
    for name, answers in demo_people.items():
        if name not in people_search._users:
            people_search.add_user(name)
        for question, answer in answers.items():
            people_search.answer_question(name, question, answer)


_seed_demo_data()


@app.route("/", methods=["GET"])
def index():
    available_questions = people_search.get_questions()
    demo_matches = people_search.search({"Do you like pets?": True})
    return render_template(
        "home.html",
        questions=available_questions,
        demo_matches=demo_matches,
    )


@app.route("/ask", methods=["POST"])
def ask_question():
    user_name = request.form.get("user_name", "").strip()
    question_text = request.form.get("question_text", "").strip()
    expected_answer = request.form.get("expected_answer") == "yes"

    if user_name and question_text:
        _ensure_user(user_name)
        people_search.add_user_question(user_name, question_text, expected_answer)
    return redirect(url_for("index"))


@app.route("/answer", methods=["POST"])
def answer_question():
    user_name = request.form.get("user_name", "").strip()
    question_text = request.form.get("question_text", "").strip()
    answer = request.form.get("answer") == "yes"

    if user_name and question_text:
        _ensure_user(user_name)
        people_search.answer_question(user_name, question_text, answer)
    return redirect(url_for("index"))


@app.route("/search", methods=["POST"])
def search():
    filters: Dict[str, bool] = {}
    for index in range(1, 4):
        question = request.form.get(f"question_{index}", "").strip()
        desired_answer = request.form.get(f"answer_{index}")
        if question and desired_answer in ("yes", "no"):
            filters[question] = desired_answer == "yes"

    results = people_search.search(filters)
    available_questions = people_search.get_questions()
    demo_matches = people_search.search({"Do you like pets?": True})
    return render_template(
        "home.html",
        questions=available_questions,
        results=results,
        applied_filters=filters,
        demo_matches=demo_matches,
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=True)
