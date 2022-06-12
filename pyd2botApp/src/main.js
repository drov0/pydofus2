const { app, BrowserWindow, Menu, ipcMain } = require('electron');
const path = require('path');
const ejse = require('ejs-electron')
const charactersDB = require('../../pyd2botDB/charachters.json');
const accountsDB = require('../../pyd2botDB/accounts.json');
ejse.data('botsCreds', charactersDB);
ejse.data('accounts', accountsDB);
let mainWindow;

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
    mainWindow.loadURL("file://" + __dirname + '/main.ejs');

    // To maximize the window
    mainWindow.maximize();
    mainWindow.show();

    const mainMenu = Menu.buildFromTemplate(mainMenuTemplate);
    Menu.setApplicationMenu(mainMenu);
    // Open the DevTools.
    mainWindow.webContents.openDevTools();
};


// ipcMain.on("switchToBotManagerView", (event, arg) => {
//     mainWindow.loadURL("file://" + __dirname + "/botManager.ejs");
// });

ipcMain.on("newAccount", (event, formData) => {
    console.log(formData);
    accountsDB[formData.entryId] = {
        "login": formData.login,
        "password": formData.password,
    }
    mainWindow.loadURL("file://" + __dirname + "/accountManager.ejs");
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