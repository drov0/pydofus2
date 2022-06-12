const ipc = window.require('electron').ipcRenderer;

function createAccount() {
    let accountId = document.getElementById("accountId").value;
    let accountLogin = document.getElementById("accountLogin").value;
    let accountPassword = document.getElementById("accountPassword").value;
    let newAccount = {
        "entryId": accountId,
        "login": accountLogin,
        "password": accountPassword
    }
    ipc.send('newAccount', newAccount)
}