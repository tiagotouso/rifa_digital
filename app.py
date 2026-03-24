from flask import Flask, render_template, request, redirect, session, url_for
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
    if not os.path.exists(DB):
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
# 🏠 Início (Página de Vendas)
# -----------------------------
@app.route("/")
def index():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT COUNT(DISTINCT numero) FROM rifa")
    vendidos = c.fetchone()[0]
    conn.close()
    
    total_numeros = 25
    disponiveis = max(0, total_numeros - vendidos)
    
    return render_template("index.html", disponiveis=disponiveis)

# -----------------------------
# 📝 Cadastro
# -----------------------------
@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    if request.method == "POST":
        session["nome"] = request.form["nome"]
        session["telefone"] = request.form["telefone"]
        return redirect(url_for("numeros"))
    
    return render_template("cadastro.html")

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
        return redirect(url_for("pagamento"))

    return render_template("numeros.html", ocupados=ocupados)

# -----------------------------
# 💰 Pagamento
# -----------------------------
@app.route("/pagamento", methods=["GET", "POST"])
def pagamento():
    if "numeros" not in session:
        return redirect(url_for("cadastro"))

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

        return redirect(url_for("obrigado"))

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
from werkzeug.middleware.proxy_fix import ProxyFix

# Usa ProxyFix para interpretar os headers X-Forwarded-* do Nginx.
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1, x_prefix=0)

# Middleware para resolver SCRIPT_NAME e PATH_INFO
# Permite rodar a base /rifa localmente e através do Nginx proxy_pass
class ReverseProxied(object):
    def __init__(self, app):
        self.app = app
    def __call__(self, environ, start_response):
        path_info = environ.get('PATH_INFO', '')

        # Se acessarem a raiz absoluta localmente (http://localhost:8599/)
        # redireciona automaticamente para /rifa/
        if path_info == '/' and not environ.get('HTTP_X_FORWARDED_FOR'):
            start_response('302 Found', [('Location', '/rifa/')])
            return [b'']

        # Fixa o prefixo de todos os links para /rifa
        environ['SCRIPT_NAME'] = '/rifa'

        # Se o acesso (local) já veio com o prefixo /rifa, nós cortamos para
        # que o roteador interno do Flask (que só conhece '/', '/cadastro') encontre a rota.
        if path_info.startswith('/rifa'):
            environ['PATH_INFO'] = path_info[5:] or '/'

        return self.app(environ, start_response)

app.wsgi_app = ReverseProxied(app.wsgi_app)

# -----------------------------
if __name__ == "__main__":

    app.run(host="0.0.0.0", port=8599)