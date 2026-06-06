from flask import Flask, jsonify, request, render_template, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
import os
import random
import time
import math
from threading import RLock

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-fence-guard-troque-em-producao")
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
)

# Conta teste funcional
USUARIOS = {
    "operador": {
        "nome": "Operador Teste",
        "perfil": "operador",
        "senha_hash": generate_password_hash("fence123"),
    }
}

# ─── Estado global do sistema ───────────────────────────────────────────────
SETORES_BASE = {"setor_1", "setor_2", "setor_3", "setor_4"}
TENSAO_MIN = 3000   # V — abaixo disso → falha
TENSAO_MAX = 8000   # V — máximo simulado
TENSAO_CRITICA = 4000  # V — zona de alerta
FALHA_INTERVALO = 180    # segundos — no máximo 1 falha permanente a cada 3 minutos
ULTIMA_FALHA_TS = time.time()

setores = {
    "setor_1": {"nome": "Setor 1", "ligado": True,  "defeito": False, "tensao": 6500.0, "tensao_alvo": 6500.0, "ts": time.time()},
    "setor_2": {"nome": "Setor 2", "ligado": True,  "defeito": False, "tensao": 7200.0, "tensao_alvo": 7200.0, "ts": time.time()},
    "setor_3": {"nome": "Setor 3", "ligado": True,  "defeito": False, "tensao": 5900.0, "tensao_alvo": 5900.0, "ts": time.time()},
    "setor_4": {"nome": "Setor 4", "ligado": False, "defeito": False, "tensao": 0.0,    "tensao_alvo": 0.0,    "ts": time.time()},
}

_proximo_id = 5   # contador para IDs extras
SENSOR_MODE = "simulado"  # pronto para evoluir para sensores físicos reais
historico_tensao = {sid: [] for sid in setores}
eventos = []
state_lock = RLock()


def json_body() -> dict:
    """Lê JSON de forma segura sem estourar erro 500 em payload inválido."""
    body = request.get_json(silent=True)
    return body if isinstance(body, dict) else {}


def usuario_logado() -> bool:
    return bool(session.get("logado") and session.get("usuario") in USUARIOS)


@app.before_request
def proteger_rotas_api():
    """Bloqueia uso direto da API sem login ativo."""
    if request.path.startswith("/api/") and not usuario_logado():
        return jsonify({"ok": False, "msg": "Sessão expirada ou não autorizada"}), 401


def registrar_evento(tipo: str, mensagem: str, setor_id: str | None = None):
    evento = {
        "tipo": tipo,
        "mensagem": mensagem,
        "setor_id": setor_id,
        "ts": time.time(),
    }
    eventos.append(evento)
    del eventos[:-80]
    return evento


def registrar_historico(sid: str, tensao: float):
    historico_tensao.setdefault(sid, []).append({"ts": time.time(), "tensao": round(float(tensao), 1)})
    del historico_tensao[sid][:-120]



def simular_tensao(setor: dict) -> float:
    """Simula pequena oscilação mantendo a tensão definida pelo usuário.

    Antes o simulador forçava qualquer valor baixo para perto de 3,7 kV,
    então o controle de tensão parecia não obedecer ao slider. Agora ele
    respeita o setpoint salvo em `tensao_alvo` e apenas oscila suavemente
    em volta dele.
    """
    alvo = float(setor.get("tensao_alvo", setor.get("tensao", 0.0)))
    if alvo <= 0:
        return 0.0

    delta = random.uniform(-80, 80)
    base = alvo + delta
    return round(max(0.0, min(base, TENSAO_MAX)), 1)


