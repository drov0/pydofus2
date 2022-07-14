const ipc = window.require('electron').ipcRenderer;
var currentVisible = "accounts";

// accounts
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

function editAccount(key) {
    ipc.send('editAccount', key)
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

// characters
function saveCharacters() {
    ipc.send('saveCharacters')
}

function fetchCharacters(key) {  
    ipc.send('fetchCharacters', key)
}

function deleteCharacter(key) {
    document.getElementById(key).remove()
    ipc.send('deleteCharacter', key)
}

function clearCharacters() {
    document.getElementById("accountsTableBody").innerHTML = "";
    ipc.send('clearCharacters')
}

function goToCharacterProfile(key) {  
    ipc.send('goToCharacterProfile', key)
}

function cancelCharacterProfileEdit() {
    ipc.send('cancelCharacterProfileEdit')
}

function switchToAccountsView() {
    document.getElementById("accountsView").style.display = "flex";
    document.getElementById("charactersView").style.display = "none";
    currentVisible = "accounts";
}

function switchToCharactersView() {
    document.getElementById("accountsView").style.display = "none";
    document.getElementById("charactersView").style.display = "flex";
    currentVisible = "characters";
}