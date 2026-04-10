from flask import Flask, request, redirect, url_for, session
import sqlite3
from flask import Flask, request, redirect, url_for
import random

app = Flask(__name__)
app.secret_key = "segredo_super_forte_123"

# =========================
# BANCO
# =========================

def conectar():
    return sqlite3.connect("banco.db")


def criar_tabelas():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS favoritos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    texto TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS prompts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    texto TEXT,
    usuario TEXT
    )
    """)
                   
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    senha TEXT
    )
    """)

    

    conn.commit()
    conn.close()


# =========================
# PROMPTS
# =========================

def carregar_prompts():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute(
    "SELECT id, texto FROM prompts WHERE usuario = ?", 
    (session["usuario"],)
)
    return cursor.fetchall()
    dados = cursor.fetchall()

    conn.close()
    return dados  



def salvar_prompt(texto, usuario):
    conn = conectar()
    cursor = conn.cursor()

    try:
        cursor.execute("INSERT INTO prompts (texto, usuario) VALUES (?, ?)", (texto, usuario))
        conn.commit()
    except:
        pass  

    conn.close()
 

def limpar_prompts():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM prompts")

    conn.commit()
    conn.close()


# =========================
# FAVORITOS
# =========================

def carregar_favoritos():
    conn = conectar()
    cursor = conn.cursor()


    cursor.execute("SELECT texto FROM favoritos")
    dados = cursor.fetchall()

    conn.close()
    return [d[0] for d in dados]


def salvar_favorito(texto):
    conn = conectar()
    cursor = conn.cursor()

    try:
        cursor.execute("INSERT INTO favoritos (texto) VALUES (?)", (texto,))
        conn.commit()
    except:
        pass

    conn.close()

def limpar_favoritos():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM favoritos")

    conn.commit()
    conn.close()


# =========================
# HOME
# =========================

@app.route("/", methods=["GET", "POST"])
def home():
    
    if "usuario" not in session:
        return redirect(url_for("login"))

    prompts = carregar_prompts() 
    favoritos = carregar_favoritos()

     # BUSCA
    if request.method == "POST":
        busca = request.form.get("busca", "").lower()
        if busca:
            prompts = [p for p in prompts if busca in p[1].lower()]

    lista = ""
    for p in prompts:
        id = p[0]
        texto = p[1]

        lista += f"""
        <div class="card">
            <span class="texto">{texto}</span>
            <span class="estrela" onclick="favoritar({id}, this)">⭐</span>
            <button onclick="excluir({id}, this)">❌</button>
            <button onclick="editar({id}, this)">✏️</button>
            <button onclick="copiarTexto(this)">📋</button>
        </div>
        """

    lista_fav = ""
    for f in favoritos:
        lista_fav += f"<p>⭐ {f}</p>" 

        menu = ""

    if "usuario" in session:
        menu = '<a href="/logout">🚪 Sair</a>'
    else:
        menu = '''
    <a href="/login">🔐 Login</a>
    <a href="/cadastro">📝 Cadastro</a>
    '''

    return f""" 
<html>

<head>
<style>

body {{
    font-family: Arial;
    color: white;
    padding: 20px;
    background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
    max-width: 900px;
    margin: auto;
}}

h1 {{
    text-align: center;
}}

.card {{
    background: #1e1e1e;
    padding: 15px;
    margin-bottom: 10px;
    border-radius: 10px;
    transition: 0.3s;
}}


.menu {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 15px 20px;
    background: rgba(0,0,0,0.3);
    border-radius: 12px;
    margin-bottom: 20px;
}}

.logo {{
    font-size: 22px;
    font-weight: bold;
}}

.menu-direita a {{
    margin-left: 15px;
    text-decoration: none;
    color: white;
    background: linear-gradient(45deg, #00c853, #00b0ff);
    padding: 8px 14px;
    border-radius: 8px;
    transition: 0.3s;
}}

.menu-direita a:hover {{
    transform: scale(1.1);
}}


h1 {{
    text-align: center;
}}



.card:hover {{
    transform: scale(1.02);
}}

.estrela {{
    cursor: pointer;
    margin-left: 10px;
}}

button {{
    margin-left: 5px;
    cursor: pointer;
}}

input {{
    padding: 10px;
    width: 60%;
    border-radius: 8px;
    border: none;
}}

.botao {{
    padding: 10px;
    border-radius: 8px;
    border: none;
    cursor: pointer;
    background: green;
    color: white;
}}

.limpar {{
    background: red;
    padding: 8px;
    border-radius: 8px;
    color: white;
    text-decoration: none;
}}

.busca-box {{
    display: flex;
    gap: 10px;
    margin: 20px 0;
}}

h2 {{
    margin-top: 30px;
}}

#lista-prompts, #lista_favoritos {{
    margin-top: 10px;
}}

.card {{
    display: flex;
    justify-content: space-between;
    align-items: center;
}}

.texto {{
    flex: 1;
}}

button {{
    background: #333;
    border: none;
    color: white;
    padding: 6px 10px;
    border-radius: 6px;
}}

button:hover {{
    background: #555;
}}

.gerar {{
    background: linear-gradient(45deg, #00c853, #64dd17);
}}


</style>
</head>

<body>


<div class="menu">

    <div class="logo">🚀 PromptKeeper</div>
    
<div class="menu-direita">
    {menu}
</div>

<form method="POST" class="busca-box">
    <input name="busca" id="busca" placeholder="🔍 Buscar...">
    <button type="submit" class="botao gerar">Buscar</button>
    <button type="button" class="botao gerar" onclick="gerarPrompt()">💡 Gerar</button>
</form>

<br>

<div style="margin-top:10px;">
    <a class="limpar" href="/limpar">🗑 Limpar tudo</a>
</div>

<h2>Prompts:</h2>
<div id="lista-prompts">
{lista}
</div>

<h2>⭐ Favoritos:</h2>
<div id="lista_favoritos">
{lista_fav}
</div>

<script>

function copiarTexto(botao) {{
    let texto = botao.parentElement.querySelector(".texto").innerText;
    navigator.clipboard.writeText(texto);
    alert("Copiado!");
}}

function favoritar(id, botao) {{
    fetch(`/favoritar_ajax/${{id}}`)
    .then(() => location.reload());
}}

function excluir(id, botao) {{
    fetch("/excluir_ajax", {{
        method: "POST",
        headers: {{ "Content-Type": "application/json" }},
        body: JSON.stringify({{ id: id }})
    }}).then(() => location.reload());
}}

function editar(id, botao) {{
    let novo = prompt("Novo texto:");
    if (!novo) return;

    fetch("/editar_ajax", {{
        method: "POST",
        headers: {{ "Content-Type": "application/json" }},
        body: JSON.stringify({{ id: id, texto: novo }})
    }}).then(() => location.reload());
}}

function gerarPrompt() {{
    let texto = document.getElementById("busca").value;

    fetch("/gerar_ajax", {{
        method: "POST",
        headers: {{
            "Content-Type": "application/x-www-form-urlencoded"
        }},
        body: "busca=" + encodeURIComponent(texto)
    }})
    .then(() => location.reload());
}}

</script>

</body>
</html>
"""
   


