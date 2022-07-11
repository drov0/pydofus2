const path = require('path')
const fs = require('fs')
const ejse = require('ejs-electron')

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

}
module.exports = SessionsManager;