const JSEncrypt = require('jsencrypt')
const encryptAlgorithm = {
    name: "RSA-OAEP",
    hash: {
        name: "SHA-1"
    }
};
var encrypt = new JSEncrypt();
class CryptoHelper {

    arrayBufferToBase64String(arrayBuffer) {
        var byteArray = new Uint8Array(arrayBuffer)
        var byteString = '';
        for (var i = 0; i < byteArray.byteLength; i++) {
            byteString += String.fromCharCode(byteArray[i]);
        }
        return btoa(byteString);
    }

    base64StringToArrayBuffer(b64str) {
        var byteStr = atob(b64str);
        var bytes = new Uint8Array(byteStr.length);
        for (var i = 0; i < byteStr.length; i++) {
            bytes[i] = byteStr.charCodeAt(i);
        }
        return bytes.buffer;
    }

    textToArrayBuffer(str) {
        var buf = unescape(encodeURIComponent(str)); // 2 bytes for each char
        var bufView = new Uint8Array(buf.length);
        for (var i = 0; i < buf.length; i++) {
            bufView[i] = buf.charCodeAt(i);
        }
        return bufView;
    }

    convertPemToBinary(pem) {
        var lines = pem.split('\n');
        var encoded = '';
        for (var i = 0; i < lines.length; i++) {
            if (lines[i].trim().length > 0 &&
                lines[i].indexOf('-BEGIN RSA PRIVATE KEY-') < 0 &&
                lines[i].indexOf('-BEGIN RSA PUBLIC KEY-') < 0 &&
                lines[i].indexOf('-BEGIN PUBLIC KEY-') < 0 &&
                lines[i].indexOf('-END PUBLIC KEY-') < 0 &&
                lines[i].indexOf('-END RSA PRIVATE KEY-') < 0 &&
                lines[i].indexOf('-END RSA PUBLIC KEY-') < 0) {
                encoded += lines[i].trim();
            }
        }
        return base64StringToArrayBuffer(encoded);
    }

    static importPublicKey(pemKey) {
        return new Promise(function (resolve) {
            var importer = crypto.subtle.importKey("spki", convertPemToBinary(pemKey), encryptAlgorithm, false, ["encrypt"]);
            importer.then(function (key) {
                resolve(key);
            });
        });
    }

    static importPrivateKey(pemKey) {
        return new Promise(function (resolve) {
            var importer = crypto.subtle.importKey("pkcs8", convertPemToBinary(pemKey), encryptAlgorithm, true, ["decrypt"]);
            importer.then(function (key) {
                resolve(key);
            });
        });
    }
}
module.exports = CryptoHelper;