const ipc = window.require('electron').ipcRenderer;

function editSession(key) {
    ipc.send('editSession', key)
}

function saveSessions() {
    ipc.send('saveSessions')
}

function deleteSession(key) {
    ipc.send('deleteSession', key)
}

function cancelCreateSession() {
    ipc.send('cancelCreateSession')
}

function runSession(key) {
    ipc.send('runSession', key)
}

function createSession() {
    let newSession = {
        "name": document.getElementById("name").value,
        "characterId": document.getElementById("characterId").value,
        "spellId": document.getElementById("spellId").value,
        "pathId": document.getElementById("pathId").checked ? true : false,
        "statToUp": document.getElementById("statToUp").value
    }
    ipc.send('createSession', newSession)
}
