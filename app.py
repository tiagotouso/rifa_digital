from flask import Flask, render_template, request, redirect, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "rifa_secreta_123"

os.makedirs("data", exist_ok=True)
DB = os.path.join("data", "database.db")

# -----------------------------
# 📌 Criar banco automaticamente
# -----------------------------
def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS rifa (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT,
            telefone TEXT,
            numero INTEGER UNIQUE
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# -----------------------------
# 🔁 Recursividade para validar números
# -----------------------------
def validar_numeros(lista, index=0):
    if index >= len(lista):
        return True
    
    numero = lista[index]
    
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT * FROM rifa WHERE numero = ?", (numero,))
    existe = c.fetchone()
    conn.close()

    if existe:
        return False
    
    return validar_numeros(lista, index + 1)

# -----------------------------
# 🏠 Cadastro
# -----------------------------
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        session["nome"] = request.form["nome"]
        session["telefone"] = request.form["telefone"]
        return redirect("/numeros")
    
    return render_template("index.html")

# -----------------------------
# 🎯 Escolha dos números
# -----------------------------
@app.route("/numeros", methods=["GET", "POST"])
def numeros():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT numero FROM rifa")
    ocupados = [row[0] for row in c.fetchall()]
    conn.close()

    if request.method == "POST":
        escolhidos = request.form.getlist("numeros")
        escolhidos = list(map(int, escolhidos))

        if not validar_numeros(escolhidos):
            return "❌ Um dos números já foi escolhido! Volte e tente novamente."

        session["numeros"] = escolhidos
        return redirect("/pagamento")

    return render_template("numeros.html", ocupados=ocupados)

# -----------------------------
# 💰 Pagamento
# -----------------------------
@app.route("/pagamento", methods=["GET", "POST"])
def pagamento():
    if "numeros" not in session:
        return redirect("/")

    if request.method == "POST":
        numeros = session["numeros"]

        # Verifica novamente antes de salvar
        if not validar_numeros(numeros):
            return "⚠️ Número já foi comprado por outra pessoa!"

        conn = sqlite3.connect(DB)
        c = conn.cursor()

        for n in numeros:
            c.execute(
                "INSERT INTO rifa (nome, telefone, numero) VALUES (?, ?, ?)",
                (session["nome"], session["telefone"], n)
            )

        conn.commit()
        conn.close()

        return redirect("/obrigado")

    return render_template("pagamento.html", numeros=session["numeros"])

# -----------------------------
# 🎉 Agradecimento
# -----------------------------
@app.route("/obrigado")
def obrigado():
    session.clear()
    return render_template("obrigado.html")

# -----------------------------
# 🌐 Configuração de Base Path / Proxy Reverso (/rifa)
# -----------------------------
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.exceptions import NotFound

# Isso embute a aplicação do Flask dentro do prefixo /rifa
# Fazendo com que todas as rotas e url_for automaticamente respeitem esse fallback.
app.wsgi_app = DispatcherMiddleware(
    NotFound(),
    {"/rifa": app.wsgi_app}
)

# -----------------------------
if __name__ == "__main__":
    app.run(debug=True)