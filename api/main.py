"""Cloud Run service — POST /create-checkout"""
from __future__ import annotations

import os

import mercadopago
from flask import Flask, jsonify, request

app = Flask(__name__)
PRODUCT_PRICES: dict[str, float] = {
    "caja_diaria": 4900,
    "precio_margen": 3900,
    "stock_control": 4500,
    "costos_por_producto": 4200,
    "flujo_de_fondos": 5200,
    "rentabilidad_por_producto": 5500,
    "simulador_inflacion": 5800,
    "proyeccion_ventas": 5300,
    "control_de_gastos": 4800,
    "compras_y_proveedores": 4900,
    "cuentas_corrientes_clientes": 5100,
    "conciliador_bancario_macro": 3000,
}

BASE_URL = os.environ.get("BASE_URL", "https://exceland.vercel.app")


@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    return response


@app.route("/create-checkout", methods=["OPTIONS"])
def create_checkout_options():
    return ("", 204)


@app.post("/create-checkout")
def create_checkout():
    body = request.get_json(silent=True) or {}
    skill_id = body.get("skill_id")

    if not skill_id or skill_id not in PRODUCT_PRICES:
        return jsonify({"error": "skill_id inválido"}), 400

    token = os.environ.get("MP_ACCESS_TOKEN")
    if not token:
        return jsonify({"error": "MP_ACCESS_TOKEN no configurado"}), 500

    try:
        sdk = mercadopago.SDK(token)

        preference_data = {
            "items": [
                {
                    "title": skill_id.replace("_", " ").title(),
                    "quantity": 1,
                    "currency_id": "ARS",
                    "unit_price": PRODUCT_PRICES[skill_id],
                }
            ],
            "back_urls": {
                "success": f"{BASE_URL}/success.html",
                "failure": f"{BASE_URL}/error.html",
            },
        }


        result = sdk.preference().create(preference_data)
        init_point = result.get("response", {}).get("init_point")

        if not init_point:
            return jsonify({"error": "error creando preferencia"}), 500

        return jsonify({"init_point": init_point})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)