#!/usr/bin/python
import datetime
import json
import os
import threading

import pyshark
from .DofusConnection import LOCAL_IP, ConnEvent, DofusConnection
from .Packet import TCPPacket

from pydofus2.com.ankamagames.jerakine.logger.Logger import Logger
from pydofus2.com.ankamagames.jerakine.network.NetworkMessage import \
    NetworkMessage
    
# Global variables for message storage and sniffer control
messages_lock = threading.Lock()
LOW_LEVEL_DEBUG = bool(os.environ.get("LOW_LEVEL_DEBUG", False))

class DofusSniffer(threading.Thread):
    
    def __init__(self, callback=None, recordMessages=True):
        super().__init__()
        self.capture = pyshark.LiveCapture(bpf_filter="tcp port 5555")
        self.connections = dict[int, DofusConnection]()
        self.callback = callback
        self.running = False
        self.recordMessages = recordMessages
        self.messagesRecord = {}

    def run(self):
        Logger().debug("Started sniffer")
        self.running = True
        self.capture.set_debug()
        for p in self.capture.sniff_continuously():
            try:
                p = TCPPacket(p)
                if LOW_LEVEL_DEBUG:
                    Logger().debug(f"Received packet: {p}")
                local_port = p.srcport if p.src == LOCAL_IP else p.dstport
                conn = self.connections.get(local_port)
                if not conn:
                    conn = DofusConnection.initFromPacket(p)
                    if not conn: continue
                    self.messagesRecord[conn.id] = []
                    conn.handle = self.handle
                    self.connections[local_port] = conn
                    conn.on(ConnEvent.CLOSE, lambda _, conn_id: self.connections.pop(conn_id))
                conn.low_receive(p)
            except Exception as e:
                Logger().error(f"Error while handling {p.all_fields()}: {e}", exc_info=True)
                self.stop()
        Logger().debug("Stopped sniffer")
        
    def handle(self, conn: DofusConnection, msg: NetworkMessage, from_client: bool):
        if msg.unpacked:
            if self.recordMessages:
                msgjson = msg.to_json()
                msg.receptionTime = datetime.datetime.now().strftime('%H:%M:%S:%f')
                msgjson["__receptionTime__"] = msg.receptionTime
                msgjson["__direction__"] = 'snd' if from_client else 'rcv'
                if 'hash_function' in msgjson:
                    del msgjson['hash_function']
                with messages_lock:
                    self.messagesRecord[conn.id].append(msgjson)
                    with open(conn.messagesRecordFile, "w") as fp:
                        json.dump(self.messagesRecord[conn.id], fp, indent=2)
            if self.callback:
                self.callback(conn.id, msg, from_client)
                
    def stop(self):
        self.capture.close()
        self.running = False

if __name__ == "__main__":

    mySniffer = DofusSniffer()
    mySniffer.start()
    try:
        mySniffer.join()
    except KeyboardInterrupt:
        mySniffer.stop()
