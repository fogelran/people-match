import os
from typing import Any, Dict

from flask import Flask, redirect, render_template, request, url_for

from ..matching_logic.people_search import PeopleSearch

app = Flask(__name__, template_folder="templates")

# A single in-memory store for demo purposes.
people_search = PeopleSearch()


def _render_home(**extra_context: Dict[str, Any]):
    base_context = {
        "questions": people_search.get_questions(),
        "demo_matches": people_search.search({"Do you like pets?": True}),
    }
    focus_user = extra_context.get("focus_user", "")
    total_questions = len(base_context["questions"])
    answered_status: Dict[str, bool] = {}
    skipped_questions = set()
    answered_count = 0
    if focus_user:
        answered_status = people_search.get_questions_with_answered_status(focus_user)
        answered_count = sum(1 for answered in answered_status.values() if answered)
        skipped_questions = people_search.get_skipped_questions(focus_user)
        base_context.update(
            {
                "user_answers": people_search.get_user_answers(focus_user),
                "user_preferences": people_search.get_user_questions(focus_user),
                "answered_status": answered_status,
                "skipped_questions": skipped_questions,
            }
        )
    base_context.update(
        {
            "answered_count": answered_count,
            "total_questions": total_questions,
            "progress_percent": int((answered_count / total_questions) * 100) if total_questions else 0,
        }
    )
    base_context.update(extra_context)
    return render_template("home.html", **base_context)


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
        people_search.register_user(name, details={"tagline": "Demo explorer"})
        for question, answer in answers.items():
            people_search.answer_question(name, question, answer)
        # Give everyone a single preference to enable best match logic.
        people_search.add_user_question(name, "Do you like pets?", True)


_seed_demo_data()


@app.route("/", methods=["GET"])
def index():
    focus_user = request.args.get("focus_user", "").strip()
    suggested_question = ""
    question_status = ""

    if focus_user:
        try:
            people_search.register_user(focus_user)
            suggested_question = people_search.get_new_question_for_user(focus_user)
            if not suggested_question:
                question_status = f"{focus_user} has answered every question so far."
        except ValueError:
            question_status = "A name is required to personalize your feed."
        except KeyError:
            question_status = "Please sign in first to start answering."

    return _render_home(
        focus_user=focus_user,
        suggested_question=suggested_question,
        question_status=question_status,
    )


@app.route("/register", methods=["POST"])
def register():
    user_name = request.form.get("user_name", "").strip()
    profile_image_url = request.form.get("profile_image_url", "").strip() or None
    tagline = request.form.get("tagline", "").strip()

    if user_name:
        details = {"tagline": tagline} if tagline else {}
        people_search.register_user(user_name, profile_image_url=profile_image_url, details=details)
    return redirect(url_for("index", focus_user=user_name))


@app.route("/ask", methods=["POST"])
def ask_question():
    user_name = request.form.get("user_name", "").strip()
    question_text = request.form.get("question_text", "").strip()
    expected_answer = request.form.get("expected_answer") == "yes"

    if user_name and question_text:
        people_search.register_user(user_name)
        people_search.add_user_question(user_name, question_text, expected_answer)
    return redirect(url_for("index", focus_user=user_name))


@app.route("/answer", methods=["POST"])
def answer_question():
    user_name = request.form.get("user_name", "").strip()
    question_text = request.form.get("question_text", "").strip()
    action = request.form.get("answer_action", "yes")
    answer = action == "yes"

    if user_name and question_text:
        people_search.register_user(user_name)
        if action == "skip":
            people_search.skip_question(user_name, question_text)
        else:
            people_search.answer_question(user_name, question_text, answer)
    return redirect(url_for("index", focus_user=user_name))


@app.route("/best-match", methods=["POST"])
def best_match():
    user_name = request.form.get("user_name", "").strip()
    match_name = ""
    if user_name:
        people_search.register_user(user_name)
        match_name = people_search.best_match_for_user(user_name)

    focus_user = user_name
    suggested_question = people_search.get_new_question_for_user(focus_user) if focus_user else ""
    return _render_home(
        focus_user=focus_user,
        suggested_question=suggested_question,
        match_name=match_name,
    )


@app.route("/search", methods=["POST"])
def search():
    filters: Dict[str, bool] = {}
    for index in range(1, 4):
        question = request.form.get(f"question_{index}", "").strip()
        desired_answer = request.form.get(f"answer_{index}")
        if question and desired_answer in ("yes", "no"):
            filters[question] = desired_answer == "yes"

    results = people_search.search(filters)
    focus_user = request.form.get("user_name", "").strip()
    suggested_question = people_search.get_new_question_for_user(focus_user) if focus_user else ""
    return _render_home(
        results=results,
        applied_filters=filters,
        focus_user=focus_user,
        suggested_question=suggested_question,
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=True)
