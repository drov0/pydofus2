const path = require('path')
const fs = require('fs')
const ejse = require('ejs-electron')
globalThis.window = {};
const JSEncrypt = require('jsencrypt')
const AuthHelper = require("../auth/AuthHelper.js");



class AccountManager {
    static get instance() {
        return AccountManager._instance || (AccountManager._instance = new AccountManager()), AccountManager._instance
    }

    constructor() {
        this.accountsDbFile = path.join(ejse.data('persistenceDir'), 'accounts.json')
        this.charachtersDbFile = path.join(ejse.data('persistenceDir'), 'charachters.json')
        this.accountsDB = require(this.accountsDbFile)
        this.charachtersDB = require(this.charachtersDbFile)
        this.accountsPasswords = {}
        this.authHelper = new AuthHelper();

        for (var key in this.accountsDB) {
            this.accountsPasswords[key] = "********"
        }
        var keysDir = path.join(process.env.AppData, 'pyd2bot', 'RSA-KEYS', 'password-crypting')

        if (!fs.existsSync(path.join(keysDir, 'public.pem')) || !fs.existsSync(path.join(keysDir, 'public.pem'))) {
            console.log('Generating RSA keys...')
            var encrypt = new JSEncrypt();

            // Generate a RSA key pair using the `JSEncrypt` library.
            var crypt = new JSEncrypt({ default_key_size: 2048 });
            var PublicPrivateKey = {
                PublicKey: crypt.getPublicKey(),
                PrivateKey: crypt.getPrivateKey()
            };
            this.publicKey = PublicPrivateKey.PublicKey;
            this.privateKey = PublicPrivateKey.PrivateKey;

            // Save the public and private keys to the filesystem.
            fs.writeFileSync(path.join(keysDir, 'public.pem'), this.publicKey);
            fs.writeFileSync(path.join(keysDir, 'private.pem'), this.privateKey);
        }
        else {
            console.log('RSA keys already exist.')
            this.publicKey = fs.readFileSync(path.join(keysDir, 'public.pem'), 'utf8');
            this.privateKey = fs.readFileSync(path.join(keysDir, 'private.pem'), 'utf8');
        }

        this.encrypt = new JSEncrypt();
        this.decrypt = new JSEncrypt();
        this.encrypt.setPublicKey(this.publicKey)
        this.decrypt.setPrivateKey(this.privateKey)
        this.urls = {
            'manageAccountsUrl': "file://" + path.join(__dirname, 'ejs', 'accountManager.ejs'),
            'manageCharachtersUrl': "file://" + path.join(__dirname, 'ejs', 'charachterManager.ejs'),
            'newAccountUrl': "file://" + path.join(__dirname, 'ejs', 'newAccountForm.ejs'),
        }
        ejse.data('accountUrls', this.urls);
    }

    hideUnhidePassword(key) {
        if (this.accountsPasswords[key] == "********") {
            var decryptedPassword = this.decrypt.decrypt(this.accountsDB[key].password)
            this.accountsPasswords[key] = decryptedPassword
        }
        else {
            this.accountsPasswords[key] = "********"
        }
    }

    newAccount(formData) {
        var encryptedPassword = this.encrypt.encrypt(formData.password)
        this.accountsDB[formData.entryId] = {
            "login": formData.login,
            "password": encryptedPassword,
        }
        this.accountsPasswords[formData.entryId] = "********"
    }

    deleteAccount(key) {
        delete this.accountsDB[key]
    }

    getAccountCreds(key) {
        var account = this.accountsDB[key]
        var r = this.authHelper.getStoredCertificate(account.login)
        var certId = r.certificate.id
        var certHash = this.authHelper.generateHashFromCertif(r.certificate)
        return {
            "login": account.login,
            "password": this.decrypt.decrypt(account.password),
            "certId": certId,
            "certHash": certHash
        }
    }

    saveAccounts() {
        var saveJson = JSON.stringify(this.accountsDB, null, 2);
        fs.writeFile(this.accountsDbFile, saveJson, 'utf8', (err) => {
            if (err) {
                console.log(err)
            }
        })
    }

    saveCharachters() {
        var saveJson = JSON.stringify(this.charachtersDB, null, 2);
        fs.writeFile(this.charachtersDbFile, saveJson, 'utf8', (err) => {
            if (err) {
                console.log(err)
            }
        })
    }

    addCharachter(accountId, charachter) {
        this.charachtersDB[`${charachter.name}(${charachter.serverId})`] = {
            "characterName": charachter.name,
            "accountId": accountId,
            "charachterId": parseFloat(charachter.id),
            "serverId": parseInt(charachter.serverId)
        }
    }

}
module.exports = AccountManager;