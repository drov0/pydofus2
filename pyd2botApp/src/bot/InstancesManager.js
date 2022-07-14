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
                console.log("Connected the client to instance " + instanceId  + " server");
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
            var instance = child_process.execFile(this.pyd2botExePath, ["--port", port, "--host", "0.0.0.0"])
            this.runningInstances[instanceId] = {"port": port, "server" : instance, "client" : null, "connection" : null};
            instance.stdout.on('data', (stdout) => {
                if (stdout.toString().includes("Server started")) {
                    console.log("Instance " + instanceId + " server started");
                    resolve(instance);
                }
            });
            instance.stderr.on('data', (stderr) => {
                console.log("Error : " + stderr.toString());
            });
            instance.on('close', (code) => {
                console.log(`child process exited with code ${code}`);
                if (instance.connection){
                    instance.connection.end();
                }
                this.freePorts.push(port);
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
        if (this.runningInstances[instanceId]) {
            var i = this.runningInstances[instanceId]
            if (i.connection) {
                console.log("Killing client for instance " + instanceId);
                this.wantsToKillClient[instanceId] = true;
                i.connection.end();
            }
            if (i.server) {
                console.log("Killing server for instance " + instanceId);
                this.wantsToKillServer[instanceId] = true;
                i.server.kill('SIGINT')
            }
            this.freePorts.push(i.port);
            delete this.runningInstances[instanceId];
        }
    }

}

module.exports = InstancesManager;