const { app, BrowserWindow, Menu, ipcMain } = require('electron');
const path = require('path')
const ejse = require('ejs-electron')
ejse.data('nodeModulesUrl', "file://" + path.join(__dirname, '..', 'node_modules'));
ejse.data('sidebarUrl', path.join(__dirname, 'ejs', 'sidebar.ejs'));
ejse.data('cssUrl', "file://" + path.join(__dirname, 'assets', 'css'));
ejse.data('persistenceDir', path.join(__dirname, '..', '..', 'pyd2botDB'))
ejse.data('pyd2botDir', )
ejse.data('appDir', path.join(__dirname));
ejse.data('dofus2Data', {
    "skills": require(path.join(ejse.data('persistenceDir'), 'skills.json')),
    "stats": {
        "strength": 10,
        "agility": 14,
        "vitality": 11,
        "intelligence": 15,
        "wisdom": 12,
        "chance": 13,
    },
    'breedSpells': require(path.join(ejse.data('persistenceDir'), 'breedSpells.json')),
})
const mainUrl = "file://" + path.join(__dirname, 'ejs', 'main.ejs')
const loadingPageUrl = "file://" + path.join(__dirname, 'ejs', 'loading.ejs')
const pathsManager = require('./paths/PathManager.js').instance;
const accountManager = require("./accounts/AccountManager.js").instance;
const sessionsManager = require("./sessions/SessionsManager.js").instance;
let mainWindow;
let loadingWindow;
// Handle creating/removing shortcuts on Windows when installing/uninstalling.
if (require('electron-squirrel-startup')) {
    // eslint-disable-line global-require
    app.quit();
}

app.disableHardwareAcceleration()

const createWindow = () => {

    // Create the browser window.
    mainWindow = new BrowserWindow({
        webPreferences: {
            nodeIntegration: true,
            contextIsolation: false,
        },
        show: false,
    });

    loadingWindow = new BrowserWindow({
        parent: mainWindow, 
        show: false, 
        frame: false, 
        transparent: true, 
        hasShadow: false, 
        resizable: false,
        modal: true,
        webPreferences: {
            nodeIntegration: true,
            contextIsolation: false,
            enableRemoteModule: true,
        },
    });
    loadingWindow.loadURL(loadingPageUrl);

    // and load the index.html of the app.
    mainWindow.loadURL(sessionsManager.urls.manageSessionsUrl);

    // To maximize the window
    mainWindow.maximize();
    mainWindow.show();

    const mainMenu = Menu.buildFromTemplate(mainMenuTemplate);
    Menu.setApplicationMenu(mainMenu);
    // Open the DevTools.
    // mainWindow.webContents.openDevTools();
};


// Accounts manager ipcs mapping
ipcMain.on("newAccount", (event, formData) => {
    accountManager.newAccount(formData);
    mainWindow.loadURL(accountManager.urls.manageAccountsUrl);
});

ipcMain.on("editAccount", (event, key) => {
    account = accountManager.accountsDB[key]
    accountManager.currentEditedAccount = { 
        "id" : key, 
        "login" : account.login,
        "password" : accountManager.getAccountPassword(key)	
    }
    mainWindow.loadURL(accountManager.urls.newAccountUrl);
});

ipcMain.on("deleteAccount", (event, key) => {
    accountManager.deleteAccount(key);
});

ipcMain.on("saveAccounts", (event, args) => {
    accountManager.saveAccounts();
});

ipcMain.on("hideUnhidePassword", (event, key) => {
    accountManager.hideUnhidePassword(key);
    event.returnValue = accountManager.accountsPasswords[key]
});

ipcMain.on("fetchCharacters", async (event, key) => {
    loadingWindow.show();
    await accountManager.fetchCharacters(key);
    mainWindow.loadURL(accountManager.urls.manageAccountsUrl);
    loadingWindow.hide();
});

// Haapi api key
ipcMain.on("fetchAPIKey", async (event, key) => {
    loadingWindow.show()
    await accountManager.fetchAccountApiKey(key);
    loadingWindow.hide()
    mainWindow.loadURL(accountManager.urls.manageAccountsUrl);
});

