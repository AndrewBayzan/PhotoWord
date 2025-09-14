from flask import Flask, request, url_for, Blueprint, redirect, render_template
from app.supabase_api import dictionary_db


dict_bp = Blueprint("dict_bp", __name__)

@dict_bp.route("/dictionary")
def dict_home():
    import string
    letters = list(string.ascii_uppercase)
    return render_template("dict_home.html", letters=letters)

@dict_bp.route("/dictionary/<letter>")
def dict_by_letter(letter):
    # Получаем слова по первой букве через REST API
    params = {"word": f"ilike.{letter}%", "order": "word.asc"}
    words = dictionary_db.get("words", params=params)
    return render_template("dict_by_letter.html", letter=letter.upper(), words=words)
                
@dict_bp.route("/dictionary/word/<word>")
def dict_word(word):
    params = {"word": f"eq.{word}"}
    entries = dictionary_db.get("words", params=params)
    entry = entries[0] if entries else None
    return render_template("dict_word.html", entry=entry)

@dict_bp.route("/search")
def dict_search():
    query = request.args.get("q", "").strip()
    words = []
    if query:
        params = {"word": f"ilike.%{query}%", "order": "word.asc"}
        words = dictionary_db.get("words", params=params)
    return render_template("dict_home.html", words=words, query=query)