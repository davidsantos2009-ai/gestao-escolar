
from flask import Flask, request, redirect, render_template_string
import sqlite3

app = Flask(__name__)
BANCO = "gestao_escolar.db"


# CONEXÃO COM O BANCO
def conectar():
    return sqlite3.connect(BANCO)


# CRIAR TABELA
with conectar() as db:
    db.execute("""
        CREATE TABLE IF NOT EXISTS reunioes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT,
            data TEXT,
            horario TEXT,
            responsavel TEXT,
            participantes TEXT,
            pauta TEXT,
            presenca TEXT,
            ata TEXT,
            decisoes TEXT,
            tarefas TEXT,
            prazo TEXT,
            status TEXT
        )
    """)


# CAMPOS DO FORMULÁRIO
campos = [
    ("titulo", "Título da reunião", 1, "text"),
    ("data", "Data", 2, "date"),
    ("horario", "Horário", 3, "time"),
    ("responsavel", "Responsável", 4, "text"),
    ("participantes", "Participantes", 5, "textarea"),
    ("pauta", "Pauta da reunião", 6, "textarea"),
    ("presenca", "Presenças", 7, "textarea"),
    ("ata", "Ata da reunião", 8, "textarea"),
    ("decisoes", "Decisões", 9, "textarea"),
    ("tarefas", "Tarefas posteriores", 10, "textarea"),
    ("prazo", "Prazo das tarefas", 11, "date"),
    ("status", "Status das tarefas", 12, "select")
]


# PÁGINA HTML
HTML = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">

<title>Gestão Escolar Pro</title>

<style>
* {
    box-sizing: border-box;
}

body {
    font-family: Arial, sans-serif;
    background: #f3f0f7;
    padding: 20px;
    margin: 0;
}

main {
    max-width: 850px;
    margin: auto;
}

h1, h2, h3 {
    color: #704080;
}

header {
    text-align: center;
    padding: 20px;
}

section {
    background: white;
    padding: 22px;
    border-radius: 12px;
    margin-bottom: 18px;
    box-shadow: 0 3px 10px #00000012;
}

label {
    display: block;
    margin-top: 12px;
    font-weight: bold;
    color: #493050;
}

input, textarea, select {
    width: 100%;
    padding: 12px;
    margin-top: 6px;
    border: 1px solid #ccc;
    border-radius: 7px;
    font-size: 14px;
}

textarea {
    min-height: 85px;
    resize: vertical;
}

button {
    background: #704080;
    color: white;
    padding: 12px 18px;
    border: none;
    border-radius: 7px;
    cursor: pointer;
    margin-top: 15px;
}

button:hover {
    background: #542e64;
}

.excluir {
    background: #c0392b;
}

.editar {
    color: #704080;
    font-weight: bold;
}

.status {
    background: #eee5f5;
    padding: 8px;
    border-radius: 6px;
    display: inline-block;
}

.acoes {
    display: flex;
    gap: 12px;
    align-items: center;
}

@media(max-width: 600px) {
    body {
        padding: 10px;
    }

    section {
        padding: 15px;
    }
}
</style>
</head>

<body>
<main>

<header>
    <h1>Gestão Escolar Pro</h1>
    <p>Sistema de gerenciamento de reuniões escolares</p>
</header>

<section>
<h2>{{ "Editar reunião" if item else "Cadastrar nova reunião" }}</h2>

<form method="POST">

{% for campo in campos %}

<label>{{ campo[1] }}</label>

{% if campo[3] == "textarea" %}

<textarea name="{{ campo[0] }}">{{ item[campo[2]] if item else '' }}</textarea>

{% elif campo[3] == "select" %}

<select name="{{ campo[0] }}">
{% for s in ["Pendente", "Em andamento", "Concluída"] %}
<option value="{{ s }}"
{% if item and item[campo[2]] == s %}selected{% endif %}>
{{ s }}
</option>
{% endfor %}
</select>

{% else %}

<input
    type="{{ campo[3] }}"
    name="{{ campo[0] }}"
    value="{{ item[campo[2]] if item else '' }}"
>

{% endif %}

{% endfor %}

<button type="submit">Salvar informações</button>

{% if item %}
<a href="/" class="editar">Cancelar edição</a>
{% endif %}

</form>
</section>


<h2>Reuniões cadastradas</h2>

{% for r in registros %}

<section>

<h3>{{ r[1] }}</h3>

<p><b>Data:</b> {{ r[2] }} | {{ r[3] }}</p>
<p><b>Responsável:</b> {{ r[4] }}</p>
<p><b>Participantes:</b> {{ r[5] }}</p>
<p><b>Pauta:</b> {{ r[6] }}</p>
<p><b>Presenças:</b> {{ r[7] }}</p>
<p><b>Ata:</b> {{ r[8] }}</p>
<p><b>Decisões:</b> {{ r[9] }}</p>
<p><b>Tarefas:</b> {{ r[10] }}</p>
<p><b>Prazo:</b> {{ r[11] }}</p>

<p>
<b>Status:</b>
<span class="status">{{ r[12] }}</span>
</p>

<div class="acoes">

<a class="editar" href="/editar/{{ r[0] }}">
Editar reunião
</a>

<form
    method="POST"
    action="/excluir/{{ r[0] }}"
    onsubmit="return confirm('Deseja realmente excluir esta reunião?')"
>
<button class="excluir" type="submit">
Excluir reunião
</button>
</form>

</div>

</section>

{% else %}

<p>Nenhuma reunião cadastrada.</p>

{% endfor %}

</main>
</body>
</html>
"""


# PÁGINA INICIAL E CADASTRO
@app.route("/", methods=["GET", "POST"])
def inicio():

    if request.method == "POST":

        valores = [
            request.form.get(campo[0], "")
            for campo in campos
        ]

        with conectar() as db:
            db.execute("""
                INSERT INTO reunioes (
                    titulo, data, horario, responsavel,
                    participantes, pauta, presenca, ata,
                    decisoes, tarefas, prazo, status
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, valores)

        return redirect("/")

    with conectar() as db:
        registros = db.execute("""
            SELECT * FROM reunioes
            ORDER BY id DESC
        """).fetchall()

    return render_template_string(
        HTML,
        registros=registros,
        campos=campos,
        item=None
    )


# EDITAR REUNIÃO
@app.route("/editar/<int:id>", methods=["GET", "POST"])
def editar(id):

    with conectar() as db:

        if request.method == "POST":

            valores = [
                request.form.get(campo[0], "")
                for campo in campos
            ]

            db.execute("""
                UPDATE reunioes SET
                    titulo=?,
                    data=?,
                    horario=?,
                    responsavel=?,
                    participantes=?,
                    pauta=?,
                    presenca=?,
                    ata=?,
                    decisoes=?,
                    tarefas=?,
                    prazo=?,
                    status=?
                WHERE id=?
            """, valores + [id])

            return redirect("/")

        item = db.execute(
            "SELECT * FROM reunioes WHERE id=?",
            (id,)
        ).fetchone()

        registros = db.execute("""
            SELECT * FROM reunioes
            ORDER BY id DESC
        """).fetchall()

    if not item:
        return redirect("/")

    return render_template_string(
        HTML,
        registros=registros,
        campos=campos,
        item=item
    )


# EXCLUIR REUNIÃO
@app.route("/excluir/<int:id>", methods=["POST"])
def excluir(id):

    with conectar() as db:
        db.execute(
            "DELETE FROM reunioes WHERE id=?",
            (id,)
        )

    return redirect("/")


# EXECUTAR SISTEMA
if __name__ == "__main__":
    app.run(debug=False)
