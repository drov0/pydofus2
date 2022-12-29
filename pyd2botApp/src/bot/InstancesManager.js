const path = require('path');
const child_process = require('child_process');
const process = require('process');
const thrift = require('thrift');
const Pyd2botService = require('../pyd2botService/Pyd2botService.js');
const ejse = require('ejs-electron');
class InstancesManager {

    // this class manages the running instances of pyd2bot
    static get instance() {
        return InstancesManager._instance || (InstancesManager._instance = new InstancesManager()), InstancesManager._instance
    }

    constructor() {
        this.pyd2botExePath = path.join(process.env.AppData, 'pyd2bot', 'pyd2bot.exe');
        this.pyd2botDevPath = path.join(ejse.data("appDir"), '..', '..', 'pyd2bot','pyd2bot.py');
        this.pyd2botDevEnvPath = path.join(ejse.data("appDir"), '..', '..', '.venv', 'Scripts', 'python.exe');
        this.runningInstances = {};
        this.freePorts = Array(100).fill().map((element, index) => index + 9999);
        this.wantsToKillServer = {};
        this.wantsToKillClient = {};
        ejse.data('runningInstances', this.runningInstances);
    }

    async spawnClient(instanceId) {
        const max_attempts = 5;
        var attempt = 0;
        const retry_connect_timeout = 1000;                
        var clientConnectionPromise = new Promise((resolve, reject) => {
            var instance = this.runningInstances[instanceId];
            if (!instance) {
                console.log("Instance " + instanceId + " not found");
                return
            }
            var transport = thrift.TBufferedTransport;
            var protocol = thrift.TBinaryProtocol;
            instance.clientStatus = "connecting";
            var connection = thrift.createConnection("127.0.0.1", instance.port, {
                transport : transport,
                protocol : protocol,
            });
            connection.on('error', (err) => {
                if (err.toString().includes("ECONNRESET")) {
                    if (!instance.wantsToKillServer) {
                        console.log(`[Client - ${instanceId}] Server closed the connection unexpectedly!`);
                    }
                }
                else {
                    console.log(`[Client - ${instanceId}] Error : ${err}`);
                }
                instance.clientStatus = "down";        
                if (instance.clientStatus === "connecting") {
                    reject(err);
                }
            });
            connection.on('timeout', (err) => {
                console.log("Connecting client of instance '" + instanceId + "' timed out") 
            });
            connection.on('close', (err) => {
                if (!instance.wantsToKillClient && instance.serverStatus !== "down") {
                    console.log(`[Client - ${instanceId}] Closed the connection unexpectedly with error: ${err}`);
                }
                else {
                    console.log(`[Client - ${instanceId}] Closed with error: ${err}`);
                }
                instance.clientStatus = "down";
                if (instance.clientStatus === "connecting") {
                    reject("Client connection of instance '" + instanceId + "' closed with error: " + err);
                }
            });
            connection.on('connect', (err) => {
                instance.clientStatus = "connected";
                console.log(`[Client - ${instanceId}] connected to server on port ${instance.port}`); 
                var client = thrift.createClient(Pyd2botService, connection);
                if (instance.connection) {
                    instance.wantsToKillClient = true;
                    instance.connection.end();
                }
                instance.connection = connection;
                instance.client = client;
                resolve(client);
            });
        });
        while (attempt < max_attempts) {
            try {
                return await clientConnectionPromise;
            }
            catch (err) {
                attempt++;
                console.log(err + ", for the " + attempt + " time. will retry after " + retry_connect_timeout + " seconds.")
                await new Promise((resolve) => setTimeout(resolve, retry_connect_timeout))
            }
        }
        console.error("Could not connect client to instance '" + instanceId + "' after " + max_attempts + " attempts");
        return null;
    }

    getFreePort() {
        return this.freePorts.pop();
    }

    freePort(port) {
        if (!this.freePorts.includes(port))
            this.freePorts.push(port);
    }

