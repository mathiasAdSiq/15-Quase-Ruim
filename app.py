from flask import Flask, render_template, jsonify
import random

app = Flask(__name__)

# 🔌 simulação de sensores reais (ESP32 depois)
setores = {
    "Setor 1": {"tensao": 7200, "lat": -29.7, "lon": -53.8},
    "Setor 2": {"tensao": 6800, "lat": -29.71, "lon": -53.81},
    "Setor 3": {"tensao": 1200, "lat": -29.72, "lon": -53.82},
    "Setor 4": {"tensao": 7100, "lat": -29.73, "lon": -53.83}
}

limite = 3000


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/sensores")
def sensores():

    dados = {}

    for setor, info in setores.items():

        # simula variação de sensor
        tensao = info["tensao"] + random.randint(-200, 200)

        dados[setor] = {
            "tensao": tensao,
            "lat": info["lat"],
            "lon": info["lon"],
            "status": "FALHA" if tensao < limite else "OK"
        }

    return jsonify(dados)


@app.route("/api/alerta")
def alerta():

    for setor, info in setores.items():
        if info["tensao"] < limite:
            return jsonify({
                "alerta": True,
                "mensagem": f"Falha detectada em {setor} ⚠️"
            })

    return jsonify({"alerta": False})


if __name__ == "__main__":
    app.run(debug=True)