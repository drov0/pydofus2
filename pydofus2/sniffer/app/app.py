import asyncio
import datetime
from threading import Thread

from flask import Flask, jsonify, render_template
from flask_socketio import SocketIO, emit

from pydofus2.com.ankamagames.jerakine.network.NetworkMessage import NetworkMessage
from pydofus2.sniffer.network.DofusSniffer import DofusSniffer


class DofusSnifferApp:
    def __init__(self):
        self.app = Flask(__name__)
        self.socketio = SocketIO(self.app)
        self.sniffer: DofusSniffer = None
        self.setup_routes()

    def handle_new_message(self, conn_id: str, msg: NetworkMessage, from_client: bool):
        msg_json = self.sniffer.messagesRecord[conn_id][-1]
        client, server = conn_id.split(" <-> ")
        self.socketio.emit("new_message", {"conn_id": server, "message": msg_json, "from_client": from_client})

    def handle_sniffer_crash(self, error_trace):
        print(f"Sniffer crashed with error: {error_trace}")
        self.socketio.emit("sniffer_crash", {"error": error_trace})

    def setup_routes(self):

        @self.app.route("/")
        def index():
            return render_template("index.html")

        @self.app.route("/start_sniffer", methods=["POST"])
        def start_sniffer():
            if self.sniffer and self.sniffer.running.is_set():
                return jsonify({"status": "error", "message": "Sniffer already running"})
            self.sniffer = DofusSniffer(
                "DofusSnifferApp", on_message=self.handle_new_message, on_crash=self.handle_sniffer_crash
            )
            self.sniffer.start()
            return jsonify({"status": "success", "message": "Sniffer started"})

        @self.app.route("/stop_sniffer", methods=["POST"])
        def stop_sniffer():
            if self.sniffer and self.sniffer.running.is_set():
                self.sniffer.stop()
                self.sniffer = None
                return jsonify({"status": "success", "message": "Sniffer stopped"})
            return jsonify({"status": "error", "message": "Sniffer not running"})

    def run(self, debug=True):
        self.socketio.run(self.app, debug=debug)


if __name__ == "__main__":
    app = DofusSnifferApp()
    app.run(debug=True)
