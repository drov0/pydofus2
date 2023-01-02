const ipc = window.require('electron').ipcRenderer;

window.onerror = function(error, url, line) {
    ipc.send('errorInWindow', {"error": error, "url": url, "line": line});
};

var followersIds = Array();
var followersAccountIds = Array();
var jobsIds = Array();
var resourcesIds = Array();
var sellerId = null;
var unloadType = null;

function editSession(key) {
    ipc.send('editSession', key);
}

function saveSessions() {
    ipc.send('saveSessions');
}

function deleteSession(key) {
    ipc.send('deleteSession', key)
    document.getElementById(`session-${key}`).remove();
}

function cancelCreateSession() {
    ipc.send('cancelCreateSession');
}

function convertMS(ms) {
    var d, h, m, s;
    s = Math.floor(ms / 1000);
    m = Math.floor(s / 60);
    s = s % 60;
    h = Math.floor(m / 60);
    m = m % 60;
    d = Math.floor(h / 24);
    h = h % 24;
    dd = d > 0 ? d + " days, " : "";
    hh = h > 0 || d > 0 ? h + " hours, " : ""; 
    mm = m > 0 || h > 0 || d > 0 ? m + " minutes, " : "";
    return dd + hh + mm + s + " seconds.";
  };

var elapsedTime = {};
var startTime = {};
function runSession(key) {
    let sessionStatusTd = document.getElementById(`session-status-${key}`);
    let sessionElapsedTimeTd = document.getElementById(`session-elapsedTime-${key}`);
    let sessionEarnedKamasTd = document.getElementById(`session-earnedKamas-${key}`);
    sessionStatusTd.innerHTML = "running";
    let runStopButton = document.getElementById(`runstop_session-${key}`);
    let intervalId;
    ipc.send('runSession', key);

    ipc.once(`sessionStarted-${key}`, function(event){    
        runStopButton.innerHTML = '<i class="fas fa-stop" style="margin-left: -5px;"></i>  stop';
        runStopButton.onclick = () => stopSession(key);
        sessionStatusTd.innerHTML = "started";
        startTime[key] = new Date();
        intervalId = setInterval(function () {
            sessionElapsedTimeTd.innerHTML = convertMS(Date.now() - startTime[key]);
            ipc.send('fetchBotsKamas', key);
        }, 5000);
    });

    ipc.on(`sessionKamasFetched-${key}`, function(event, data) {
        sessionEarnedKamasTd.innerHTML = data;
    });

    ipc.once(`sessionStoped-${key}`, function(event) {
        clearInterval(intervalId);
        runStopButton.innerHTML = '<i class="fas fa-play" style="margin-left: -5px;"></i>  run';
        runStopButton.onclick = () => runSession(key);
        sessionStatusTd.innerHTML = "idle";
    });
}

function stopSession(key) {    
    var sessionStatusTd = document.getElementById(`session-status-${key}`);
    sessionStatusTd.innerHTML = "stopping";
    ipc.send('stopSession', key);
}

function createSession() {
    let sessionType = document.getElementById("sessionType").textContent
    let newSession;
    if (sessionType == "farm") {
        let farmer = JSON.parse(document.getElementById("farmer").value);
        newSession = {
            "name": document.getElementById("name").value,
            "path": document.getElementById("path").value,
            "type": sessionType,
            "farmer" : farmer.id,
            "jobIds": jobsIds,
            "resourcesIds": resourcesIds,
        }
        if (!newSession.jobIds.length) {
            alert("Please select at least one job");
            return;
        }
        if (!newSession.resourcesIds.length) {
            alert("Please select at least one resource");
            return;
        }
    }   
    else if (sessionType == "fight") {
        var leader = JSON.parse(document.getElementById("leader").value);
        newSession = {
            "name": document.getElementById("name").value,
            "path": document.getElementById("path").value,
            "type": sessionType,
            "monsterLvlCoefDiff" : document.getElementById("monsterLvlCoefDiff").value,
            "leaderId": leader.id,
            "followersIds": followersIds,
            "unloadType": unloadType,
            "sellerId": sellerId
        }
    }
    if (unloadType == "seller" && !sellerId) {
        alert("Please choose a seller");
        return;
    }
    if (!newSession.name) {
        alert("Please enter a name");
        return;
    }

    ipc.send('createSession', newSession)
}

// leader section
function onLeaderChange() {
    let leaderPhNode = document.getElementById("leader_ph")
    if (leaderPhNode) leaderPhNode.remove()
    followersIds.length = 0;
    followersAccountIds.length = 0;
    var followersListNode = document.getElementById("followers");
    followersListNode.innerHTML = "";
    populateFollowersSelectNode()
    sellerId = null
    populateSellerSelectNode()
}

