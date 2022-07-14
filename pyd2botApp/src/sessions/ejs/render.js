const ipc = window.require('electron').ipcRenderer;

var followersIds = Array();
var followersAccountIds = Array();
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
        "monsterLvlCoefDiff" : document.getElementById("monsterLvlCoefDiff").value,
        "leader": leader.id,
        "followers": followersIds,
    }
    if (!newSession.name) {
        alert("Please enter a name");
        return;
    }
    ipc.send('createSession', newSession)
}

function addFollower() { 
    var followersListNode = document.getElementById("followers");
    var liNode = document.createElement("Li");
    if (!document.getElementById("follower").value)
        return;
    var follower = JSON.parse(document.getElementById("follower").value);
    var leader = JSON.parse(document.getElementById("leader").value);
    if (follower.accountId == leader.accountId) {
        alert("A follower must be in a different account than the leader");
        return;
    }
    if (follower.serverId != leader.serverId) {
        alert("A follower must be from the same server as the leader");
        return;
    }
    console.log("account ids : " + JSON.stringify(followersAccountIds));
    console.log(follower);
    if (followersAccountIds.includes(follower.accountId)) {
        alert("Followers must belong to different accounts");
        return;
    }
    try {
        followersListNode.childNodes.forEach(function(li) {
            if (li.character) {
                var nch = JSON.parse(li.character);
                if (nch.serverId != follower.serverId) {
                    throw "All followers must belong to the same server";
                }
            }
        })
    }
    catch (err) {
        alert(err);
        return;
    }
    if (followersAccountIds.includes(follower.accountId)) {
        alert("Followers must be in different accounts");
        return;
    }
    followersIds.push(follower.id);
    followersAccountIds.push(follower.accountId);
    liNode.className = "list-group-item";
    liNode.addEventListener('mouseover', (event) => {
        liNode.className = "list-group-item active";
    })
    liNode.textContent = `${follower.name} (${follower.serverName})`;
    liNode.character = JSON.stringify(follower);
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
        followersIds.splice(followersIds.indexOf(follower.id), 1);
        followersAccountIds.splice(followersAccountIds.indexOf(follower.accountId), 1);
        populateFollowersSelect()
    });
    followersListNode.appendChild(liNode);
    populateFollowersSelect()
}

function populateFollowersSelect() { 
    var leader = JSON.parse(document.getElementById("leader").value);
    var fNode = document.getElementById("follower");
    fNode.innerHTML = "";
    var characters = ipc.sendSync('getCharactersData');
    Object.entries(characters).forEach(([key, ch]) => {
        if (ch.accountId != leader.accountId && ch.serverId == leader.serverId && !followersAccountIds.includes(ch.accountId)) {
            optionNode = document.createElement("option");
            optionNode.value = JSON.stringify(ch);
            optionNode.textContent = `${ch.name} (${ch.serverName}, ${ch.breedName})`;
            fNode.appendChild(optionNode);
        }
    })
 }