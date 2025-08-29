from flask import Flask, request, url_for, Blueprint, redirect, render_template
from app.models import Words
from app.extensions import db


dict_bp = Blueprint("dict_bp", __name__)

@dict_bp.route("/dictionary")
def dict_home():
    import string
    letters = list(string.ascii_uppercase)
    return render_template("dict_home.html", letters=letters)

@dict_bp.route("/dictionary/<letter>")
def dict_by_letter(letter):
    words = Words.query.filter(Words.word.ilike(f"{letter}%"))\
                       .order_by(Words.word.asc()).all()
    return render_template("dict_by_letter.html", letter=letter.upper(), words=words)
                
@dict_bp.route("/dictionary/word/<word>")
def dict_word(word):
    entry = Words.query.filter_by(word=word).first_or_404()
    return render_template("dict_word.html", entry=entry)

@dict_bp.route("/search")
def dict_search():
    query = request.args.get("q", "").strip()
    words = []
    if query:
        words = (
            Words.query
            .filter(Words.word.ilike(f"%{query}%"))
            .order_by(Words.word.asc())
            .all()
        )
    return render_template("dict_home.html", words=words, query=query)