// follower section
function addFollower() {
    var followerNode = document.getElementById("follower");
    var leaderNode = document.getElementById("leader");
    if (!leaderNode) {
        alert("You must select a leader first");
        return;
    }
    if (!followerNode.value)
        return;
    var follower = JSON.parse(followerNode.value);
    var leader = JSON.parse(leaderNode.value);
    if (follower.accountId == leader.accountId) {
        alert("A follower must be in a different account than the leader");
        return;
    }
    if (follower.serverId != leader.serverId) {
        alert("A follower must be from the same server as the leader");
        return;
    }
    if (followersAccountIds.includes(follower.accountId)) {
        alert("Followers must belong to different accounts");
        return;
    }
    addFollowerByValue(follower)
}

function addFollowerByValue(follower) { 
    var followersListNode = document.getElementById("followers");
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
    var [liNode, removeButton] = makeLiNode()
    liNode.textContent = `${follower.name} (${follower.serverName})`;
    liNode.character = JSON.stringify(follower);
    liNode.appendChild(removeButton);
    removeButton.addEventListener('click', (event) => {
        liNode.remove();
        followersIds.splice(followersIds.indexOf(follower.id), 1);
        followersAccountIds.splice(followersAccountIds.indexOf(follower.accountId), 1);
        addFollowerOption(follower);
        addSellerOption(follower);
    });
    document.getElementById(`sellerSelectOption-${follower.id}`).remove()
    document.getElementById(`followerSelectOption-${follower.id}`).remove()
    followersListNode.appendChild(liNode);
}

function addFollowerOption(ch) {
    var fNode = document.getElementById("follower");
    optionNode = document.createElement("option");
    optionNode.value = JSON.stringify(ch);
    optionNode.id = `followerSelectOption-${ch.id}`
    optionNode.textContent = `${ch.name} (${ch.serverName}, ${ch.breedName}, ${ch.level})`;
    fNode.appendChild(optionNode);
}

function populateFollowersSelectNode() {
    var leaderNode = document.getElementById("leader");
    if (leaderNode.value) {
        var leader = JSON.parse(leaderNode.value)
        var fNode = document.getElementById("follower");
        fNode.innerHTML = "<option selected disabled>Choose a follower to add</option>";
        var accounts = ipc.sendSync('getData', 'accounts');
        var characters = accounts.charactersDB;
        Object.entries(characters).forEach(([key, ch]) => {
            if (ch.accountId != leader.accountId && ch.serverId == leader.serverId && !followersAccountIds.includes(ch.accountId) && ch.id != sellerId) {
                addFollowerOption(ch)
            }
        })
    }
}

function populateFollowersListNode () {
    var sessionsData = ipc.sendSync('getSessionsData');
    var accounts = ipc.sendSync('getData', 'accounts');
    var curr = sessionsData.currentEditedSession;
    if (curr) {
        curr.followersIds.forEach(key => {
            follower = accounts.charactersDB[key];
            addFollowerByValue(follower)
        });
    }
}

// seller section
function onUnloadTypeChange() {    
    var sellerDivNode = document.getElementById("sellerDiv");
    unloadType = document.getElementById("unloadType").value;
    if (unloadType == "seller") {
        sellerDivNode.style.display = "flex";
        populateSellerSelectNode();
    } else {
        sellerDivNode.style.display = "none";
        if (sellerId != null) {
            var accounts = ipc.sendSync('getData', 'accounts');
            ch = accounts.charactersDB[sellerId];
            addFollowerOption(ch);
        }
    }
}

function onSellerChange() {
    let sellerPhNode = document.getElementById("seller_ph");
    if (sellerPhNode) 
        sellerPhNode.remove();
    let seller = JSON.parse(document.getElementById("seller").value);
    var accounts = ipc.sendSync('getData', 'accounts');
    if (sellerId != null) {
        ch = accounts.charactersDB[sellerId];
        addFollowerOption(ch);
    }
    sellerId = seller.id;
    document.getElementById(`followerSelectOption-${sellerId}`).remove();
}

function addSellerOption(ch) {
    var sNode = document.getElementById("seller");
    optionNode = document.createElement("option");
    optionNode.value = JSON.stringify(ch);
    optionNode.textContent = `${ch.name} (${ch.serverName}, ${ch.breedName}, ${ch.level})`;
    optionNode.id = `sellerSelectOption-${ch.id}`;
    sNode.appendChild(optionNode);
}

function populateSellerSelectNode() {
    var sessionsData = ipc.sendSync('getSessionsData');
    var accounts = ipc.sendSync('getData', 'accounts');
    var curr = sessionsData.currentEditedSession;
    var currSeller = curr ? accounts.charactersDB[curr.sellerId] : null;
    sellerId = curr ? curr.sellerId : null;
    var leaderNode = document.getElementById("leader");
    var sNode = document.getElementById("seller");
    if (leaderNode.value) {
        var leader = JSON.parse(leaderNode.value)
        if (!currSeller) {
            sNode.innerHTML = "<option id='seller_ph' selected disabled>Choose a seller</option>";
        } else {
            sNode.innerHTML = `<option value='${JSON.stringify(currSeller)}' selected disabled>${currSeller.name} (${currSeller.serverName}, ${currSeller.breedName}, ${currSeller.level})</option>`;
        }
        var accounts = ipc.sendSync('getData', 'accounts');
        var characters = accounts.charactersDB;
        Object.entries(characters).forEach(([key, ch]) => {
            if (ch.accountId != leader.accountId && ch.serverId == leader.serverId && !followersAccountIds.includes(ch.accountId) && ch.id != sellerId) {
                addSellerOption(ch);
            }
        });
    }
}

