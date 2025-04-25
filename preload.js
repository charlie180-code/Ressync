const { ipcRenderer, contextBridge } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
    closeSplash: () => ipcRenderer.send('close-splash')
});
