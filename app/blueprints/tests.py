from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.models import db, Words, WrongWord
from sqlalchemy import func

tests_bp = Blueprint("tests_bp", __name__, url_prefix="/tests")


@tests_bp.route("/settings", methods=["GET", "POST"])
def settings():
    """
    Settings page. POST saves settings to session and redirects to /start.
    """
    if request.method == "POST":
        # get values from form
        source = request.form.get("source", "random")            # random | wrong
        levels = request.form.getlist("levels")                 # list of levels (can be empty)
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

        # safe way: first get word ids from WrongWord (user_db),
        # then pull records from Words (dictionary bind)
        wrong_rows = WrongWord.query.filter_by(user_id=user_id).all()
        wrong_ids = [r.word_id for r in wrong_rows]

        if not wrong_ids:
            flash("You have no words in the incorrect list — choose another source.", "info")
            return redirect(url_for("tests_bp.settings"))

        # if level filter is selected — apply it when selecting words
        q = Words.query.filter(Words.id.in_(wrong_ids))
        # levels can contain e.g. 'MIX' — in this case we don't filter
        if levels and "MIX" not in [l.upper() for l in levels]:
            q = q.filter(Words.cefr_level.in_(levels))

        words = q.order_by(func.random()).limit(limit).all()

        # if after filtering by levels words became less than limit:
        if not words:
            flash("No words found for review at selected levels.", "danger")
            return redirect(url_for("tests_bp.settings"))
        if len(words) < limit:
            flash(f"Found only {len(words)} words for review — quiz will be shorter.", "info")

    else:
        # source: random
        q = Words.query
        if levels and "MIX" not in [l.upper() for l in levels]:
            q = q.filter(Words.cefr_level.in_(levels))
        words = q.order_by(func.random()).limit(limit).all()
        if not words:
            flash("No words found for selected levels.", "danger")
            return redirect(url_for("tests_bp.settings"))

    # save only word ids in session (better not to store objects)
    session["test_word_ids"] = [w.id for w in words]
    # clear statistics (if there was any)
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

    # out of bounds — go to finish
    if index < 0 or index >= len(ids):
        return redirect(url_for("tests_bp.finish"))

    word = Words.query.get(ids[index])
    if not word:
        # something went wrong: no word from list — skip it
        flash(f"Word with id={ids[index]} not found — skipping.", "warning")
        return redirect(url_for("tests_bp.run", index=index + 1))

    word_text = (word.word or "").strip()
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
    Check answer. Validation:
     - session/word list exists
     - word found
     - user entered enough characters (or field not empty)
    If input is incomplete — return to the same card with flash message.
    Also update session['test_stats'] and insert WrongWord on error (without duplication).
    """
    ids = session.get("test_word_ids")
    if not ids:
        flash("Quiz session lost. Please select settings first.", "warning")
        return redirect(url_for("tests_bp.settings"))

    if index < 0 or index >= len(ids):
        flash("Invalid card index.", "danger")
        return redirect(url_for("tests_bp.settings"))

    word = Words.query.get(ids[index])
    if not word:
        flash("Word not found.", "danger")
        return redirect(url_for("tests_bp.run", index=index + 1))

    # Get form — support two options:
    # 1) letter-by-letter fields name="letters" -> getlist("letters")
    # 2) fallback: single field name="letters" (noscript) -> get("letters")
    letters = request.form.getlist("letters")
    if not letters:
        single = request.form.get("letters", "")
        # if user entered the whole word in one field, split into letters
        if single:
            letters = list(single)
        else:
            letters = []

    # clean spaces
    letters = [l.strip() for l in letters]

    correct = (word.word or "").strip()
    # validation: user must enter exactly as many characters as word length,
    # and all fields must not be empty
    if len(letters) != len(correct) or any(ch == "" for ch in letters):
        flash("Please enter all letters of the word (each field must be filled).", "warning")
        return redirect(url_for("tests_bp.run", index=index))

    user_answer = "".join(letters).strip().lower()
    correct_answer = correct.lower()
    is_correct = user_answer == correct_answer

    # update statistics in session
    stats = session.get("test_stats", {"correct": 0, "wrong": 0, "total": len(ids)})
    if is_correct:
        stats["correct"] += 1
    else:
        stats["wrong"] += 1
    session["test_stats"] = stats

    # if incorrect and user is logged in — add to WrongWord if not already there
    user_id = session.get("user_id")
    if not is_correct and user_id:
        try:
            existing = WrongWord.query.filter_by(user_id=user_id, word_id=word.id).first()
            if not existing:
                db.session.add(WrongWord(user_id=user_id, word_id=word.id))
            else:
                # if needed can update timestamp/counter; here just leave the record
                pass
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            current_app = None
            try:
                from flask import current_app as _ca
                current_app = _ca
            except Exception:
                current_app = None
            if current_app:
                current_app.logger.exception("Error writing WrongWord: %s", e)
            flash("Failed to save error statistics (server error).", "danger")

    # show feedback screen
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
    # clear session so next test starts from zero
    session.pop("test_stats", None)
    session.pop("test_word_ids", None)
    session.pop("test_settings", None)
    return render_template("finish.html", stats=stats)
