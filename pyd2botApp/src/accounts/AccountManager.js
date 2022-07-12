const path = require('path')
const fs = require('fs')
const ejse = require('ejs-electron')
globalThis.window = {};
const JSEncrypt = require('jsencrypt')
const AuthHelper = require("../auth/AuthHelper.js");
const InstancesManager = require("../bot/InstancesManager.js");
const instancesManager = InstancesManager.instance;

class AccountManager {
    static get instance() {
        return AccountManager._instance || (AccountManager._instance = new AccountManager()), AccountManager._instance
    }

    constructor() {
        this.accountsDbFile = path.join(ejse.data('persistenceDir'), 'accounts.json')
        this.charactersDbFile = path.join(ejse.data('persistenceDir'), 'characters.json')
        this.accountsDB = require(this.accountsDbFile)
        this.charactersDB = require(this.charactersDbFile)
        this.accountsPasswords = {}
        this.authHelper = new AuthHelper();
        this.currentEditedAccount = null
        this.charactersChanged = false
        this.selectedAccount = null
        this.classesIconsDir = path.join(ejse.data('appDir'), 'assets', 'images', 'classes')
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
        this.breedName = {    
            1 : 'Feca',
            2 : 'Osamodas',
            3 : 'Enutrof',
            4 : 'Sram',
            5 : 'Xelor',
            6 : 'Ecaflip',
            7 : 'Eniripsa',
            8 : 'Iop',
            9 : 'Cra',
            10 : 'Sadida',
            11 : 'Sacrieur',
            12 : 'Pandawa',
            13 : 'Roublard',
            14 : 'Zobal',
            15 : 'Steamer',
            16 : 'Eliotrope',
            17 : 'Huppermage',
            18 : 'Ouginak'
        }
        ejse.data('accounts', this);

    }

    getClassIcon(key) {
        var character = this.charactersDB[key]
        return path.join(this.classesIconsDir, `symbole_${character.breedId}.png`)
    }

    getCharacterBreedName(breedId) {

    }

    getAccountPassword(key) {
        return this.decrypt.decrypt(this.accountsDB[key].password)
    }

    hideUnhidePassword(key) {
        console.log("before huide " + this.accountsPasswords[key])
        if (this.accountsPasswords[key] == "********") {
            var decryptedPassword = this.getAccountPassword(key)
            this.accountsPasswords[key] = decryptedPassword
        }
        else {
            this.accountsPasswords[key] = "********"
        }
        console.log("after huide " + this.accountsPasswords[key])
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

    fetchCharacters(key) {
        instancesManager.spawnServer(key);
        console.log("fetchCharacters " + key);
        setTimeout(() => {
            var client = instancesManager.spawnClient(key);
            var creds = this.getAccountCreds(key);
            console.log(creds)
            client.fetchAccountCharacters(creds.login, creds.password, creds.certId, creds.certHash, function(err, response) {
                if (err) {
                    console.log("Error while callling fetch : " + err);
                }
                console.log("fetched characters : " + JSON.stringify(response));
                instancesManager.killInstance(key);
                response.forEach(character => {
                    this.addCharacter({
                        "characterName": character.name,
                        "accountId": key,
                        "characterId": character.id,
                        "breedId": character.breedId,
                        "breedName": character.breedId,
                        "serverId": character.serverId,
                        "serverName": character.serverName,
                    });
                });
                this.saveCharacters();
            });
        }, 5000);
    }
}
module.exports = AccountManager;