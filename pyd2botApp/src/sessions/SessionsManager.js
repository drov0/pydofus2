const path = require('path')
const fs = require('fs')
const ejse = require('ejs-electron')
const instancesManager = require("../bot/InstancesManager.js").instance;
const { session } = require('electron');
const accountManager = require("../accounts/AccountManager.js").instance;
const pathsManager = require("../paths/PathManager.js").instance;
class SessionsManager {
    static get instance() {
        return SessionsManager._instance || (SessionsManager._instance = new SessionsManager()), SessionsManager._instance
    }

    constructor() {
        this.sessionsDbFile = path.join(ejse.data('persistenceDir'), 'sessions.json')
        this.sessionsDB = require(this.sessionsDbFile)
        this.urls = {
            'manageSessionsUrl': "file://" + path.join(__dirname, 'ejs', 'sessionsManager.ejs'),
            'newSessionUrl': "file://" + path.join(__dirname, 'ejs', 'newSessionForm.ejs'),
        }
        this.currentEditedSession = null
        ejse.data('sessions', this);
    }

    createSession(session) {
        if (this.currentEditedSession != null) {
            if (session.name != this.currentEditedSession.name) {
                delete this.sessionsDB[this.currentEditedSession.name]
            }
        }
        this.currentEditedSession = null
        this.sessionsDB[session.name] = path
    }

    deleteSession(key) {
        if (this.sessionsDB[key]) {
            delete this.sessionsDB[key]
        }
        else {
            console.log('Session not found')
        }
    }

    saveSessions() {
        var saveJson = JSON.stringify(this.sessionsDB, null, 2);
        fs.writeFile(this.sessionsDbFile, saveJson, 'utf8', (err) => {
            if (err) {
                console.log(err)
            }
        })
    }

    async runSession(key) {
        if (instancesManager.runningInstances[key]) {
            instancesManager.killInstance(key);
        }
        instancesManager.spawnServer(key);
        console.log("running session : " + key);
        var result = await (new Promise(resolve => { 
            setTimeout(() => {
                var client = instancesManager.spawnClient(key);
                var session = this.sessionsDB[key];
                session.character = accountManager.charactersDB[session.characterId.toString()]
                session.path = pathsManager.pathsDB[session.pathId]
                var creds = accountManager.getAccountCreds(session.character.accountId);
                var sessionStr = JSON.stringify(session);
                client.runSession(creds.login, creds.password, creds.certId.toString(), creds.certHash, sessionStr, function(err, response) {
                    if (err) {
                        resolve('start failed : ' + err);
                    }
                });
                resolve('started');
            }, 5000);
        }));
        if (result == 'started') {
            return true;
        }
        else {
            console.log(result);
            return false;
        }
    }

    stopSession(key) {
        if (instancesManager.runningInstances[key]) {
            instancesManager.killInstance(key);
        }
    }

}
module.exports = SessionsManager;