var socket = io(); // This line should be at the top of your scripts.js file


document.addEventListener('DOMContentLoaded', function() {
    // Start sniffer
    document.getElementById('start-btn').addEventListener('click', function() {
        sendSnifferCommand('/start_sniffer');
    });

    // Stop sniffer
    document.getElementById('stop-btn').addEventListener('click', function() {
        sendSnifferCommand('/stop_sniffer');
    });
});

socket.on('connect', function() {
    console.log('Socket connected.');
});


socket.on('new_message', function(data) {
    // Handle new message
    // Update the messages in the tab corresponding to data.conn_id
    updateMessageDisplay(data.conn_id, data.message, data.from_client);
});

socket.on('sniffer_crash', function(data) {
    // Handle sniffer crash
    // Display the error message to the user
    alert("Sniffer crashed: " + data.error);
});

function sendSnifferCommand(url) {
    var xhr = new XMLHttpRequest();
    xhr.open('POST', url, true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.onreadystatechange = function() {
        if (xhr.readyState === 4 && xhr.status === 200) {
            var response = JSON.parse(xhr.responseText);
            if(response.success) {
                console.log('Sniffer command successful');
                // Update UI or perform other actions based on success
            } else {
                console.error('Sniffer command failed');
                // Handle failure
            }
        }
    };
    xhr.send(JSON.stringify({}));
}

function updateMessageDisplay(connId, message, fromClient) {
    var tabContentDiv = document.getElementById('tab-content-' + connId);
    if (!tabContentDiv) {
        createNewTab(connId);
        tabContentDiv = document.getElementById('tab-content-' + connId);
    }
    var contentBody = tabContentDiv.querySelector('.tab-content-body');
    appendMessageToTab(contentBody, message, fromClient);
}

function createNewTab(connId) {
    var tabLabelsContainer = document.getElementById('tab-labels-container');
    var tabContainer = document.getElementById('tab-container');

    // Create the tab label with a close button
    var tabLabel = document.createElement('li');
    tabLabel.className = 'tab-label';
    tabLabel.dataset.target = 'tab-content-' + connId;
    tabLabel.innerHTML = 'Connection ' + connId + 
    '<span class="tab-button-spacing"></span>' + // For spacing
    '<button class="tab-close-button">×</button>';
    tabLabelsContainer.appendChild(tabLabel);

    // Create the tab content with a clear content button
    var tabContentDiv = document.createElement('div');
    tabContentDiv.id = 'tab-content-' + connId;
    tabContentDiv.className = 'tab-content';
    tabContainer.appendChild(tabContentDiv);

    // Create a clear content button
    var clearButton = document.createElement('button');
    clearButton.textContent = 'Clear Content';
    clearButton.className = 'clear-content-button'; // Add a class for styling
    clearButton.onclick = function() {
        var contentBody = tabContentDiv.querySelector('.tab-content-body');
        if (!contentBody) {
            console.error('Could not find tab content body');
            return;
        }
        contentBody.innerHTML = '';
    };
    tabContentDiv.appendChild(clearButton);

    // Add a div for the tab content body witrh class 'tab-content-body'
    var contentBody = document.createElement('div');
    contentBody.className = 'tab-content-body';
    tabContentDiv.appendChild(contentBody);
    
    // Add click event to the tab label for switching tabs
    tabLabel.addEventListener('click', function(event) {
        if (event.target.classList.contains('tab-close-button')) {
            // Close tab logic here
            tabLabelsContainer.removeChild(tabLabel);
            tabContainer.removeChild(tabContentDiv);
            return;
        }
        
        var targetId = this.dataset.target;
        var contents = document.getElementsByClassName('tab-content');
        var labels = document.getElementsByClassName('tab-label');

        // Hide all contents and remove active class from labels
        for (var i = 0; i < contents.length; i++) {
            contents[i].style.display = 'none';
            labels[i].classList.remove('active');
        }

        // Show the clicked tab content and set label as active
        document.getElementById(targetId).style.display = 'block';
        this.classList.add('active');
    });
}

function appendMessageToTab(tabContentDiv, msg, fromClient) {
    console.log('Appending message to tab:', msg);
    var messageContainer = document.createElement('div');
    messageContainer.className = 'message-container';

    var toggleLabel = document.createElement('label');
    toggleLabel.className = 'message-toggle';
    toggleLabel.textContent = msg['__receptionTime__'] + '-' + msg['__type__'];
    toggleLabel.style.color = fromClient ? '#28a745' : '#007bff'; // Green if from client, Blue otherwise

    var detailsDiv = document.createElement('div');
    detailsDiv.className = 'message-details';
    delete msg['__type__'];
    delete msg['__receptionTime__'];
    delete msg['__direction__'];
    detailsDiv.textContent = JSON.stringify(msg, null, 2);
    detailsDiv.style.display = 'none'; // Initially hide details

    toggleLabel.onclick = function() {
        detailsDiv.style.display = detailsDiv.style.display === 'none' ? 'block' : 'none';
    };

    messageContainer.appendChild(toggleLabel);
    messageContainer.appendChild(detailsDiv);
    tabContentDiv.appendChild(messageContainer);
}
