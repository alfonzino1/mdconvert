const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('api', {
  // Convert text
  convert: (text, options) => ipcRenderer.invoke('convert', text, options),

  // Clipboard
  copyToClipboard: (text) => ipcRenderer.invoke('copy-to-clipboard', text),

  // History
  getHistory: () => ipcRenderer.invoke('get-history'),
  saveToHistory: (entry) => ipcRenderer.invoke('save-to-history', entry),
  clearHistory: () => ipcRenderer.invoke('clear-history'),

  // Window controls
  minimize: () => ipcRenderer.invoke('window-minimize'),
  maximize: () => ipcRenderer.invoke('window-maximize'),
  close: () => ipcRenderer.invoke('window-close'),

  // Events
  onFocusInput: (callback) => ipcRenderer.on('focus-input', callback),
  onConvertResult: (callback) => ipcRenderer.on('convert-result', (event, result) => callback(result)),
});