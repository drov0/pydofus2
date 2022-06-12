const path = require('path')
const fs = require('fs')
const ejse = require('ejs-electron')
const JSEncrypt = require('jsencrypt')



class AccountManager {
    static get instance() {
        return AccountManager._instance || (AccountManager._instance = new AccountManager()), AccountManager._instance
    }

    constructor() {
        this.dbFile = path.join(ejse.data('persistenceDir'), 'accounts.json')
        this.accountsDB = require(this.dbFile)
        var keysDir = path.join(process.env.AppData, 'pyd2bot', 'RSA-KEYS', 'password-crypting')
        var privateKeyPem = fs.readFileSync(path.join(keysDir, 'id_rsa'), 'utf8')
        var pubKeyPem = fs.readFileSync(path.join(keysDir, 'id_rsa.pub'), 'utf8')
        this.encrypt = new JSEncrypt();
        this.decrypt = new JSEncrypt();
        this.encrypt.setPublicKey(pubKeyPem)
        this.decrypt.setPrivateKey(privateKeyPem)
        this.urls = {
            'manageAccountsUrl': "file://" + path.join(__dirname, 'ejs', 'accountManager.ejs'),
            'manageCharactersUrl': "file://" + path.join(__dirname, 'ejs', 'charachterManager.ejs'),
            'newAccountUrl': "file://" + path.join(__dirname, 'ejs', 'newAccountForm.ejs')
        }
        ejse.data('accountUrls', this.urls);
    }

    getKeyPath() {
        return path.join(process.env.AppData, 'pyd2bot/keys/')
    }

    encryptPassword(password) {
    }

    // decryptPassword(encpassword) {
    // }

    newAccount(formData) {
        this.accountsDB[formData.entryId] = {
            "login": formData.login,
            "password": this.encrypt.encrypt(formData.password),
        }
    }

    deleteAccount(key) {
        delete this.accountsDB[key]
    }

    saveAccounts() {
        var saveJson = JSON.stringify(this.accountsDB, null, 2);
        fs.writeFile(this.dbFile, saveJson, 'utf8', (err) => {
            if (err) {
                console.log(err)
            }
        })
    }

}
module.exports = AccountManager;