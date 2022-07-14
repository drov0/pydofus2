const ipc = window.require('electron').ipcRenderer;

var followersIds = Array();
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

function stopSession(key) {
    ipc.send('stopSession', key)
}

function createSession() {
    var leader = JSON.parse(document.getElementById("leader").value);
    let newSession = {
        "name": document.getElementById("name").value,
        "path": document.getElementById("path").value,
        "type": document.getElementById("sessionType").textContent,
        "leader": leader.id,
        "followers": followersIds
    }
    ipc.send('createSession', newSession)
}

function addFollower() { 
    var followerList = document.getElementById("followers");
    var liNode = document.createElement("Li");
    var follower = JSON.parse(document.getElementById("follower").value);
    var leader = JSON.parse(document.getElementById("leader").value);
    if (follower.id == leader.id) {
        alert("A follower must be different than the leader");
        return;
    }
    try {
        followerList.childNodes.forEach(function(li) { 
            if (li.nodeType == Node.ELEMENT_NODE &&  `${follower.name} (${follower.serverName})` == li.textContent) {
                throw "already in list of followers";
            }
        });
    }
    catch(err) {
        alert(err);
        return;
    }
    followersIds.push(follower.id);
    liNode.className = "list-group-item";
    liNode.addEventListener('mouseover', (event) => {
        liNode.className = "list-group-item active";
    })
    liNode.textContent = `${follower.name} (${follower.serverName})`;
    liNode.addEventListener('mouseout', (event) => {
        liNode.className = "list-group-item";
    })
    liNode.style.display = "flex";
    liNode.style.flexDirection = "row";
    liNode.style.justifyContent = "space-between";
    var button = document.createElement("input");
    button.type = "button";
    button.value = "x";
    button.className = "bi bi-minus";
    button.id = "removeFollower";
    liNode.appendChild(button);
    button.addEventListener('click', (event) => {
        liNode.remove();
    });
    document.getElementById("followers").appendChild(liNode);
 }