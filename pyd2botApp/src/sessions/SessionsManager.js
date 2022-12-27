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
        this.sessionsDbFile = path.join(ejse.data('persistenceDir'), 'sessions.json');
        this.sessionsDB = require(this.sessionsDbFile);
        this.urls = {
            'manageSessionsUrl': "file://" + path.join(__dirname, 'ejs', 'sessionsManager.ejs'),
            'farmSessionFormUrl': "file://" + path.join(__dirname, 'ejs', 'newFarmSessionForm.ejs'),
            'fightSessionFormUrl': "file://" + path.join(__dirname, 'ejs', 'newFightSessionForm.ejs'),
        }
        this.currentEditedSession = null;
        ejse.data('sessions', this);
    }

    createSession(session) {
        if (this.currentEditedSession != null) {
            if (session.name != this.currentEditedSession.name) {
                delete this.sessionsDB[this.currentEditedSession.name];
            }
        }
        this.currentEditedSession = null;
        this.sessionsDB[session.name] = session;
        console.log(session);
    }

    deleteSession(key) {
        if (this.sessionsDB[key]) {
            delete this.sessionsDB[key];
        }
        else {
            console.log('Session not found');
        }
    }

    saveSessions() {
        var saveJson = JSON.stringify(this.sessionsDB, null, 2);
        fs.writeFile(this.sessionsDbFile, saveJson, 'utf8', (err) => {
            if (err) {
                console.log(err);
            }
        })
    }

    async runSession(sessionKey) {
        console.log("running session : " + sessionKey);
        var sessionData = this.sessionsDB[sessionKey];
        if (!sessionData) {
            console.log("Session " + sessionKey + " not found");
            return;
        }
        var leader = accountManager.charactersDB[sessionData.leaderId];
        var path = pathsManager.pathsDB[sessionData.pathId];
        var instanceKey = `${leader.name}(${leader.id})`;
        var leaderPort = instancesManager.getFreePort();
        leader.serverPort = leaderPort;
        var followers = [];
        var seller = null;
        this.sessionsDB[sessionKey].runningBots = Array();
        var leaderSession = {
            "key": instanceKey,
            "type": sessionData.type,
            "character": leader,
            "path": path,
            "unloadType": sessionData.unloadType
        }
        if (sessionData.type == "farm") {
            leaderSession = {
                ...leaderSession,
                "jobIds": sessionData.jobIds,
                "resourceIds": sessionData.resourceIds
            }
        }
        else if (sessionData.type == "fight") {
            for (var i = 0; i < sessionData.followersIds.length; i++) {
                let followerId = sessionData.followersIds[i];
                let follower = accountManager.charactersDB[followerId];
                let followerPort = instancesManager.getFreePort();
                follower.serverPort = followerPort;
                followers.push(follower);
            }
            leaderSession = {
                ...leaderSession,
                "monsterLvlCoefDiff": sessionData.monsterLvlCoefDiff,
                "followers": followers
            }
        }
        if (sessionData.unloadType == "seller") {
            seller = accountManager.charactersDB[sessionData.sellerId];
            seller.serverPort = instancesManager.getFreePort();
            leaderSession.seller = seller;
        }
        // console.log("will run session : " + JSON.stringify(session))
        var leaderBot = await this.runPyd2Bot(leaderSession);
        this.sessionsDB[sessionKey].runningBots.push(leaderBot);
        console.log("Done running session : " + instanceKey);
        for (var i = 0; i < sessionData.followersIds.length; i++) {
            var follower = accountManager.charactersDB[sessionData.followersIds[i]];
            var instanceKey = `${follower.name}(${follower.id})`;
            console.log("running follower session : " + instanceKey);
            var followerSession = {
                "key": instanceKey,
                "type": "fight",
                "character": follower,
                "leader": leader,
                "unloadType": sessionData.unloadType
            }
            if (followerSession.unloadType == "seller") {
                followerSession.seller = seller;
            } 
            var followerBot = await this.runPyd2Bot(followerSession);
            console.log("Done running session : " + instanceKey);
            this.sessionsDB[sessionKey].runningBots.push(followerBot)
        }
        if (followerSession.unloadType == "seller") {
            var instanceKey = `${seller.name}(${seller.id})`;
            var sellerSession = {
                "key": instanceKey,
                "type": "selling",
                "unloadType": null,
                "character": seller
            }
            var sellerBot = await this.runPyd2Bot(sellerSession);
            console.log("Done running session : " + instanceKey);
            this.sessionsDB[sessionKey].runningBots.push(sellerBot);
        }
        this.sessionsDB[sessionKey].isRunning = true;
    }

    isRunning(key) {
        var sessionData = this.sessionsDB[key];
        var character = accountManager.charactersDB[sessionData.leaderId]
        var inst = instancesManager.runningInstances[`${character.name}(${character.id})`]
        if (inst) {
            return true
        }
        return false
    }

    async runPyd2Bot(session) {
        if (!session.key) {
            throw new Error("Session key is required");
        }
        var instance = await instancesManager.spawn(session.key, session.character.serverPort);
        instance.runningSession = session;
        instance.serverClosed = false;
        var creds = accountManager.getAccountCreds(session.character.accountId);
        var apiKey = await accountManager.fetchAccountApiKey(session.character.accountId);
        instance.client.runSession(
            creds.login, 
            creds.password, 
            creds.certId, 
            creds.certHash, 
            apiKey,
            JSON.stringify(session)
        );
        console.debug("Run Session :" + (creds.login, creds.password, creds.certId, creds.certHash, apiKey, JSON.stringify(session)));
        return instance;
    }

    stopSession(key) {
        if (instancesManager.runningInstances[key]) {
            instancesManager.killInstance(key);
        }
    }

}
module.exports = SessionsManager;