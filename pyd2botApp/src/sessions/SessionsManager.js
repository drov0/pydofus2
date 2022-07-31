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

    async runFollowerSession(character, leader, leaderInstance) {
        var instanceKey = `${character.name}(${character.id})`
        console.log("running follower session : " + instanceKey);
        var session = {
            "key": instanceKey,
            "type": "fight",
            "character": character,
            "leader": leader
        }
        await this.runSessionLow(session)
        console.log("Done running session : " + instanceKey)
        leaderInstance.childs.push(character.id)
    }

    async runSession(sessionKey) {
        console.log("running session : " + sessionKey);
        var sessionData = this.sessionsDB[sessionKey];
        if (!sessionData) {
            console.log("Session " + sessionKey + " not found")
            return
        }
        var leader = accountManager.charactersDB[sessionData.leaderId]
        var path = pathsManager.pathsDB[sessionData.pathId]
        var instanceKey = `${leader.name}(${leader.id})`
        var leaderPort = instancesManager.getFreePort()
        leader.serverPort = leaderPort
        var followers = []
        var session = {
            "key": instanceKey,
            "type": sessionData.type,
            "character": leader,
            "path": path,
        }
        if (sessionData.type == "farm") {
            session = {
                ...session,
                "jobIds": sessionData.jobIds,
                "resourceIds": sessionData.resourceIds
            }
        }
        else if (sessionData.type == "fight") {
            for (var i = 0; i < sessionData.followersIds.length; i++) {
                console.log(i)
                var follower = accountManager.charactersDB[sessionData.followersIds[i]]
                var followerPort = instancesManager.getFreePort()
                follower.serverPort = followerPort
                followers.push(follower)
            }
            session = {
                ...session,
                "monsterLvlCoefDiff": sessionData.monsterLvlCoefDiff,
                "followers": followers
            }
        }
        console.log("will run session : " + JSON.stringify(session))
        var leaderInstance = await this.runSessionLow(session)
        console.log("Done running session : " + instanceKey);
        for (var i = 0; i < sessionData.followersIds.length; i++) {
            var follower = accountManager.charactersDB[sessionData.followersIds[i]]
            await this.runFollowerSession(follower, leader, leaderInstance)
        }

    }

    async runSessionLow(session, port) {
        if (!session.key) {
            throw new Error("Session key is required")
        }
        var instance = await instancesManager.spawn(session.key, port);
        instance.runningSession = session
        instance.serverClosed = false
        var creds = accountManager.getAccountCreds(session.character.accountId)
        instance.client.runSession(
            creds.login, 
            creds.password, 
            creds.certId, 
            creds.certHash, 
            JSON.stringify(session)
        );
        console.debug("Run Session :" + (creds.login, creds.password, creds.certId, creds.certHash, JSON.stringify(session)))
        return instance
    }

    stopSession(key) {
        if (instancesManager.runningInstances[key]) {
            instancesManager.killInstance(key);
        }
    }

}
module.exports = SessionsManager;