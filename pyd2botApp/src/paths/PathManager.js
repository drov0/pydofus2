const path = require('path')
const fs = require('fs')
const ejse = require('ejs-electron')

class PathManager {
    static get instance() {
        return PathManager._instance || (PathManager._instance = new PathManager()), PathManager._instance
    }

    constructor() {
        this.pathsDbFile = path.join(ejse.data('persistenceDir'), 'paths.json')
        this.pathsDB = require(this.pathsDbFile)
        this.urls = {
            'managePathsUrl': "file://" + path.join(__dirname, 'ejs', 'pathsManager.ejs'),
            'newPathUrl': "file://" + path.join(__dirname, 'ejs', 'newPathForm.ejs'),
        }
        this.types = ['RandomSubAreaFarmPath']
        this.currentEditedPath = null
        ejse.data('paths', this);
    }

    createPath(path) {
        if (this.currentEditedPath != null) {
            if (path.name != this.currentEditedPath.name) {
                delete this.pathsDB[this.currentEditedPath.name]
            }
        }
        this.currentEditedPath = null
        this.pathsDB[path.name] = path
    }

    deletePath(key) {
        if (this.pathsDB[key]) {
            delete this.pathsDB[key]
        }
        else {
            console.log('Path not found')
        }
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