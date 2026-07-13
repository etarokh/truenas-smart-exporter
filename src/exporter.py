from flask import Flask, Response
from prometheus_client import Gauge, generate_latest, CONTENT_TYPE_LATEST

app = Flask(__name__)

exporter_up = Gauge(
    "exporter_up",
    "Exporter status",
)

exporter_up.set(1)


@app.get("/metrics")
def metrics() -> Response:
    return Response(
        generate_latest(),
        mimetype=CONTENT_TYPE_LATEST,
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9111)