    async spawnServer(instanceId, port, originSessionKey=null) {
        var execFunc = (resolve, reject) => {
            var instance = {
                "key": instanceId, 
                "port": port, 
                "server" : null, 
                "client" : null, 
                "connection" : null, 
                "childs" : [], 
                "wantsToKillServer" : false,
                "wantsToKillClient" : false,
                "serverStatus": "connecting",
                "clientStatus": "down",
                "originSessionKey": originSessionKey,
            };
            let timeoutId = setTimeout(() => {
                this.freePorts.push(port);
                reject("Timeout : Could not start thrift server for instance '" + instanceId + "' on port " + port);
            }, 20000)
            var pyd2bot_process = child_process.execFile(this.pyd2botExePath, ['--port', port, '--host', '0.0.0.0', '--id', instanceId])
            this.runningInstances[instanceId] = instance;
            instance.server = pyd2bot_process;

            pyd2bot_process.stdout.on('data', async (stdout) => {
                let stdout_str = stdout.toString()
                if (stdout_str.includes(`[Server - ${instanceId}] Started listening on 0.0.0.0:${port}`)) {
                    if (instance.serverStatus === "connecting") {
                        instance.serverStatus = "started";
                        console.log(`[Server - ${instanceId}] Started listening on 0.0.0.0:${port}`);
                        clearTimeout(timeoutId);
                        resolve(pyd2bot_process);
                    }
                }
                if (stdout_str.includes(`[Server - ${instanceId}] Error while running session:`)) {
                    console.log(`[Server - ${instanceId}] Error while running session: \n${stdout_str.split("Error while running session:")[1]}`);
                }
                if (stdout_str.includes(`[Server - ${instanceId}] Stop called`)) {
                    instance.wantsToKillClient = true;
                }
                if (stdout_str.includes(`[Server - ${instanceId}] Goodbye crual world!`)) {
                    await ejse.data('sessions').stopSession(instance.originSessionKey);
                    ejse.data('sessions').sessionsDB[instance.originSessionKey].event.sender.send(`sessionStoped-${instance.originSessionKey}`);
                }
            });

            pyd2bot_process.stderr.on('data', (stderr) => {
                if (!stderr.toString().includes("DEBUG") && !stderr.toString().includes("INFO") && !stderr.toString().includes("WARNING")) {
                    console.log(`[Server - ${instanceId}] error - ${stderr}`);
                }
            });

            pyd2bot_process.on('exit', function(code) {
                instance.serverStatus = "down";
                InstancesManager.instance.freePort(port);
                if (instance.wantsToKillServer)
                    console.log(`[Server - ${instanceId}] Killed as expected with code ${code}`);
                else 
                    console.log(`[Server - ${instanceId}] Exited unexpectedly with code ${code}`);
                if (!instance) {
                    console.log(`[Server - ${instanceId}] Instance not found!`);
                }
                if (!instance.wantsToKillServer && instance.runningSession) {
                    console.log(`[Server - ${instanceId}] Crashed unexpectedly while running a session!, restarting the session...`);
                    if (instance.connection) {
                        instance.wantsToKillClient = true;
                        instance.connection.end();
                    }
                    ejse.data('sessions').runPyd2Bot(instance.runningSession);
                }
            });

            pyd2bot_process.on('close', async (code) => {
                instance.serverStatus = "down";
                console.log(`[Server - ${instanceId}] Closed with code ${code}`);

            });
        }
        var promise = new Promise(execFunc);
        return await promise;
    }

    clear() {
        for (var instanceId in this.runningInstances) {
            this.killInstance(instanceId);
        }
    }

    async spawn(instanceId, port, originSessionKey=undefined) {
        await this.spawnServer(instanceId, port, originSessionKey);
        await this.spawnClient(instanceId);
        return this.runningInstances[instanceId];
    }
    
    async killInstance(instanceId) {
        var instance = this.runningInstances[instanceId];
        console.log("kill Instance '" + instanceId + "' called");
        if (instance) {
            if (instance.server) {
                const disconnect_timeout = 20000;
                var execFunc = (resolve, reject) => {
                    var serverExited = false, clientExited = false;
                    clientExited = (instance.clientStatus === "down");
                    serverExited = (instance.serverStatus === "down");
                    var timeoutID = setTimeout(() => reject(`Connection close for instance ${instanceId} timed out!`), disconnect_timeout);
                    if (serverExited && clientExited) {
                        resolve();
                        clearTimeout(timeoutID);
                    }
                    if (!serverExited) {
                        instance.server.on('exit', (code) => {
                            serverExited = true;
                            if (clientExited) {
                                resolve();
                                clearTimeout(timeoutID);
                            }
                        });

                    }
                    if (!clientExited) {
                        instance.connection.on('close', (err) => {
                            clientExited = true;
                            if (serverExited) {
                                resolve();
                                clearTimeout(timeoutID); 
                            }
                        });
                    }
                    console.log(`[Instances manager] Wants to kill server and client of instance : ${instanceId}`);
                    instance.wantsToKillServer = true;
                    instance.wantsToKillClient = true;
                    instance.server.kill('SIGINT');
                }
                var promiseConnectionClosed = new Promise(execFunc);
                await promiseConnectionClosed;
                this.freePort(instance.port);
                delete this.runningInstances[instanceId];
                console.log(`[Instances manager] Instance ${instanceId} killed successfully!`);
            }
        }
        else {
            console.log("Instance '" + instanceId + "' not found.");
        }
    }

}

module.exports = InstancesManager;