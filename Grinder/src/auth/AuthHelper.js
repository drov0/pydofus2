const path = require('path');
const child_process = require('child_process');
const fs = require('fs');
const os = require('os');
const crypto = require('crypto');
var osPlatform = process.platform;
var getGuuidCmdPerPltf = {
    darwin: "ioreg -rd1 -c IOPlatformExpertDevice",
    win32: {
        native: "%windir%\\System32",
        mixed: "%windir%\\sysnative\\cmd.exe /c %windir%\\System32"
    }["win32" !== process.platform ? "" : "ia32" === process.arch && process.env.hasOwnProperty("PROCESSOR_ARCHITEW6432") ? "mixed" : "native"] + "\\REG.exe QUERY HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Cryptography /v MachineGuid",
    linux: "( cat /var/lib/dbus/machine-id /etc/machine-id 2> /dev/null || hostname ) | head -n 1 || :",
    freebsd: "kenv -q smbios.system.uuid || sysctl -n kern.hostuuid"
};

function hashWithSha256(str) {
    return crypto.createHash("sha256").update(str).digest("hex");
}

function parseMachineGuuidFromCmdStdOut(stdOut) {
    switch (process.platform) {
        case "darwin":
            return stdOut.split("IOPlatformUUID")[1].split("\n")[0].replace(/\=|\s+|\"/gi, "").toLowerCase();
        case "win32":
            return stdOut.toString().split("REG_SZ")[1].replace(/\r+|\n+|\s+/gi, "").toLowerCase();
        case "linux":
        case "freebsd":
            return stdOut.toString().replace(/\r+|\n+|\s+/gi, "").toLowerCase();
        default:
            throw new Error("Unsupported platform: " + process.platform);
    }
}

function machineIdSync(withSha256Hash) {
    var machineGuuid = parseMachineGuuidFromCmdStdOut(child_process.execSync(getGuuidCmdPerPltf[osPlatform]).toString());
    return withSha256Hash ? machineGuuid : hashWithSha256(machineGuuid);
}

function machineId(withSha256Hash) {
    return child_process.exec(getGuuidCmdPerPltf[osPlatform], (err, stdout, stderr) => {
        if (err)
            return console.log(new Error("Error while obtaining machine id: " + err.stack));
        var machineGuuid = parseMachineGuuidFromCmdStdOut(stdout.toString());
        return withSha256Hash ? machineGuuid : hashWithSha256(machineGuuid)
    })
}

class CryptoHelper {

    getUUID() {
        return [os.platform(), os.arch(), machineIdSync(), os.cpus().length, os.cpus()[0].model].join()
    }

    createHashFromString(str) {
        var md5Hasher = crypto.createHash("md5");
        var hash = md5Hasher.update(str);
        return hash.digest();
    }

    createHashFromStringSha(str) {
        var sha256Hasher = crypto.createHash("sha256");
        var hash = sha256Hasher.update(str);
        return hash.digest('hex').slice(0, 32);
    }

    encrypt(json, t) {
        var key = this.createHashFromString(t);
        var iv = crypto.randomBytes(16);
        var cipher = crypto.createCipheriv("aes-128-cbc", key, iv);
        var o = Buffer.from(JSON.stringify(json), "utf8");
        var a = Buffer.concat([s.update(o), cipher.final()]);
        return iv.toString("hex") + "|" + a.toString("hex")
    }

    generateHashFromCertif(cert, hashedMachineInfos, hashedMachineInfos_reversed) {
        let cipher = crypto.createDecipheriv("aes-256-ecb", hashedMachineInfos_reversed, "");
        let s = Buffer.concat([cipher.update(cert.encodedCertificate, "base64"), cipher.final()]);
        return crypto.createHash("sha256").update(hashedMachineInfos + s.toString()).digest("hex");
    }

    decryptFromFileWithUUID(filePath) {
        const uuid = this.getUUID();
        return this.decryptFromFile(filePath, uuid);
    }

    decryptFromFile(filePath, uuid) {
        let data = fs.readFileSync(filePath, "utf8")
        try {
            return this.decrypt(data, uuid);
        } catch (err) {
            console.log("[1019 CRYPTO_HELPER] cannot decrypt from file", filePath, err);
            throw err;
        }
    }

    decrypt(data, uuid) {
        var r = data.split("|");
        var iv = Buffer.from(r[0], "hex");
        var dataToDecrypt = Buffer.from(r[1], "hex");
        var key = this.createHashFromString(uuid);
        var decipher = crypto.createDecipheriv("aes-128-cbc", key, iv);
        var plainText = decipher.update(dataToDecrypt);
        var u = Buffer.concat([plainText, decipher.final()]).toString();
        var r = JSON.parse(u);
        return r;
    }
}

class AuthHelper {

    constructor() {
        this.cryptoHelper = new CryptoHelper();
    }

    getComputerRam() {
        return Math.pow(2, Math.round(Math.log(os.totalmem() / 1024 / 1024) / Math.log(2)))
    }

    getOsVersion() {
        var t, n;
        [t, n] = os.release().split(".");
        return parseFloat(`${t}.${n}`)
    }

    getApiKeysFolderPath() {
        return path.join(this.getZaapPath("userData"), "keydata")
    }

    getZaapPath(flag) {
        if (flag == "userData") {
            return path.join(process.env.AppData, 'zaap')
        }
    }

    getStoredCertificate(username) {
        const certFolder = this.getCertificateFolderPath()
        var certPath = path.join(certFolder, `.certif${this.cryptoHelper.createHashFromStringSha(username)}`);
        if (fs.existsSync(certPath))
            try {
                return {
                    certificate: this.cryptoHelper.decryptFromFileWithUUID(certPath),
                    filepath: certPath
                }
            } catch (e) {
                console.log(`[1020 AUTH_HELPER] delete indecipherable certificate on ${certPath}`, e);
                try {
                    fs.unlinkSync(certPath)
                } catch (e) {
                    console.log(`[1030 AUTH_HELPER] Impossible to delete certificate file : ${e.message}`)
                }
            }
        return Promise.resolve(null)
    }

    generateApiForAccount(username, t, n) {
        return this.getStoredCertificate(username).then(async r => {
            if (r) {
                const {
                    certificate: certificate,
                    filepath: filepath
                } = r;
                let certHash;
                try {
                    certHash = this.generateHashFromCertif(certificate)
                } catch (r) {
                    s.error(`[1022 AUTH_HELPER] Error on generateHashFromCertif, \n ${r} \n delete certificate on ${filepath}`);
                    try {
                        fs.unlinkSync(filepath)
                    } catch (e) {
                        s.warn(`[1032 AUTH_HELPER] Impossible to delete certificate file : ${e.message}`)
                    }
                    return this.Haapi.instance.get("ankama.api.createApiKey", username, t, n).then(e => e)
                }
                const certId = certificate.id;
                return this.Haapi.instance.get("ankama.api.createApiKey", username, t, n, certId, certHash).then(e => (e.certificate = certificate, e))
            }
            return this.Haapi.instance.get("ankama.api.createApiKey", username, t, n).then(e => e)
        })
    }

    generateHashFromCertif(cert) {
        const {
            hm1: hashedMachineInfos,
            hm2: hashedMachineInfos_reversed
        } = this.createHmEncoders();
        return this.cryptoHelper.generateHashFromCertif(cert, hashedMachineInfos, hashedMachineInfos_reversed)
    }

    getCertificateFolderPath() {
        return path.join(this.getZaapPath("userData"), 'certificate');
    }

    createHmEncoders() {
        let data = [];
        data.push(os.arch());
        data.push(os.platform());
        data.push(machineIdSync());
        data.push(os.userInfo().username);
        data.push(this.getOsVersion());
        data.push(this.getComputerRam());
        let machineInfos = data.join("");
        const hashedMachineInfos = this.cryptoHelper.createHashFromStringSha(machineInfos);
        let hashedMachineInfos_reversed = hashedMachineInfos.split("").reverse().join("");
        return {
            hm1: hashedMachineInfos,
            hm2: hashedMachineInfos_reversed
        }
    }
}

module.exports = AuthHelper;