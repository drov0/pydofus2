const path = require('path');
const child_process = require('child_process');
const process = require('process');
const thrift = require('thrift');
const Pyd2botService = require('../pyd2botService/Pyd2botService.js');
const ejse = require('ejs-electron');
const { emit } = require('process');

class InstancesManager {

    // this class manages the running instances of pyd2bot
    static get instance() {
        return InstancesManager._instance || (InstancesManager._instance = new InstancesManager()), InstancesManager._instance
    }

    constructor() {
        this.pyd2botExePath = path.join(process.env.AppData, 'pyd2bot', 'pyd2bot.exe');
        this.pyd2botDevPath = path.join(ejse.data("appDir"), '..', '..', 'pyd2bot','pyd2bot.py');
        this.pyd2botDevEnvPath = path.join(ejse.data("appDir"), '..', '..', '.venv', 'Scripts', 'activate');
        this.runningInstances = {};
        this.freePorts = Array(100).fill().map((element, index) => index + 9999);
        this.wantsToKillServer = {};
        this.wantsToKillClient = {};
        ejse.data('runningInstances', this.runningInstances);
    }

    async spawnClient(instanceId) {
        const max_attempts = 3;
        var attempt = 0;
        var connect_timeout = 1000;
        var execFunc = (resolve, reject) => {
            var inst = this.runningInstances[instanceId];
            if (!inst) {
                console.log("Instance " + instanceId + " not found");
                return
            }
            var transport = thrift.TBufferedTransport;
            var protocol = thrift.TBinaryProtocol;
            var connection = thrift.createConnection("127.0.0.1", inst.port, {
                transport : transport,
                protocol : protocol
            });
            connection.on('error', (err) => {
                if (InstancesManager.instance.wantsToKillClient[instanceId]) {
                    InstancesManager.instance.wantsToKillClient[instanceId] = false;
                }
                else {
                    reject("Could not connect client to instance " + instanceId);
                }
            });
            connection.on('connect', () => {
                console.log("Connected the client to instance " + instanceId  + " server" + "on port " + inst.port);
                var client = thrift.createClient(Pyd2botService, connection);
                if (inst.connection) {
                    this.wantsToKillClient[instanceId] = true;
                    inst.connection.end();
                }
                inst.connection = connection;
                inst.client = client;
                resolve(client)
            })
        }
        while (attempt < max_attempts) {
            try {
                var promise = new Promise(execFunc);
                return await promise;
            }
            catch (err) {
                attempt++;
                await new Promise(resolve => setTimeout(resolve, connect_timeout));
            }
        }
        throw "Could not connect client to instance " + instanceId;
    }

    async spawnServer(instanceId) {
        var execFunc = (resolve, reject) => {
            var port = this.freePorts.pop();
            var pyd2bot_process = child_process.execFile(this.pyd2botExePath, ["--port", port, "--host", "0.0.0.0"], {"detached": true});
            this.runningInstances[instanceId] = {"port": port, "server" : pyd2bot_process, "client" : null, "connection" : null, "childs" : []};
            pyd2bot_process.stdout.on('data', (stdout) => {
                if (stdout.toString().includes("Server started")) {
                    console.log("Instance " + instanceId + " server started");
                    resolve(pyd2bot_process);
                }
            });
            pyd2bot_process.stderr.on('data', (stderr) => {
                if (!stderr.toString().includes("DEBUG") && !stderr.toString().includes("INFO") && !stderr.toString().includes("WARNING") && !stderr.toString().includes("ERROR")) {
                    console.log("Error : " + stderr.toString());
                    pyd2bot_process.kill()
                }
            });
            pyd2bot_process.on('close', async (code) => {
                console.log(`Server ${instanceId} exited with code ${code}`);
                this.freePorts.push(port);
                var instance = this.runningInstances[instanceId];
                if (!instance) {
                    console.log("Instance " + instanceId + " not found");
                }
                else {
                    instance.serverClosed = true
                    if (instance.connection){
                        instance.connection.end();
                    }
                    if (this.wantsToKillServer[instanceId]) {
                        this.wantsToKillClient[instanceId] = false;
                    }
                    else if (instance.runningSession) {
                        console.log("Instance " + instanceId + " server crashed");
                        console.log("running session : " + JSON.stringify(instance.runningSession))
                        const sessionsManager = require("../sessions/SessionsManager.js").instance;
                        sessionsManager.runSession(instance.runningSession)
                    }
                }
            });
            setTimeout(() => {
                this.freePorts.push(port);
                reject("Timeout : Could not start instance " + instanceId);
            }, 20000)
        }
        var promise = new Promise(execFunc);
        return await promise;
    }

    clear() {
        for (var instanceId in this.runningInstances) {
            this.killInstance(instanceId);
        }
    }

    killInstance(instanceId) {
        var instance = this.runningInstances[instanceId]
        if (instance) {
            if (instance.connection) {
                console.log("Killing client for instance " + instanceId);
                this.wantsToKillClient[instanceId] = true;
                instance.connection.end();
            }
            if (instance.server) {
                console.log("Killing server for instance " + instanceId);
                if (!instance.ServerClosed) {
                    this.wantsToKillServer[instanceId] = true;
                    instance.server.kill('SIGINT')
                }
            }
            if (instance.childs) {
                console.log("Killing childs for instance " + instanceId);
                instance.childs.forEach(child => {
                    this.killInstance(child);
                })
            }
            this.freePorts.push(instance.port);
            delete this.runningInstances[instanceId];
        }
    }

}

module.exports = InstancesManager;