def gerar_falha_programada():
    """Gera no máximo 1 falha permanente a cada 3 minutos."""
    global ULTIMA_FALHA_TS
    agora = time.time()
    if agora - ULTIMA_FALHA_TS < FALHA_INTERVALO:
        return

    candidatos = [
        s for s in setores.values()
        if s["ligado"] and not s["defeito"]
    ]
    if not candidatos:
        ULTIMA_FALHA_TS = agora
        return

    alvo = random.choice(candidatos)
    alvo["defeito"] = True
    alvo["tensao"] = 0.0
    alvo["tensao_alvo"] = 0.0
    alvo["ts"] = agora
    ULTIMA_FALHA_TS = agora
    registrar_evento("falha", f"Falha permanente gerada em {alvo['nome']}")


def atualizar_tensoes():
    """Atualiza tensões; falhas permanentes só entram pelo intervalo programado."""
    for s in setores.values():
        if not s["ligado"] or s["defeito"]:
            s["tensao"] = 0.0
            continue
        s["tensao"] = simular_tensao(s)
        s["ts"] = time.time()
        for sid2, setor2 in setores.items():
            if setor2 is s:
                registrar_historico(sid2, s["tensao"])
                break

    gerar_falha_programada()


def serializar_setor(sid: str, s: dict) -> dict:
    base = sid in SETORES_BASE
    tensao = s["tensao"]

    if s["defeito"]:
        status = "falha"
    elif not s["ligado"]:
        status = "desligado"
    elif tensao < TENSAO_CRITICA:
        status = "critico"
    else:
        status = "normal"

    return {
        "id": sid,
        "nome": s["nome"],
        "ligado": s["ligado"],
        "defeito": s["defeito"],
        "tensao": tensao,
        "tensao_alvo": s.get("tensao_alvo", tensao),
        "status": status,
        "base": base,
        "ts": s["ts"],
    }


# ─── Rotas ──────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    if not usuario_logado():
        return redirect(url_for("login"))
    return render_template("index.html", usuario=session.get("usuario"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        if usuario_logado():
            return redirect(url_for("index"))
        return render_template("login.html")

    body = json_body()
    usuario = str(body.get("usuario", "")).strip()
    senha = str(body.get("senha", ""))
    conta = USUARIOS.get(usuario)

    if conta and check_password_hash(conta["senha_hash"], senha):
        session.clear()
        session["logado"] = True
        session["usuario"] = usuario
        session["nome"] = conta["nome"]
        session["perfil"] = conta["perfil"]
        return jsonify({"ok": True, "usuario": usuario, "nome": conta["nome"], "perfil": conta["perfil"]})

    return jsonify({"ok": False, "msg": "Usuário ou senha inválidos"}), 401


@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"ok": True})


@app.route("/api/sensores")
def api_sensores():
    atualizar_tensoes()
    data = [serializar_setor(sid, s) for sid, s in setores.items()]
    alertas = [d for d in data if d["status"] in ("falha", "critico")]
    return jsonify({"setores": data, "alertas": alertas, "ts": time.time()})


@app.route("/api/controle", methods=["POST"])
def api_controle():
    body = json_body()
    sid = body.get("id")
    acao = body.get("acao")  # ligar | desligar | reiniciar | manutencao

    if sid not in setores:
        return jsonify({"ok": False, "msg": "Setor não encontrado"}), 404

    s = setores[sid]

    if acao == "ligar":
        s["ligado"] = True
        # NÃO remove defeito
        if not s["defeito"]:
            s["tensao_alvo"] = random.uniform(5500, TENSAO_MAX)
            s["tensao"] = s["tensao_alvo"]

    elif acao == "desligar":
        s["ligado"] = False
        s["tensao"] = 0.0
        s["tensao_alvo"] = 0.0

    elif acao == "reiniciar":
        s["ligado"] = True
        # NÃO remove defeito; se tiver defeito tensão permanece 0
        if not s["defeito"]:
            s["tensao_alvo"] = random.uniform(5500, TENSAO_MAX)
            s["tensao"] = s["tensao_alvo"]

    elif acao == "manutencao":
        # Única ação que remove falha permanente
        s["defeito"] = False
        s["ligado"] = True
        s["tensao_alvo"] = random.uniform(6000, TENSAO_MAX)
        s["tensao"] = s["tensao_alvo"]

    else:
        return jsonify({"ok": False, "msg": "Ação inválida"}), 400

    s["ts"] = time.time()
    registrar_historico(sid, s["tensao"])
    registrar_evento("controle", f"Ação {acao} executada em {s['nome']}", sid)
    return jsonify({"ok": True, "setor": serializar_setor(sid, s)})


