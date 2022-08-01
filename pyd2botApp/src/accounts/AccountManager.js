const path = require('path')
const fs = require('fs')
const ejse = require('ejs-electron')
globalThis.window = {};
const JSEncrypt = require('jsencrypt')
const AuthHelper = require("../auth/AuthHelper.js");
const InstancesManager = require("../bot/InstancesManager.js");
const instancesManager = InstancesManager.instance;
const defaultBreedConfig = {
    10: { // sadida
        "primarySpellId" : 13516, // ronce
        "primaryStat" : 10 // force
    },
    4 : { // sram
        "primarySpellId" : 12902, // Truanderie
        "primaryStat" : 10 // force
    },
}
class AccountManager {
    static get instance() {
        return AccountManager._instance || (AccountManager._instance = new AccountManager()), AccountManager._instance
    }

    constructor() {
        this.accountsDbFile = path.join(ejse.data('persistenceDir'), 'accounts.json')
        this.charactersDbFile = path.join(ejse.data('persistenceDir'), 'characters.json')
        this.apiKeysDbFile = path.join(ejse.data('persistenceDir'), 'apiKeys.json')
        this.accountsDB = require(this.accountsDbFile)
        this.charactersDB = require(this.charactersDbFile)
        this.apiKeysDB = require(this.apiKeysDbFile)
        this.accountsPasswords = {}
        this.authHelper = new AuthHelper();
        this.currentEditedAccount = null
        this.charactersChanged = false
        this.selectedAccount = null
        this.classesIconsDir = path.join(ejse.data('appDir'), 'assets', 'images', 'classes')
        this.currentView = "accounts"
        for (var key in this.accountsDB) {
            this.accountsPasswords[key] = "********"
        }
        var keysDir = path.join(process.env.AppData, 'pyd2bot', 'RSA-KEYS', 'password-crypting')

        if (!fs.existsSync(path.join(keysDir, 'public.pem')) || !fs.existsSync(path.join(keysDir, 'public.pem'))) {
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
            'manageCharactersUrl': "file://" + path.join(__dirname, 'ejs', 'characterManager.ejs'),
            'newAccountUrl': "file://" + path.join(__dirname, 'ejs', 'newAccountForm.ejs'),
            'characterProfileUrl': "file://" + path.join(__dirname, 'ejs', 'characterProfile.ejs'),
        }
        ejse.data('accounts', this);

    }

    getClassIcon(key) {
        var character = this.charactersDB[key]
        return path.join(this.classesIconsDir, `symbol_${character.breedId}.png`)
    }

    getAccountPassword(key) {
        return this.decrypt.decrypt(this.accountsDB[key].password)
    }

    hideUnhidePassword(key) {
        if (this.accountsPasswords[key] == "********") {
            var decryptedPassword = this.getAccountPassword(key)
            this.accountsPasswords[key] = decryptedPassword
        }
        else {
            this.accountsPasswords[key] = "********"
        }
    }

    newAccount(formData) {
        var encryptedPassword = this.encrypt.encrypt(formData.password)
        var currentAccount = ejse.data('currentEditedAccount')
        if (currentAccount != null) {
            if (formData.entryId != currentAccount.id) {
                delete this.accountsDB[currentAccount.id]
                for (var [key, character] of Object.entries(this.charactersDB)) {
                    if (currentAccount.id == character.accountId) {
                        this.charactersDB[key].accountId = formData.entryId
                    }
                }
                this.charactersChanged = true
            }
        }
        this.accountsDB[formData.entryId] = {
            "login": formData.login,
            "password": encryptedPassword,
        }
        this.accountsPasswords[formData.entryId] = "********"
        this.currentEditedAccount = null 
    }

    deleteAccount(key) {
        delete this.accountsDB[key]
    }

    getAccountCreds(key) {
        var account = this.accountsDB[key]
        var r = this.authHelper.getStoredCertificate(account.login)
        if (!r) {
            alertt("No certificate found for account " + account.login)
            return
        }
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
        for (var [key, account] of Object.entries(this.accountsDB)) {
            this.accountsDB[key] = {
                "login": account.login,
                "password": this.encrypt.encrypt(account.password)
            }
        }
        var saveJson = JSON.stringify(this.accountsDB, null, 2);
        fs.writeFile(this.accountsDbFile, saveJson, 'utf8', (err) => {
            if (err) {
                console.log(err)
            }
        })
        if (this.charactersChanged) {
            this.saveCharacters()
            this.charactersChanged = false
        }
    }

    saveCharacters() {
        var saveJson = JSON.stringify(this.charactersDB, null, 2);
        fs.writeFile(this.charactersDbFile, saveJson, 'utf8', (err) => {
            if (err) {
                console.log(err)
            }
        })
    }

    saveBreedSpells() {
        var saveJson = JSON.stringify(ejse.data('dofus2Data').breedSpells, null, 2);
        fs.writeFile(path.join(ejse.data('persistenceDir'), 'breedSpells.json'), saveJson, 'utf8', (err) => {
            if (err) {
                console.log(err)
            }
        })
    }

    addCharacter(character) {
        this.charactersDB[character.characterId] = character
    }

    deleteCharacter(key) {
        delete this.charactersDB[key]
    }

    clearCharacters() {
        for (var key in this.charactersDB) {
            delete this.charactersDB[key]
        }
    }

    saveApiKeys() {
        var saveJson = JSON.stringify(this.apiKeysDb, null, 2);
        fs.writeFile(path.join(ejse.data('persistenceDir'), 'apiKeys.json'), saveJson, 'utf8', (err) => {
            if (err) {
                console.log(err)
            }
        })
    }

    async getAccountApiKey(key) {
        var apiKeyData = this.apiKeysDB[key]
        if (!apiKeyData) {
            var apiKeyData = await instance.client.getApiKey()
            this.apiKeysDB[key] = apiKeyData
            this.saveApiKeys()
        }
        else {
            var expiredate = Date.parse(apiKeyData.expiration_date)
            if (expiredate < Date.now()) {
                console.log("API key expired, generating new one")
                var apiKeyData = await instance.client.getApiKey()
                this.apiKeysDB[key] = apiKeyData
                this.saveApiKeys()
            }
        }
        return apiKeyData.key
    }

    async fetchCharacters(key) {
        var instance = await instancesManager.spawn(key)
        var apiKey = this.getAccountApiKey(key)
        var creds = this.getAccountCreds(key)
        console.log(creds)
        var response = await instance.client.fetchAccountCharacters(creds.login, creds.password, creds.certId, creds.certHash, apiKey)
        console.log("fetcheCharacters result: " + JSON.stringify(response))
        for (let ck in response) {
            var character = response[ck]
            console.log("character: " + JSON.stringify(character))
            if (!ejse.data('dofus2Data').breedSpells[character.breedId])
            {
                var spells = {}
                var breedSpellsResponse = await instance.client.fetchBreedSpells(character.breedId)
                Object.values(breedSpellsResponse).forEach(spell => {
                    spells[spell.id] = spell
                })
                ejse.data('dofus2Data').breedSpells[character.breedId] = spells
                this.saveBreedSpells()
            }  
            character.accountId = key
            var defaultConfig = defaultBreedConfig[character.breedId]
            if (defaultConfig) {
                character.primarySpellId = defaultBreedConfig[character.breedId].primarySpellId
                character.primaryStatId = defaultBreedConfig[character.breedId].primaryStat
            }
            this.charactersDB[character.id] = character
        }
        console.log("fetch characters ended")
        AccountManager.instance.saveCharacters()
        instancesManager.killInstance(key)
    }
}
module.exports = AccountManager;