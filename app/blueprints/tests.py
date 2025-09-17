from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app
from app.supabase_api import users_db, dictionary_db
import random

tests_bp = Blueprint("tests_bp", __name__, url_prefix="/tests")


@tests_bp.route("/settings", methods=["GET", "POST"])
def settings():
    """
    Settings page. POST saves settings to session and redirects to /start.
    """
    if request.method == "POST":
        # get values from form
        source = request.form.get("source", "random")            # random | wrong
        levels = request.form.getlist("levels")                  # list of levels (can be empty)
        try:
            limit = int(request.form.get("limit", 10))
            if limit not in (10, 15):
                limit = 10
        except ValueError:
            limit = 10

        session["test_settings"] = {"source": source, "levels": levels, "limit": limit}
        return redirect(url_for("tests_bp.start"))

    # GET — show settings form
    return render_template("setting.html")


@tests_bp.route("/start")
def start():
    """
    Collect words by settings and save list of ids to session.
    Handle cases when there are not enough words in wrong_words.
    """
    settings = session.get("test_settings")
    if not settings:
        flash("Quiz settings not set — please choose parameters.", "warning")
        return redirect(url_for("tests_bp.settings"))

    source = settings.get("source", "random")
    levels = settings.get("levels", [])   # list
    limit = settings.get("limit", 10)

    # --- source: wrong (words from wrong_words) ---
    if source == "wrong":
        user_id = session.get("user_id")
        if not user_id:
            flash("Login required to use incorrect words list.", "warning")
            return redirect(url_for("tests_bp.settings"))

        # Get user"s wrong words
        params = {"user_id": f"eq.{user_id}"}
        wrong_words = users_db.get("wrong_words", params=params)
        if not wrong_words:
            flash("You have no words in the incorrect list — choose another source.", "info")
            return redirect(url_for("tests_bp.settings"))

        wrong_ids = [w["word_id"] for w in wrong_words]

        # Get words from dictionary
        words = []
        for word_id in wrong_ids:
            params = {"id": f"eq.{word_id}"}
            if levels and "MIX" not in [l.upper() for l in levels]:
                params["cefr_level"] = f"in.({",".join(levels)})"
            word = dictionary_db.get("words", params=params)
            if word:
                words.extend(word)

        # Shuffle and limit count
        random.shuffle(words)
        words = words[:limit]

        if not words:
            flash("No words found for review at selected levels.", "danger")
            return redirect(url_for("tests_bp.settings"))
        if len(words) < limit:
            flash(f"Found only {len(words)} words for review — quiz will be shorter.", "info")

    # --- source: random (words from dictionary) ---
    else:
        # Get random words
        params = {}
        if levels and "MIX" not in [l.upper() for l in levels]:
            params["cefr_level"] = f"in.({",".join(levels)})"
        words = dictionary_db.get("words", params=params)
        
        if not words:
            flash("No words found for selected levels.", "danger")
            return redirect(url_for("tests_bp.settings"))
            
        # Shuffle and limit count
        random.shuffle(words)
        words = words[:limit]

    # Save word IDs to session
    session["test_word_ids"] = [w["id"] for w in words]
    session.pop("test_stats", None)
    return redirect(url_for("tests_bp.run", index=0))


@tests_bp.route("/run/<int:index>", methods=["GET"])
def run(index):
    """
    Show one card (index).
    If word is missing or empty — skip forward with flash.
    """
    ids = session.get("test_word_ids")
    if not ids:
        flash("Quiz not initialized. Please select settings first.", "warning")
        return redirect(url_for("tests_bp.settings"))

    if index < 0 or index >= len(ids):
        return redirect(url_for("tests_bp.finish"))

    # Get word by ID
    params = {"id": f"eq.{ids[index]}"}
    words = dictionary_db.get("words", params=params)
    if not words:
        flash(f"Word with id={ids[index]} not found — skipping.", "warning")
        return redirect(url_for("tests_bp.run", index=index + 1))

    word = words[0]
    word_text = (word["word"] or "").strip()
    if not word_text:
        flash("Word is empty — skipping.", "warning")
        return redirect(url_for("tests_bp.run", index=index + 1))

    return render_template(
        "run.html",
        word=word,
        current_index=index,
        total=len(ids),
        word_length=len(word_text)
    )


@tests_bp.route("/check/<int:index>", methods=["POST"])
def check_answer(index):
    """
    Check answer and update statistics
    """
    ids = session.get("test_word_ids")
    if not ids:
        flash("Quiz session lost. Please select settings first.", "warning")
        return redirect(url_for("tests_bp.settings"))

    if index < 0 or index >= len(ids):
        flash("Invalid card index.", "danger")
        return redirect(url_for("tests_bp.settings"))

    # Get word by ID
    params = {"id": f"eq.{ids[index]}"}
    words = dictionary_db.get("words", params=params)
    if not words:
        flash("Word not found.", "danger")
        return redirect(url_for("tests_bp.run", index=index + 1))

    word = words[0]

    # Get user"s answer
    letters = request.form.getlist("letters")
    if not letters:
        single = request.form.get("letters", "")
        letters = list(single) if single else []

    letters = [l.strip() for l in letters]
    correct = (word["word"] or "").strip()

    if len(letters) != len(correct) or any(ch == "" for ch in letters):
        flash("Please enter all letters of the word (each field must be filled).", "warning")
        return redirect(url_for("tests_bp.run", index=index))

    user_answer = "".join(letters).strip().lower()
    correct_answer = correct.lower()
    is_correct = user_answer == correct_answer

    # Update statistics
    stats = session.get("test_stats", {"correct": 0, "wrong": 0, "total": len(ids)})
    if is_correct:
        stats["correct"] += 1
    else:
        stats["wrong"] += 1
    session["test_stats"] = stats

    # If answer is wrong and user is logged in - add to wrong_words
    user_id = session.get("user_id")
    if not is_correct and user_id:
        try:
            # Check if entry exists
            params = {
                "user_id": f"eq.{user_id}",
                "word_id": f"eq.{word["id"]}"
            }
            existing = users_db.get("wrong_words", params=params)
            
            if not existing:
                # Add new entry
                wrong_word_data = {
                    "user_id": user_id,
                    "word_id": word["id"]
                }
                users_db.post("wrong_words", wrong_word_data)

        except Exception as e:
            current_app.logger.exception("Error writing wrong word: %s", e)
            flash("Failed to save error statistics (server error).", "danger")

    # Show results
    next_index = index + 1
    return render_template(
        "results.html",
        word=word,
        user_answer=user_answer,
        correct_answer=correct_answer,
        is_correct=is_correct,
        next_index=next_index,
        total=len(ids)
    )


@tests_bp.route("/finish", methods=["GET"])
def finish():
    """
    Final screen with statistics. Clear temporary test data.
    """
    stats = session.get("test_stats", {"correct": 0, "wrong": 0, "total": 0})
    session.pop("test_stats", None)
    session.pop("test_word_ids", None)
    session.pop("test_settings", None)
    return render_template("finish.html", stats=stats)
