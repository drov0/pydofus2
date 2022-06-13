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

function saveAccounts() {
    ipc.send('saveAccounts')
}

function deleteAccount(key) {
    ipc.send('deleteAccount', key)
}

function hideUnhidePassword(key) {
    ipc.send('hideUnhidePassword', key)
}

function createCharachter() {

}

function saveCharachters() {

}