// characters ipc handling
ipcMain.on("saveCharacters", (event, args) => {
    accountManager.saveCharacters();
});

ipcMain.on("clearCharacters", (event, args) => {
    accountManager.clearCharacters();
});

ipcMain.on("deleteCharacter", (event, key) => {
    accountManager.deleteCharacter(key);
});

ipcMain.on("goToCharacterProfile", (event, key) => {
    accountManager.selectedCharacterKey = key;
    mainWindow.loadURL(accountManager.urls.characterProfileUrl);
});

ipcMain.on("cancelCharacterProfileEdit", (event, args) => {
    accountManager.selectedCharacterKey = null;
    accountManager.currentView = "characters";
    mainWindow.loadURL(accountManager.urls.manageAccountsUrl);
});

// paths ipc handling
ipcMain.on("createPath", (event, newPath) => {
    loadingWindow.show()
    pathsManager.createPath(newPath);
    mainWindow.loadURL(pathsManager.urls.managePathsUrl);
    loadingWindow.hide()
});

ipcMain.on("savePaths", (event, args) => {
    pathsManager.savePaths();
});

ipcMain.on("deletePath", (event, key) => {
    pathsManager.deletePath(key);
    mainWindow.loadURL(pathsManager.urls.managePathsUrl);
});

ipcMain.on("editPath", (event, key) => {
    pathsManager.currentEditedPath = pathsManager.pathsDB[key];
    mainWindow.loadURL(pathsManager.urls.newPathUrl);
});

ipcMain.on("cancelCreatePath", (event, args) => {
    pathsManager.currentEditedPath = null;
    mainWindow.loadURL(pathsManager.urls.managePathsUrl);
});

// sessions ipc handling
ipcMain.on("runSession", (event, sessionkey) => {
    sessionsManager.runSession(sessionkey);
    mainWindow.loadURL(sessionsManager.urls.manageSessionsUrl);
});

ipcMain.on("stopSession", (event, sessionkey) => {
    sessionsManager.stopSession(sessionkey);
    mainWindow.loadURL(sessionsManager.urls.manageSessionsUrl);

});

ipcMain.on("createSession", (event, newSession) => {
    sessionsManager.createSession(newSession);
    mainWindow.loadURL(sessionsManager.urls.manageSessionsUrl);
});

ipcMain.on("saveSessions", (event, args) => {
    sessionsManager.saveSessions();
});

ipcMain.on("deleteSession", (event, key) => {
    sessionsManager.deleteSession(key);
});

ipcMain.on("editSession", (event, key) => {
    var session = sessionsManager.sessionsDB[key];
    sessionsManager.currentEditedSession = session;
    if (session.type == "farm") 
        mainWindow.loadURL(sessionsManager.urls.farmSessionFormUrl);
    else if (session.type == "fight") 
        mainWindow.loadURL(sessionsManager.urls.fightSessionFormUrl);
});

ipcMain.on("cancelCreateSession", (event, args) => {
    sessionsManager.currentEditedSession = null;
    mainWindow.loadURL(sessionsManager.urls.manageSessionsUrl);
});

ipcMain.on("getData", (event, key) => {
    event.returnValue = ejse.data(key);
});
// This method will be called when Electron has finished
// initialization and is ready to create browser windows.
// Some APIs can only be used after this event occurs.
app.on('ready', createWindow);

// Quit when all windows are closed, except on macOS. There, it's common
// for applications and their menu bar to stay active until the user quits
// explicitly with Cmd + Q.
app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        app.quit();
    }
});

app.on('activate', () => {
    // On OS X it's common to re-create a window in the app when the
    // dock icon is clicked and there are no other windows open.
    if (BrowserWindow.getAllWindows().length === 0) {
        createWindow();
    }
});

// In this file you can include the rest of your app's specific main process
// code. You can also put them in separate files and import them here.

const mainMenuTemplate = [
    {
        label: 'File',
        submenu: [
            {
                label: 'dashboard',
            }
        ]
    }
];