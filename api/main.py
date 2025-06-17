import json
import logging
import os
import sys

from flask import Flask
from mcstatus import JavaServer

server_port = os.getenv("SERVER_PORT", 25565)

app = Flask(__name__)

app.logger.disabled = True
log = logging.getLogger('werkzeug')
log.disabled = True

@app.route("/api/status")
def get_status():
	try:
		server = JavaServer.lookup(f"localhost:{server_port}", timeout=1)
		status = server.status()
	except Exception:
		return json.dumps({
			'version': "unknown",
			'online': 0,
		})
	else:

		data: dict[str, str | int] = {
			'version': status.version.name,
			'online': status.players.online,
		}

		return json.dumps(data)

if __name__ == '__main__':
	if os.getenv("ENABLE_API") != "true":
		sys.exit(-1)

	app.run(host="0.0.0.0", port=5050)
