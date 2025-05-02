const { app, BrowserWindow, ipcMain, screen } = require('electron');
const path = require('path');
const http = require('http');
const { spawn } = require('child_process');
const fs = require('fs');
const dotenv = require('dotenv');
const killProcessTree = require('tree-kill');

let mainWindow;
let splash;
let serverProcess;

dotenv.config({ path: path.join(__dirname, '.env') });

const isDev = !app.isPackaged;
const LOCAL_SERVER_URL = 'http://127.0.0.1:5000';

function getSessionFilePath() {
    const documentsDir = app.getPath('documents');
    const sessionDir = path.join(documentsDir, 'Ressync', 'session');
    if (!fs.existsSync(sessionDir)) {
        fs.mkdirSync(sessionDir, { recursive: true });
    }
    return path.join(sessionDir, 'session_token.json');
}

function readSessionToken() {
    try {
        const filePath = getSessionFilePath();
        if (fs.existsSync(filePath)) {
            const data = fs.readFileSync(filePath, 'utf8');
            return JSON.parse(data);
        }
    } catch (error) {
        console.error('Error reading session token:', error);
    }
    return null;
}

function clearSessionToken() {
    try {
        const filePath = getSessionFilePath();
        if (fs.existsSync(filePath)) {
            fs.unlinkSync(filePath);
        }
    } catch (error) {
        console.error('Error clearing session token:', error);
    }
}

function getAssetPath(...paths) {
    return isDev
        ? path.join(__dirname, ...paths)
        : path.join(process.resourcesPath, ...paths);
}

function startLocalServer() {
    const serverDir = isDev 
        ? path.join(__dirname, 'server')
        : path.join(process.resourcesPath, 'server');
    
    const serverExecutable = path.join(serverDir, 'ressync.exe');
    const env = {
        ...process.env,
        ...process.env.FLASK_ENV ? dotenv.parse(fs.readFileSync(path.join(serverDir, '.env'))) : {}
    };

    serverProcess = spawn(serverExecutable, [], {
        stdio: 'ignore',
        cwd: serverDir,
        env: env
    });

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
    let attempts = 0;

    while (!serverReady) {
        serverReady = await isServerRunning();
        if (!serverReady) {
            attempts++;
            console.log(`Waiting for server... (${attempts})`);
            await new Promise(resolve => setTimeout(resolve, 500));
        }
    }
}


async function attemptTokenLogin(token) {
    return new Promise((resolve, reject) => {
        const options = {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        };
        
        const req = http.request(`${LOCAL_SERVER_URL}/auth/token-login`, options, (res) => {
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
        });
        
        req.on('error', reject);
        req.write(JSON.stringify({ token }));
        req.end();
    });
}

async function checkAuthentication() {
    const sessionData = readSessionToken();
    if (sessionData && sessionData.token) {
        try {
            const response = await attemptTokenLogin(sessionData.token);
            if (response.authenticated) {
                return response;
            }
        } catch (error) {
            console.log('Token login failed, falling back to cookie:', error.message);
        }
    }
    
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
            preload: path.join(__dirname, 'preload.js')
        }
    });

    splash.loadFile(getAssetPath('splash.html'));
    splash.on('closed', () => splash = null);
}

async function createMainWindow() {
    try {
        const authStatus = await checkAuthentication();
        const loadURL = authStatus.authenticated
            ? `${LOCAL_SERVER_URL}/user_home/${authStatus.company_id}`
            : `${LOCAL_SERVER_URL}/auth/login`;

        mainWindow = new BrowserWindow({
            width: 1200,
            height: 800,
            minWidth: 800,
            minHeight: 600,
            resizable: true,
            fullscreen: false,
            icon: getAssetPath('logo-desktop-splash.png'),
            webPreferences: {
                nodeIntegration: true,
                contextIsolation: false,
                enableRemoteModule: true
            },
            autoHideMenuBar: true,
            show: false,
            backgroundColor: '#ffffff'
        });

        mainWindow.loadURL(loadURL);
        mainWindow.once('ready-to-show', () => {
            if (splash) splash.destroy();
            mainWindow.show();
            
        });

        mainWindow.on('closed', () => {
            mainWindow = null;
        });

        mainWindow.webContents.on('did-navigate', (event, url) => {
            if (url.includes('/auth/login')) {
                clearSessionToken();
            }
        });

    } catch (error) {
        console.error("Failed to create main window:", error);
        if (splash) splash.destroy();
        
        const errorWindow = new BrowserWindow({ width: 400, height: 300 });
        errorWindow.loadFile(getAssetPath('error.html'));
    }
}

ipcMain.on('close-splash', () => {
    if (splash) splash.close();
});

ipcMain.on('logout', () => {
    clearSessionToken();
    if (mainWindow) {
        mainWindow.loadURL(`${LOCAL_SERVER_URL}/auth/login`);
    }
});

ipcMain.on('store-session-token', (event, tokenData) => {
    try {
        const filePath = getSessionFilePath();
        fs.writeFileSync(filePath, JSON.stringify(tokenData));
    } catch (error) {
        console.error('Error storing session token:', error);
    }
});

app.on('ready', async () => {
    createSplashWindow();

    try {
        startLocalServer();
        await waitForServer();
        await createMainWindow();
    } catch (err) {
        console.error("Error during startup:", err);
        if (splash) splash.destroy();
        app.quit();
    }
});

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') app.quit();
});

app.on('before-quit', () => {
    if (global.localServerPid) {
        killProcessTree(global.localServerPid, 'SIGTERM', (err) => {
            if (err) {
                console.error('Failed to kill local server process:', err);
            } else {
                console.log('Local server process terminated.');
            }
        });
    }
});

app.on('activate', () => {
    if (mainWindow === null) {
        createMainWindow();
    }
});