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
            'farmSessionFormUrl': "file://" + path.join(__dirname, 'ejs', 'newFarmSessionForm.ejs'),
            'fightSessionFormUrl': "file://" + path.join(__dirname, 'ejs', 'newFightSessionForm.ejs'),
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
        this.sessionsDB[session.name] = session
        console.log(session)
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

    async runFollowerSession(follower, leader) {
        var key = follower.id
        if (instancesManager.runningInstances[key]) {
            instancesManager.killInstance(key);
        }
        var server = await instancesManager.spawnServer(key);
        var client = await instancesManager.spawnClient(key);
        console.log("running session : " + key);
        var creds = accountManager.getAccountCreds(follower.accountId);
        var sessionStr = JSON.stringify({
            "name": follower.name,
            "type": "fight",
            "character": follower,
            "leader": leader,
        })
        var instance = instancesManager.runningInstances[key];
        instance.runningSession = {"key": key, "creds": creds, sessionStr: sessionStr};
        client.runSession(creds.login, creds.password, creds.certId, creds.certHash, sessionStr);
    }

    async runSession(key) {
        if (instancesManager.runningInstances[key]) {
            instancesManager.killInstance(key);
        }
        var server = await instancesManager.spawnServer(key);
        var client = await instancesManager.spawnClient(key);
        var instance = instancesManager.runningInstances[key];
        console.log("running session : " + key);
        var session = this.sessionsDB[key];
        if (!session) {
            console.log("Session " + key + " not found")
            return
        }
        var leader = accountManager.charactersDB[session.leaderId]
        var path = pathsManager.pathsDB[session.pathId]
        var creds = accountManager.getAccountCreds(leader.accountId);
        if (session.type == "farm") {
            var sessionStr = JSON.stringify({
                "name": session.name,
                "type": session.type,
                "character": leader,
                "path": path,
                "jobIds": session.jobIds,
                "resourceIds": session.resourceIds
            })
        }
        else if (session.type == "fight") {
            var followers = undefined
            if (session.followersIds && session.followersIds.length > 0) {
                followers = []
                for (var i = 0; i < session.followersIds.length; i++) {
                    var follower = accountManager.charactersDB[session.followersIds[i]]
                    followers.push({"name": follower.name, "id": follower.id})
                    instancesManager.runningInstances[key].childs.push(follower.id)
                    await this.runFollowerSession(follower, leader)
                }
            }
            var sessionStr = JSON.stringify({
                "name": session.name,
                "type": session.type,
                "character": leader,
                "path": path,
                "monsterLvlCoefDiff": session.monsterLvlCoefDiff,
                "followers": followers
            })
        }
        instance.runningSession = {"key": key, "creds": creds, sessionStr: sessionStr};
        await client.runSession(creds.login, creds.password, creds.certId, creds.certHash, sessionStr);
    }

    async restartSession(sessionArgs) {
        var server = await instancesManager.spawnServer(sessionArgs.key);
        var client = await instancesManager.spawnClient(sessionArgs.key);
        console.log("restarting session : " + sessionArgs.key);
        var instance = instancesManager.runningInstances[sessionArgs.key];
        instance.runningSession = sessionArgs
        instance.serverClosed = false
        client.runSession(sessionArgs.creds.login, sessionArgs.creds.password, sessionArgs.creds.certId, sessionArgs.creds.certHash, sessionArgs.sessionStr);
    }

    stopSession(key) {
        if (instancesManager.runningInstances[key]) {
            instancesManager.killInstance(key);
        }
    }

}
module.exports = SessionsManager;