@app.route("/api/adicionar", methods=["POST"])
def api_adicionar():
    global _proximo_id
    body = json_body()
    nome = body.get("nome", "").strip()[:60]
    if not nome:
        return jsonify({"ok": False, "msg": "Nome obrigatório"}), 400

    sid = f"setor_{_proximo_id}"
    _proximo_id += 1
    setores[sid] = {
        "nome": nome,
        "ligado": False,
        "defeito": False,
        "tensao": 0.0,
        "tensao_alvo": 0.0,
        "ts": time.time(),
    }
    historico_tensao[sid] = []
    registrar_evento("layout", f"Novo setor criado: {nome}", sid)
    return jsonify({"ok": True, "setor": serializar_setor(sid, setores[sid])})


@app.route("/api/remover", methods=["POST"])
def api_remover():
    body = json_body()
    sid = body.get("id")
    if sid in SETORES_BASE:
        return jsonify({"ok": False, "msg": "Setores base não podem ser removidos"}), 403
    if sid not in setores:
        return jsonify({"ok": False, "msg": "Setor não encontrado"}), 404
    nome = setores[sid]["nome"]
    del setores[sid]
    historico_tensao.pop(sid, None)
    registrar_evento("layout", f"Setor removido: {nome}", sid)
    return jsonify({"ok": True})


@app.route("/api/editar", methods=["POST"])
def api_editar():
    body = json_body()
    sid = body.get("id")
    novo_nome = body.get("nome", "").strip()[:60]
    if sid not in setores:
        return jsonify({"ok": False, "msg": "Setor não encontrado"}), 404
    if not novo_nome:
        return jsonify({"ok": False, "msg": "Nome obrigatório"}), 400
    antigo = setores[sid]["nome"]
    setores[sid]["nome"] = novo_nome
    registrar_evento("layout", f"Setor renomeado: {antigo} → {novo_nome}", sid)
    return jsonify({"ok": True, "setor": serializar_setor(sid, setores[sid])})


@app.route("/api/tensao", methods=["POST"])
def api_tensao():
    body = json_body()
    sid = body.get("id")
    try:
        tensao = float(body.get("tensao", 0))
    except (TypeError, ValueError):
        return jsonify({"ok": False, "msg": "Tensão inválida"}), 400

    if sid not in setores:
        return jsonify({"ok": False, "msg": "Setor não encontrado"}), 404

    s = setores[sid]

    # Aumentar potência NÃO corrige fios/trechos com defeito.
    if s["defeito"]:
        s["tensao"] = 0.0
        s["ts"] = time.time()
        return jsonify({"ok": True, "msg": "Setor em falha: use manutenção", "setor": serializar_setor(sid, s)})

    if not math.isfinite(tensao):
        return jsonify({"ok": False, "msg": "Tensão inválida"}), 400

    tensao = max(0.0, min(tensao, TENSAO_MAX))
    s["tensao_alvo"] = tensao
    s["ligado"] = tensao > 0
    s["tensao"] = tensao if s["ligado"] else 0.0
    s["ts"] = time.time()
    registrar_historico(sid, s["tensao"])
    registrar_evento("tensao", f"Tensão ajustada para {s['tensao'] / 1000:.1f} kV em {s['nome']}", sid)
    return jsonify({"ok": True, "setor": serializar_setor(sid, s)})


