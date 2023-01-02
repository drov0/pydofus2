const path = require('path')
const fs = require('fs')
const ejse = require('ejs-electron')
const instancesManager = require("../bot/InstancesManager.js").instance;
const accountManager = require("../accounts/AccountManager.js").instance;
const pathsManager = require("../paths/PathManager.js").instance;
class SessionsManager {
    static get instance() {
        return SessionsManager._instance || (SessionsManager._instance = new SessionsManager()), SessionsManager._instance
    }

    constructor() {
        this.sessionsDbFile = path.join(ejse.data('persistenceDir'), 'sessions.json');
        this.sessionsDB = require(this.sessionsDbFile);
        this.sessionsOper = {}
        for (var key in this.sessionsDB) {
            this.sessionsOper[key] = this.newEmptyOperSession()
        }
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
        this.sessionsOper[session.name] = this.newEmptyOperSession();
        console.log(`Created new session : ${session}`);
    }

    newEmptyOperSession() {
        return {
            "status": "idle",
            "startTime": null,
            "elapsedTime": 0,
            "earnedKamas": 0,
            "runningBots": [],
            "event": null,
        }
    }

    deleteSession(key) {
        if (this.sessionsDB[key]) {
            if (this.sessionsOper[key].status != "idle") {
                console.log("Session is running, stop it first");
                return;
            }
            delete this.sessionsDB[key];
            delete this.sessionsOper[key];
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

    async runSession(sessionKey, event) {
        console.log("running session : " + sessionKey);
        var sessionData = this.sessionsDB[sessionKey];
        let runningBots = Array();
        if (!sessionData) {
            console.log("Session " + sessionKey + " not found");
            return;
        }
        var leader = accountManager.charactersDB[sessionData.leaderId];
        var path = pathsManager.pathsDB[sessionData.path];
        var instanceKey = `${leader.name}(${leader.id})`;
        var leaderPort = instancesManager.getFreePort();
        leader.serverPort = leaderPort;
        var followers = [];
        var seller = null;
        this.sessionsOper[sessionKey].event = event;
        var leaderSession = {
            "key": instanceKey,
            "type": sessionData.type,
            "character": leader,
            "path": path,
            "unloadType": sessionData.unloadType,
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
        runningBots.push(this.runPyd2Bot(sessionKey, leaderSession));
        for (var i = 0; i < sessionData.followersIds.length; i++) {
            var follower = accountManager.charactersDB[sessionData.followersIds[i]];
            var instanceKey = `${follower.name}(${follower.id})`;
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
            runningBots.push(this.runPyd2Bot(sessionKey, followerSession));
        }
        if (followerSession.unloadType == "seller") {
            var instanceKey = `${seller.name}(${seller.id})`;
            var sellerSession = {
                "key": instanceKey,
                "type": "selling",
                "unloadType": null,
                "character": seller
            }
            runningBots.push(this.runPyd2Bot(sessionKey, sellerSession));
        }
        this.sessionsOper[sessionKey].status = "started";
        await Promise.all(runningBots);
        event.sender.send(`sessionStarted-${sessionKey}`);
    }

    async runPyd2Bot(parentKey, session) {
        if (!session.key) {
            throw new Error("Session key is required");
        }
        console.log(`[SessionManager] running session : '${session.key}'`);
        return instancesManager.spawn(session.key, session.character.serverPort).then(
            (instance) => {        
                instance.runningSession = session;
                instance.serverClosed = false;
                instance.isSeller = session.unloadType === null;
                this.sessionsOper[parentKey].runningBots.push(instance);
                var creds = accountManager.getAccountCreds(session.character.accountId);
                accountManager.fetchAccountApiKey(session.character.accountId).then(
                    (apiKey) => {
                        console.log(`[SessionManager] session '${session.key}' run called`);
                        instance.originSessionKey = parentKey;
                        instance.client.runSession(
                            creds.login, 
                            creds.password, 
                            creds.certId, 
                            creds.certHash, 
                            apiKey,
                            JSON.stringify(session)
                        ).then(() => {return instance})
                    }
                );
            }
        );
    }

    async stopSession(key) {
        console.log("Stop Session : " + key)
        if (!key) {
            console.log("Can't stop session of undefined key");
        }
        var bots = this.sessionsOper[key].runningBots;
        for (let i = 0; i < bots.length; i += 1) {
            await instancesManager.killInstance(bots[i].key);
        }
        this.sessionsOper[key].status = "idle";
        this.sessionsOper[key].event.sender.send(`sessionStoped-${key}`);
    }

    fetchBotsKamas(event, sessionKey) {
        let runningBots = this.sessionsOper[sessionKey].runningBots;
        runningBots.forEach((instance) => {
            // console.log(`Getting kamas for instance ${instance.key}`);
            instance.client.getInventoryKamas().then((kamas) => {
                if (!instance.isSeller) {
                    // console.log(`Got kamas: ${kamas} for instance ${instance.key}`);
                    let oldKamas = instance.kamas;
                    instance.kamas = kamas; 
                    if (!oldKamas || kamas < oldKamas) // if oldKamas is undefined or delta is negative (because of a trade for example) 
                        oldKamas = kamas; // we set oldKamas to kamas to avoid negative delta
                    this.sessionsOper[sessionKey].earnedKamas += kamas - oldKamas; // we add the delta to the total earned kamas
                    event.data = this.sessionsOper[sessionKey].earnedKamas; // we set the data to the total earned kamas
                    event.sender.send(`sessionKamasFetched-${sessionKey}`, this.sessionsOper[sessionKey].earnedKamas);  // we send the event to the renderer
                }
            });
        });
    }
}
module.exports = SessionsManager;