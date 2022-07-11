const ipc = window.require('electron').ipcRenderer;

function editPath(key) {
    ipc.send('editPath', key)
}

function savePaths() {
    ipc.send('savePaths')
}

function deletePath(key) {
    ipc.send('deletePath', key)
}

function cancelCreatePath() {
    ipc.send('cancelCreatePath')
}
function createPath() {
    let newPath = {
        "name": document.getElementById("pathName").value,
        "type": document.getElementById("pathType").value,
        "fightOnly": document.getElementById("fightOnly").checked ? true : false,
        "monsterLvlCoefDiff": document.getElementById("monsterLvlCoefDiff").value,
        "startVertex" : {
            "mapId": document.getElementById("startMapId").value,
            "mapRpZone": document.getElementById("startMapRpZone").value,
        },
        "subAreaId": document.getElementById("subAreaId").value,
    }
    ipc.send('createPath', newPath)
}