# =========================
# GERAR
# =========================


@app.route("/gerar", methods=["POST"])
def gerar():
    if "usuario" not in session:
        return redirect(url_for("login"))

    texto = request.form.get("busca", "").lower().strip()

    if not texto:
        prompt = random.choice([
            "Explique inteligência artificial",
            "Crie um roteiro",
            "Crie uma imagem estilo Pixar"
        ])
    else:
        prompt = f"Crie algo sobre: {texto}"

    salvar_prompt(prompt, session["usuario"])
    return redirect(url_for("home"))
    

@app.route("/gerar_ajax", methods=["POST"])
def gerar_ajax():

    if "usuario" not in session:
        return "erro"

    texto = request.form.get("busca", "").strip().lower()

    if not texto:
        prompt = random.choice([
            "Explique inteligência artificial",
            "Crie um roteiro",
            "Crie uma imagem estilo Pixar"
        ])
    else:
        prompt = f"Crie algo sobre: {texto}"

        salvar_prompt(prompt, session["usuario"])

    return prompt


# =========================
# AÇÕES
# =========================

@app.route("/limpar")
def limpar():
    limpar_prompts()
    limpar_favoritos()
    return redirect(url_for("home"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = request.form.get("username")
        senha = request.form.get("senha")

        conn = conectar()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM usuarios WHERE username = ? AND senha = ?",
            (user, senha)
        )

        usuario = cursor.fetchone()
        conn.close()

        if usuario:
            session["usuario"] = user
            return redirect(url_for("home"))
        else:
            return "Login inválido!"

    return """
    <h2>Login</h2>
    <form method="POST">
        <input name="username" placeholder="Usuário"><br>
        <input name="senha" type="password" placeholder="Senha"><br>
        <button>Entrar</button>
    </form>
    """


@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    if request.method == "POST":
        user = request.form.get("username")
        senha = request.form.get("senha")

        conn = conectar()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "INSERT INTO usuarios (username, senha) VALUES (?, ?)",
                (user, senha)
            )
            conn.commit()
        except:
            return "Usuário já existe!"

        conn.close()
        return redirect(url_for("login"))

    return """
    <h2>Cadastro</h2>
    <form method="POST">
        <input name="username" placeholder="Usuário"><br>
        <input name="senha" type="password" placeholder="Senha"><br>
        <button>Cadastrar</button>
    </form>
    """



@app.route("/favoritar_ajax/<int:id>")
def favoritar_ajax(id):
    prompts = carregar_prompts()

    for p in prompts:
        if p[0] == id:
            salvar_favorito(p[1])
            return p[1]

    return "erro"


@app.route("/excluir_ajax", methods=["POST"])
def excluir_ajax():

    if "usuario" not in session:
        return "erro"
    dados = request.get_json()
    id = dados.get("id")

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM prompts WHERE id = ?", (id,))
    cursor.execute("DELETE FROM favoritos WHERE rowid = ?", (id,))

    conn.commit()
    conn.close()

    return "ok"


@app.route("/editar_ajax", methods=["POST"])
def editar_ajax():

    if "usuario" not in session:
        return "erro"

    dados = request.get_json()
    id = dados.get("id")
    texto = dados.get("texto")

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("UPDATE prompts SET texto = ? WHERE id = ?", (texto, id))

    conn.commit()
    conn.close()

    return "ok"


@app.route("/logout")
def logout():
    session.pop("usuario", None)
    return redirect(url_for("login"))


# =========================
# START
# =========================


criar_tabelas()


if __name__ == "__main__": 
    app.run()