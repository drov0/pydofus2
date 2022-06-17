const AuthHelper = require("./authHelper.js");

var ah = new AuthHelper();
var login = 'aloone-100';
var r = ah.getStoredCertificate(login);
var certId = r.certificate.id;
let certHash = ah.generateHashFromCertif(r.certificate);
