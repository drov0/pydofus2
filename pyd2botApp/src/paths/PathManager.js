const path = require('path')
const fs = require('fs')
const ejse = require('ejs-electron')

class PathManager {
    static get instance() {
        return AccountManager._instance || (AccountManager._instance = new AccountManager()), AccountManager._instance
    }

    constructor() {
        this.pathsDbFile = path.join(ejse.data('persistenceDir'), 'paths.json')
        this.pathsDB = require(this.pathsDbFile)
        this.urls = {
            'managePathsUrl': "file://" + path.join(__dirname, 'ejs', 'pathsManager.ejs'),
            'newPathUrl': "file://" + path.join(__dirname, 'ejs', 'newPathForm.ejs'),
        }
        ejse.data('pathsUrls', this.urls);
    }

    newPath(formData) {
        this.pathsDB[formData.name] = {
            "name": formData.name,
            "type": formData.type,
        }
    }

    deletePath(key) {
        delete this.pathsDB[key]
    }

    savePaths() {
        var saveJson = JSON.stringify(this.pathsDB, null, 2);
        fs.writeFile(this.pathsDbFile, saveJson, 'utf8', (err) => {
            if (err) {
                console.log(err)
            }
        })
    }

}
module.exports = PathManager;