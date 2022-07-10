$("#btnLeft").click(function () {
    var selectedItem = $("#rightValues option:selected");
    $("#leftValues").append(selectedItem);
});

$("#btnRight").click(function () {
    var selectedItem = $("#leftValues option:selected");
    $("#rightValues").append(selectedItem);
});

$("#rightValues").change(function () {
    var selectedItem = $("#rightValues option:selected");
    $("#txtRight").val(selectedItem.text());
});

function editPath(key) {
    ipc.send('editPath', key)
}

function savePaths() {
    ipc.send('savePaths')
}

function deletePath(key) {
    ipc.send('deletePath', key)
}

function createPath() {
    let newPath = {
        "name": document.getElementById("pathName").value,
        "type": document.getElementById("pathType").value,
        "fightOnly": document.getElementById("fightOnly").value,
        "monsterLvlCoefDiff": document.getElementById("monsterLvlCoefDiff").value,
        "startMapId": document.getElementById("startMapId").value,
        "startMapRpZone": document.getElementById("startMapRpZone").value,
        "subAreaId": document.getElementById("subAreaId").value,
    }
    ipc.send('createPath', newPath)
}
