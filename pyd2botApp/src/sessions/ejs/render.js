const ipc = window.require('electron').ipcRenderer;

var followersIds = Array();
var followersAccountIds = Array();
var jobsIds = Array();
var resourcesIds = Array();
function editSession(key) {
    ipc.send('editSession', key)
}

function saveSessions() {
    ipc.send('saveSessions')
}

function deleteSession(key) {
    ipc.send('deleteSession', key)
    document.getElementById(`session-${key}`).remove();
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
    var sessionType = document.getElementById("sessionType").textContent
    let newSession;
    if (sessionType == "farm") {
        var farmer = JSON.parse(document.getElementById("farmer").value);
        newSession = {
            "name": document.getElementById("name").value,
            "path": document.getElementById("path").value,
            "type": sessionType,
            "farmer" : farmer.id,
            "jobIds": jobsIds,
            "resourcesIds": resourcesIds,
        }
        if (!newSession.jobs.length) {
            alert("Please select at least one job");
            return;
        }
        if (!newSession.resources.length) {
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
        }
    }
    if (!newSession.name) {
        alert("Please enter a name");
        return;
    }

    ipc.send('createSession', newSession)
}

function addFollower() { 
    var followersListNode = document.getElementById("followers");
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
    var [liNode, button] = makeLiNode()
    liNode.textContent = `${follower.name} (${follower.serverName})`;
    liNode.character = JSON.stringify(follower);
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
    var accounts = ipc.sendSync('getData', 'accounts');
    var characters = accounts.charactersDB;
    Object.entries(characters).forEach(([key, ch]) => {
        if (ch.accountId != leader.accountId && ch.serverId == leader.serverId && !followersAccountIds.includes(ch.accountId)) {
            optionNode = document.createElement("option");
            optionNode.value = JSON.stringify(ch);
            optionNode.textContent = `${ch.name} (${ch.serverName}, ${ch.breedName})`;
            fNode.appendChild(optionNode);
        }
    })
 }

 function populateResourcesSelect() { 
    const dofusData = ipc.sendSync('getData', 'dofus2Data');
    const skills = dofusData.skills;
    var jobsNode = document.getElementById("jobs");
    console.log(jobsNode.innerHTML);
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
            })
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