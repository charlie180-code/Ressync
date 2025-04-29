const { app, BrowserWindow, ipcMain, dialog, screen } = require('electron');
const { autoUpdater } = require('electron-updater');
const path = require('path');
const http = require('http');
const { spawn } = require('child_process');

let mainWindow;
let splash;
let serverProcess;

const isDev = !app.isPackaged;
const LOCAL_SERVER_URL = 'http://127.0.0.1:5000';

function getAssetPath(...paths) {
    return isDev
        ? path.join(__dirname, ...paths)
        : path.join(process.resourcesPath, ...paths);
}

function startLocalServer() {
    const serverExecutable = isDev
        ? path.join(__dirname, 'server', 'ressync.exe')
        : path.join(process.resourcesPath, 'server', 'ressync.exe');

    serverProcess = spawn(serverExecutable, [], { detached: true, stdio: 'ignore' });
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
    const { width, height } = screen.getPrimaryDisplay().bounds;

    splash = new BrowserWindow({
        width,
        height,
        frame: false,
        transparent: true,
        fullscreen: true,
        autoHideMenuBar: true,
        webPreferences: {
            preload: path.join(__dirname, 'preload.js'),
            devTools: false
        }
    });

    splash.loadFile(getAssetPath('splash.html'));
    splash.on('closed', () => splash = null);
}

ipcMain.on('close-splash', () => {
    if (splash) splash.close();
});

async function checkAuthentication() {
    return new Promise((resolve, reject) => {
        http.get(`${LOCAL_SERVER_URL}/auth/status`, (res) => {
            let data = '';

            res.on('data', chunk => data += chunk);
            res.on('end', () => {
                try {
                    const response = JSON.parse(data);
                    resolve(response);
                } catch (error) {
                    reject(error);
                }
            });
        }).on('error', reject);
    });
}

async function createMainWindow() {
    try {
        const authStatus = await checkAuthentication();
        const loadURL = authStatus.authenticated
            ? `${LOCAL_SERVER_URL}/user_home/${authStatus.company_id}`
            : `${LOCAL_SERVER_URL}/auth/login`;

        const { width, height } = screen.getPrimaryDisplay().bounds;

        mainWindow = new BrowserWindow({
            width: 1200,
            height: 800,
            resizable: true,
            fullscreen: false,
            icon: getAssetPath('logo-desktop-splash.png'),
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
    if (process.platform !== 'darwin') app.quit();
});

app.on('before-quit', () => {
    if (serverProcess && !serverProcess.killed) {
        try {
            process.kill(serverProcess.pid, 'SIGTERM');
            console.log('Local server stopped.');
        } catch (err) {
            console.error('Error killing server process:', err);
        }
    }
});


app.on('activate', () => {
    if (mainWindow === null) {
        createSplashWindow();
        createMainWindow();
    }
});
