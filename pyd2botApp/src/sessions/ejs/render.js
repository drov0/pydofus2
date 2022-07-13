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

function stopSession(key) {
    ipc.send('stopSession', key)
}

function createSession() {
    var listfollowers = document.getElementById("followers").childNodes;
    var followersNames = [];
    listfollowers.forEach(function(li) {
        followersNames.push(li.textContent.split(" (")[0]);
    });
    let newSession = {
        "name": document.getElementById("name").value,
        "pathId": document.getElementById("pathId").value,
        "type": document.getElementById("type").value,
        "leader": document.getElementById("leader").value,
        "followers": followersNames
    }
    ipc.send('createSession', newSession)
}

function addFollower() { 
    var followerList = document.getElementById("followers");
    var liNode = document.createElement("Li");
    var follower = document.getElementById("follower").value;
    var leader = document.getElementById("leader").value;
    if (follower == leader) {
        alert("A follower must be different than the leader");
        return;
    }
    try {
        followerList.childNodes.forEach(function(li) { 
            if (li.nodeType == Node.ELEMENT_NODE &&  follower == li.textContent) {
                throw "already in list of followers";
            }
        });
    }
    catch(err) {
        alert(err);
        return;
    }
    var textnode = document.createTextNode(follower);
    liNode.appendChild(textnode);
    liNode.className = "list-group-item";
    liNode.addEventListener('mouseover', (event) => {
        liNode.className = "list-group-item active";
    })
    liNode.textContent = follower;
    liNode.addEventListener('mouseout', (event) => {
        liNode.className = "list-group-item";
    })
    liNode.style.display = "flex";
    liNode.style.flexDirection = "row";
    liNode.style.justifyContent = "space-between";
    var button = document.createElement("input");
    button.type = "button";
    button.value = "-";
    button.className = "bi bi-minus";
    button.id = "removeFollower";
    liNode.appendChild(button);
    button.addEventListener('click', (event) => {
        liNode.remove();
    });
    document.getElementById("followers").appendChild(liNode);
 }