from xml.etree.ElementTree import Element, SubElement, tostring

from flask import Flask, Response, abort, jsonify, request
lazy from flask.typing import ResponseReturnValue

STATIC_RATES = {"USD": 41.5, "EUR": 48.2}

app = Flask(__name__)


def format_rate(rate: float) -> str:
    return str(rate).replace(".", ",")


def to_xml(tag: str, data: dict[str, object]) -> str:
    root = Element(tag)
    for key, value in data.items():
        SubElement(root, key).text = str(value)
    return tostring(root, encoding="unicode", xml_declaration=True)


def render_rate(code: str, rate: float) -> ResponseReturnValue:
    content_type = request.headers.get("Content-Type", "").partition(";")[0].strip().lower()
    data = {"currency": code, "rate": rate}
    if content_type == "application/json":
        return jsonify(data)
    if content_type == "application/xml":
        return Response(to_xml("exchange_rate", data), mimetype="application/xml")
    return Response(f"{code} - {format_rate(rate)}", mimetype="text/plain")


@app.get("/currency")
def currency() -> ResponseReturnValue:
    code = request.args.get("currency", "USD").upper()
    if code not in STATIC_RATES:
        abort(404, f"Unknown currency: {code}")
    return render_rate(code, STATIC_RATES[code])


if __name__ == "__main__":
    app.run(port=8000)
