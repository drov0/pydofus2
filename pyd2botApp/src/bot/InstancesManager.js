const path = require('path');
const child_process = require('child_process');
const process = require('process');
const thrift = require('thrift');
const Pyd2botService = require('../pyd2botService/Pyd2botService.js');
const ejse = require('ejs-electron')

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

    spawnClient(instanceId) {
        var inst = this.runningInstances[instanceId];
        var transport = thrift.TBufferedTransport;
        var protocol = thrift.TBinaryProtocol;
        var connection = thrift.createConnection("127.0.0.1", inst.port, {
            transport : transport,
            protocol : protocol
        });
        connection.on('error', function(err) {
            if (InstancesManager.instance.wantsToKillClient[instanceId]) {
                InstancesManager.instance.wantsToKillClient[instanceId] = false;
            }
            else {
                console.log("Error in client : " + err);
            }
        });
        var client = thrift.createClient(Pyd2botService, connection);
        if (inst.connection) {
            this.wantsToKillClient[instanceId] = true;
            inst.connection.end();
        }
        inst.connection = connection;
        inst.client = client;
        return client;
    }

    spawnServer(instanceId) {
        var port = this.freePorts.pop();
        var cmd = `source ${this.pyd2botDevEnvPath} && python ${this.pyd2botDevPath} --host 0.0.0.0 --port ${port}`
        console.log(cmd);
        var log = "";
        var instance = child_process.execFile(this.pyd2botExePath, ["--port", port, "--host", "0.0.0.0"])
        this.runningInstances[instanceId] = {"port": port, "server" : instance, "client" : null, "connection" : null};
        instance.stdout.on('data', (stdout) => {
            log += stdout;
            console.log(stdout.toString());
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
        return instance
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