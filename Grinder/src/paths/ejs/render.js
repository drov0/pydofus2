const ipc = window.require('electron').ipcRenderer;
window.onerror = function(error, url, line) {
    ipc.send('errorInWindow', {"error": error, "url": url, "line": line});
};
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
        "startVertex" : {
            "mapId": document.getElementById("startMapId").value,
            "mapRpZone": document.getElementById("startMapRpZone").value,
        },
    }
    if (!newPath.name || !newPath.startVertex.mapId) {
        alert("Invalid input")
        return
    }
    ipc.send('createPath', newPath)
}