// resource section
 function populateResourcesSelect() { 
    const dofusData = ipc.sendSync('getData', 'dofus2Data');
    const skills = dofusData.skills;
    var jobsNode = document.getElementById("jobs");
    var resourceSelectNode = document.getElementById("resourceSelect");
    resourceSelectNode.innerHTML = "";
    jobsNode.childNodes.forEach( (li) => {
        if (li.value) {
            var jobId = li.value;
            var resources = skills[jobId].gatheredRessources;
            resources.forEach( (resource) => {
                var optionNode = document.createElement("option");
                optionNode.value = JSON.stringify(resource);
                optionNode.textContent = resource.name;
                optionNode.id = `resourceSelectOption-${resource.id}`;
                resourceSelectNode.appendChild(optionNode);
            });
        }
    })
}

function addJob() {
    const dofusData = ipc.sendSync('getData', 'dofus2Data');
    const skills = dofusData.skills;
    var jobsListNode = document.getElementById("jobs");
    var jobSelectNode = document.getElementById("jobSelect");
    var jobId = jobSelectNode.value
    if (!jobId)
        return;
    if (jobsIds.includes(jobId)) {
        alert("Job already added");
        return
    }
    jobsIds.push(jobId);
    var [liNode, button] = makeLiNode()
    liNode.textContent = skills[jobId].name;
    liNode.value = jobId;
    button.addEventListener('click', (event) => {
        liNode.remove();
        jobsIds.splice(jobsIds.indexOf(jobId), 1);
        var optionNode = document.createElement("option");
        optionNode.value = jobId;
        optionNode.textContent = liNode.textContent;
        optionNode.id = `jobSelectOption-${jobId}`;
        jobSelectNode.appendChild(optionNode);
        skills[jobId].gatheredRessources.forEach( (resource) => {
            var r = document.getElementById(`resourceSelectOption-${resource.id}`)
            if (r) {
                r.remove();
            }
            else {
                document.getElementById(`resourceLi-${resource.id}`).remove();
            }
        })
    });
    liNode.appendChild(button);
    jobsListNode.appendChild(liNode);
    document.getElementById(`jobSelectOption-${jobId}`).remove();
    populateResourcesSelect()
}

function populateJobsSelect() {
    const dofusData = ipc.sendSync('getData', 'dofus2Data');
    const skills = dofusData.skills;
    var jobSelectNode = document.getElementById("jobSelect");
    jobSelectNode.innerHTML = "";
    try {
        Object.entries(skills).forEach(([key, skill]) => {
            if (!jobsIds.includes(skill.id)) {
                var optionNode = document.createElement("option");
                optionNode.value = key;
                optionNode.textContent = skill.name;
                optionNode.id = `jobSelectOption-${skill.id}`;
                jobSelectNode.appendChild(optionNode);
            }
            else {
                throw "Jobs must be unique";
            }
        })
        populateResourcesSelect()
    }
    catch (err) {
        alert(err);
        return;
    }
}
    
function addResource() {
    var resourceSelectNode = document.getElementById("resourceSelect");
    var resourcesListNode = document.getElementById("resources");
    var resource = JSON.parse(resourceSelectNode.value);
    if (!resource.id)
        return;
    if (resourcesIds.includes(resource.id)) {
        alert("Resource already added");
        return
    }
    resourcesIds.push(resource.id);
    var [liNode, button] = makeLiNode()
    liNode.textContent = resource.name;
    liNode.id = `resourceLi-${resource.id}`;
    button.addEventListener('click', (event) => {
        liNode.remove();
        resourcesIds.splice(resourcesIds.indexOf(resource.id), 1);
        var optionNode = document.createElement("option");
        optionNode.value = JSON.stringify(resource);
        optionNode.textContent = resource.name;
        optionNode.id = `resourceSelectOption-${resource.id}`;
        resourceSelectNode.appendChild(optionNode);
    });
    liNode.appendChild(button);
    document.getElementById(`resourceSelectOption-${resource.id}`).remove();
    resourcesListNode.appendChild(liNode);
}

// misc
function makeLiNode() {
    var liNode = document.createElement("Li");
    liNode.className = "list-group-item";
    liNode.addEventListener('mouseover', (event) => {
        liNode.className = "list-group-item active";
    })
    liNode.addEventListener('mouseout', (event) => {
        liNode.className = "list-group-item";
    })
    liNode.style.display = "flex";
    liNode.style.flexDirection = "row";
    liNode.style.justifyContent = "space-between";
    var button = document.createElement("input");
    button.type = "button";
    button.value = "x";
    liNode.appendChild(button);
    return [liNode, button];
}

function initFightSessionForm() {
    onUnloadTypeChange()
    populateFollowersSelectNode()
    populateFollowersListNode()
}