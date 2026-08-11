"""Entry point used by the Windows launcher (and by you, if you ever
want to run the app from a terminal instead of double-clicking).

Starts the local dashboard at http://127.0.0.1:5055 — reachable only
from this computer.
"""

from app.dashboard.server import create_app

if __name__ == "__main__":
    app = create_app()
    app.run(host="127.0.0.1", port=5055, debug=False)