@app.route("/api/manutencao_todos", methods=["POST"])
def api_manutencao_todos():
    for s in setores.values():
        s["defeito"] = False
        s["ligado"] = True
        s["tensao_alvo"] = random.uniform(6000, TENSAO_MAX)
        s["tensao"] = s["tensao_alvo"]
        s["ts"] = time.time()
    for sid, s in setores.items():
        registrar_historico(sid, s["tensao"])
    registrar_evento("manutencao", "Manutenção geral executada em todos os setores")
    data = [serializar_setor(sid, s) for sid, s in setores.items()]
    return jsonify({"ok": True, "setores": data})


@app.route("/api/alerta")
def api_alerta():
    atualizar_tensoes()
    alertas = [
        serializar_setor(sid, s)
        for sid, s in setores.items()
        if s["defeito"] or (s["ligado"] and not s["defeito"] and s["tensao"] < TENSAO_CRITICA)
    ]
    return jsonify({"alertas": alertas, "total": len(alertas)})


@app.route("/api/estatisticas")
def api_estatisticas():
    atualizar_tensoes()
    data = [serializar_setor(sid, s) for sid, s in setores.items()]
    ativos = [d for d in data if d["ligado"] and not d["defeito"]]
    tensao_media = sum(d["tensao"] for d in ativos) / len(ativos) if ativos else 0.0
    return jsonify({
        "ok": True,
        "nome": "Fence Guard SCADA v8",
        "sensor_mode": SENSOR_MODE,
        "total_setores": len(data),
        "setores_ativos": len(ativos),
        "setores_desligados": len([d for d in data if not d["ligado"]]),
        "setores_falha": len([d for d in data if d["status"] == "falha"]),
        "setores_criticos": len([d for d in data if d["status"] == "critico"]),
        "tensao_media": round(tensao_media, 1),
        "eventos_recentes": eventos[-10:],
        "ts": time.time(),
    })


@app.route("/api/diagnostico")
def api_diagnostico():
    atualizar_tensoes()
    data = [serializar_setor(sid, s) for sid, s in setores.items()]
    itens = []
    for d in data:
        if d["defeito"]:
            itens.append({"nivel": "falha", "setor_id": d["id"], "msg": f"{d['nome']} está em falha permanente. Use manutenção."})
        elif not d["ligado"]:
            itens.append({"nivel": "info", "setor_id": d["id"], "msg": f"{d['nome']} está desligado."})
        elif d["tensao"] < TENSAO_CRITICA:
            itens.append({"nivel": "critico", "setor_id": d["id"], "msg": f"{d['nome']} está com tensão baixa ({d['tensao']/1000:.1f} kV)."})
    return jsonify({"ok": True, "diagnostico": itens, "total": len(itens), "ts": time.time()})


@app.route("/api/arquitetura")
def api_arquitetura():
    return jsonify({
        "ok": True,
        "nome": "Fence Guard SCADA v8",
        "descricao": "Sistema web para monitoramento, controle de tensão e diagnóstico de cerca elétrica rural.",
        "camadas": [
            {"nome": "Operador", "itens": ["Dashboard", "Mapa SVG", "Controles de tensão", "Manutenção"]},
            {"nome": "Frontend", "itens": ["HTML", "CSS", "JavaScript", "Fetch API"]},
            {"nome": "Backend Flask", "itens": ["/api/sensores", "/api/controle", "/api/tensao", "/api/diagnostico"]},
            {"nome": "Núcleo SCADA", "itens": ["Regras de falha", "Tensão alvo", "Histórico", "Eventos"]},
            {"nome": "Cerca elétrica", "itens": ["Setores", "Fios", "Energizador", "Sensores simulados"]},
        ],
        "modulos_ativos": ["controle_tensao", "fios_por_tensao", "falha_permanente", "manutencao", "diagnostico", "historico"],
        "sensor_mode": SENSOR_MODE,
    })


if __name__ == "__main__":
    app.run(debug=True, port=5000)
