const { app, BrowserWindow, ipcMain, dialog } = require('electron');
const { autoUpdater } = require('electron-updater');
const path = require('path');
const http = require('http');
const { spawn } = require('child_process');

let mainWindow;
let splash;
let serverProcess;
const LOCAL_SERVER_URL = ' http://127.0.0.1:5000';

function startLocalServer() {
    const serverPath = path.join(__dirname, 'server', 'sails.exe');
    serverProcess = spawn(serverPath, [], { detached: true, stdio: 'ignore' });
    serverProcess.unref();
    console.log('Local server started.');
}

function isServerRunning() {
    return new Promise((resolve) => {
        http.get(`${LOCAL_SERVER_URL}`, (res) => {
            resolve(res.statusCode === 200);
        }).on('error', () => resolve(false));
    });
}

async function waitForServer() {
    let serverReady = false;
    while (!serverReady) {
        serverReady = await isServerRunning();
        if (!serverReady) {
            await new Promise(resolve => setTimeout(resolve, 500));
        }
    }
}

function createSplashWindow() {
    splash = new BrowserWindow({
        width: 800,
        height: 600,
        transparent: true,
        center: true,
        autoHideMenuBar: true,
        webPreferences: {
            preload: path.join(__dirname, 'preload.js'),
            devTools: false
        }
    });

    splash.loadFile(path.join(__dirname, './splash.html'));
    splash.on('closed', () => splash = null);
}

ipcMain.on('close-splash', () => {
    if (splash) {
        splash.close();
    }
});

async function checkAuthentication() {
    return new Promise((resolve, reject) => {
        http.get(`${LOCAL_SERVER_URL}/auth/status`, (res) => {
            let data = '';

            res.on('data', chunk => {
                data += chunk;
            });

            res.on('end', () => {
                try {
                    const response = JSON.parse(data);
                    resolve(response);
                } catch (error) {
                    reject(error);
                }
            });
        }).on('error', (err) => reject(err));
    });
}

async function createMainWindow() {
    try {
        const authStatus = await checkAuthentication();
        let loadURL = authStatus.authenticated
            ? `${LOCAL_SERVER_URL}/user_home/${authStatus.company_id}`
            : `${LOCAL_SERVER_URL}/auth/login`;

        mainWindow = new BrowserWindow({
            width: 800,
            height: 600,
            icon: path.join(__dirname, './logo-desktop-splash.svg'),
            webPreferences: {
                nodeIntegration: true,
            },
            autoHideMenuBar: true,
            show: false,
        });

        mainWindow.loadURL(loadURL);
        mainWindow.once('ready-to-show', () => {
            if (splash) splash.destroy();
            mainWindow.show();
        });

        mainWindow.on('closed', () => mainWindow = null);
    } catch (error) {
        console.error("Failed to determine authentication status:", error);
    }
}

app.on('ready', async () => {
    createSplashWindow();

    try {
        startLocalServer();
        await waitForServer();
        await createMainWindow();
    } catch (err) {
        console.error("Error waiting for Flask server:", err);
    }
});

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        app.quit();
    }
});

app.on('quit', () => {
    if (serverProcess) {
        serverProcess.kill();
    }
});

app.on('activate', () => {
    if (mainWindow === null) {
        createSplashWindow();
        createMainWindow();
    }
});
