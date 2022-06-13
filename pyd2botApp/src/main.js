const { app, BrowserWindow, Menu, ipcMain } = require('electron');
const path = require('path')
const ejse = require('ejs-electron')
ejse.data('nodeModulesUrl', "file://" + path.join(__dirname, '..', 'node_modules'));
ejse.data('sidebarUrl', path.join(__dirname, 'ejs', 'sidebar.ejs'));
ejse.data('cssUrl', "file://" + path.join(__dirname, 'assets', 'css'));
ejse.data('persistenceDir', path.join(__dirname, '..', '..', 'pyd2botDB'))
const mainUrl = "file://" + path.join(__dirname, 'ejs', 'main.ejs')
const charactersDB = require('../../pyd2botDB/charachters.json');
const AccountManager = require("./accounts/AccountManager.js");
console.log(AccountManager);
let mainWindow;
const accountManager = AccountManager.instance;
ejse.data('charachters', charactersDB);
ejse.data('accounts', accountManager.accountsDB);
ejse.data('accountsPasswords', accountManager.accountsPasswords);
// Handle creating/removing shortcuts on Windows when installing/uninstalling.
if (require('electron-squirrel-startup')) {
    // eslint-disable-line global-require
    app.quit();
}

const createWindow = () => {
    // Create the browser window.
    mainWindow = new BrowserWindow({
        webPreferences: {
            nodeIntegration: true,
            contextIsolation: false,
        },
        show: false,
    });

    // and load the index.html of the app.
    mainWindow.loadURL(accountManager.urls.manageCharactersUrl);

    // To maximize the window
    mainWindow.maximize();
    mainWindow.show();

    const mainMenu = Menu.buildFromTemplate(mainMenuTemplate);
    Menu.setApplicationMenu(mainMenu);
    // Open the DevTools.
    mainWindow.webContents.openDevTools();
};


// Accounts manager ipcs mapping
ipcMain.on("newAccount", (event, formData) => {
    accountManager.newAccount(formData);
    mainWindow.loadURL(accountManager.urls.manageAccountsUrl);
});

ipcMain.on("deleteAccount", (event, key) => {
    accountManager.deleteAccount(key);
    mainWindow.loadURL(accountManager.urls.manageAccountsUrl);
});

ipcMain.on("saveAccounts", (event, args) => {
    accountManager.saveAccounts();
});

ipcMain.on("hideUnhidePassword", (event, key) => {
    accountManager.hideUnhidePassword(key);
    mainWindow.loadURL(accountManager.urls.manageAccountsUrl);
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