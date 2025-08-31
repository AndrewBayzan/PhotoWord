from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.models import db, Words, WrongWord
from sqlalchemy import func

tests_bp = Blueprint("tests_bp", __name__, url_prefix="/tests")


@tests_bp.route("/settings", methods=["GET", "POST"])
def settings():
    """
    Страница настроек. POST сохраняет настройки в сессию и редиректит на /start.
    """
    if request.method == "POST":
        # получаем значения из формы
        source = request.form.get("source", "random")            # random | wrong
        levels = request.form.getlist("levels")                 # список уровней (может быть пуст)
        try:
            limit = int(request.form.get("limit", 10))
            if limit not in (10, 15):
                limit = 10
        except ValueError:
            limit = 10

        session["test_settings"] = {"source": source, "levels": levels, "limit": limit}
        return redirect(url_for("tests_bp.start"))

    # GET — показать форму настроек
    return render_template("setting.html")


@tests_bp.route("/start")
def start():
    """
    Собираем слова по настройкам и сохраняем список id в сессию.
    Обрабатываем случаи, когда в wrong_words недостаточно слов.
    """
    settings = session.get("test_settings")
    if not settings:
        flash("Настройки теста не заданы — выберите параметры.", "warning")
        return redirect(url_for("tests_bp.settings"))

    source = settings.get("source", "random")
    levels = settings.get("levels", [])   # list
    limit = settings.get("limit", 10)

    # --- источник: wrong (слова из wrong_words) ---
    if source == "wrong":
        user_id = session.get("user_id")
        if not user_id:
            flash("Требуется вход, чтобы использовать список ошибок.", "warning")
            return redirect(url_for("tests_bp.settings"))

        # безопасный способ: сначала взять id слов из WrongWord (user_db),
        # затем тянуть записи из Words (dictionary bind)
        wrong_rows = WrongWord.query.filter_by(user_id=user_id).all()
        wrong_ids = [r.word_id for r in wrong_rows]

        if not wrong_ids:
            flash("У вас нет слов в списке ошибок — выберите другой источник.", "info")
            return redirect(url_for("tests_bp.settings"))

        # если выбран фильтр по уровням — применим его при выборке слов
        q = Words.query.filter(Words.id.in_(wrong_ids))
        # levels может содержать e.g. 'MIX' — в этом случае не фильтруем
        if levels and "MIX" not in [l.upper() for l in levels]:
            q = q.filter(Words.cefr_level.in_(levels))

        words = q.order_by(func.random()).limit(limit).all()

        # если после фильтрации по уровням слов стало меньше, чем limit:
        if not words:
            flash("Слова на повторение по выбранным уровням не найдены.", "danger")
            return redirect(url_for("tests_bp.settings"))
        if len(words) < limit:
            flash(f"Найдено только {len(words)} слов для повторения — тест будет короче.", "info")

    else:
        # источник: random
        q = Words.query
        if levels and "MIX" not in [l.upper() for l in levels]:
            q = q.filter(Words.cefr_level.in_(levels))
        words = q.order_by(func.random()).limit(limit).all()
        if not words:
            flash("Не найдено слов по выбранным уровням.", "danger")
            return redirect(url_for("tests_bp.settings"))

    # сохраняем только id-ы слов в сессии (лучше не хранить объекты)
    session["test_word_ids"] = [w.id for w in words]
    # очищаем статистику (если была)
    session.pop("test_stats", None)
    return redirect(url_for("tests_bp.run", index=0))


@tests_bp.route("/run/<int:index>", methods=["GET"])
def run(index):
    """
    Показать одну карточку (index).
    Если слово отсутствует или пустое — пропускаем вперёд с флешем.
    """
    ids = session.get("test_word_ids")
    if not ids:
        flash("Тест не инициализирован. Сначала выберите настройки.", "warning")
        return redirect(url_for("tests_bp.settings"))

    # выход за пределы — на finish
    if index < 0 or index >= len(ids):
        return redirect(url_for("tests_bp.finish"))

    word = Words.query.get(ids[index])
    if not word:
        # что-то пошло не так: нет слова из списка — пропускаем его
        flash(f"Слово с id={ids[index]} не найдено — пропускаем.", "warning")
        return redirect(url_for("tests_bp.run", index=index + 1))

    word_text = (word.word or "").strip()
    if not word_text:
        flash("Слово пустое — пропускаю.", "warning")
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
    Проверка ответа. Валидация:
     - сессия/список слов существует
     - слово найдено
     - пользователь ввёл достаточно символов (или поле не пустое)
    Если ввод неполный — возвращаем на ту же карточку с флеш-сообщением.
    Также обновляем session['test_stats'] и вставляем WrongWord при ошибке (без дублирования).
    """
    ids = session.get("test_word_ids")
    if not ids:
        flash("Сессия теста потеряна. Сначала выберите настройки.", "warning")
        return redirect(url_for("tests_bp.settings"))

    if index < 0 or index >= len(ids):
        flash("Некорректный индекс карточки.", "danger")
        return redirect(url_for("tests_bp.settings"))

    word = Words.query.get(ids[index])
    if not word:
        flash("Слово не найдено.", "danger")
        return redirect(url_for("tests_bp.run", index=index + 1))

    # Получаем форму — поддерживаем два варианта:
    # 1) по-буквенные поля name="letters" -> getlist("letters")
    # 2) fallback: одно поле name="letters" (noscript) -> get("letters")
    letters = request.form.getlist("letters")
    if not letters:
        single = request.form.get("letters", "")
        # если пользователь ввёл всё слово в одном поле, разобьём на буквы
        if single:
            letters = list(single)
        else:
            letters = []

    # очистка пробелов
    letters = [l.strip() for l in letters]

    correct = (word.word or "").strip()
    # валидация: пользователь должен ввести ровно столько символов, сколько длина слова,
    # и все поля не должны быть пустыми
    if len(letters) != len(correct) or any(ch == "" for ch in letters):
        flash("Введите все буквы слова (каждое поле должно быть заполнено).", "warning")
        return redirect(url_for("tests_bp.run", index=index))

    user_answer = "".join(letters).strip().lower()
    correct_answer = correct.lower()
    is_correct = user_answer == correct_answer

    # обновляем статистику в сессии
    stats = session.get("test_stats", {"correct": 0, "wrong": 0, "total": len(ids)})
    if is_correct:
        stats["correct"] += 1
    else:
        stats["wrong"] += 1
    session["test_stats"] = stats

    # если неверно и пользователь залогинен — добавляем в WrongWord, если ещё нет
    user_id = session.get("user_id")
    if not is_correct and user_id:
        try:
            existing = WrongWord.query.filter_by(user_id=user_id, word_id=word.id).first()
            if not existing:
                db.session.add(WrongWord(user_id=user_id, word_id=word.id))
            else:
                # при необходимости можно обновить timestamp/счётчик; здесь просто оставим запись
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
                current_app.logger.exception("Ошибка при записи WrongWord: %s", e)
            flash("Не удалось сохранить статистику ошибки (серверная ошибка).", "danger")

    # показываем экран с обратной связью
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
    Финальный экран со статистикой. Очищаем временные тестовые данные.
    """
    stats = session.get("test_stats", {"correct": 0, "wrong": 0, "total": 0})
    # очищаем сессию, чтобы следующий тест начинался с нуля
    session.pop("test_stats", None)
    session.pop("test_word_ids", None)
    session.pop("test_settings", None)
    return render_template("finish.html", stats=stats)
