const { app, BrowserWindow, Tray, Menu, globalShortcut, clipboard, nativeImage, Notification, ipcMain } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const Store = require('electron-store');

const store = new Store({
  defaults: {
    format: 'claude',
    autoCopy: true,
    showStats: true,
    history: []
  }
});

let mainWindow = null;
let tray = null;
let pythonProcess = null;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1100,
    height: 700,
    minWidth: 800,
    minHeight: 500,
    frame: false,
    titleBarStyle: 'hidden',
    backgroundColor: '#0f172a',
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
    },
  });

  mainWindow.loadFile(path.join(__dirname, 'renderer', 'index.html'));

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

function createTray() {
  const icon = nativeImage.createEmpty();
  tray = new Tray(icon);

  const contextMenu = Menu.buildFromTemplate([
    {
      label: 'Quick Convert',
      click: () => convertClipboard()
    },
    { type: 'separator' },
    {
      label: 'Show Window',
      click: () => {
        if (mainWindow) {
          mainWindow.show();
          mainWindow.focus();
        }
      }
    },
    { type: 'separator' },
    {
      label: 'Quit',
      click: () => app.quit()
    }
  ]);

  tray.setToolTip('Markdown Converter');
  tray.setContextMenu(contextMenu);

  tray.on('click', () => {
    if (mainWindow) {
      mainWindow.isVisible() ? mainWindow.hide() : mainWindow.show();
    }
  });
}

function registerShortcuts() {
  globalShortcut.register('CommandOrControl+Shift+M', () => {
    convertClipboard();
  });

  globalShortcut.register('CommandOrControl+Shift+H', () => {
    if (mainWindow) {
      mainWindow.isVisible() ? mainWindow.hide() : mainWindow.show();
    }
  });

  globalShortcut.register('CommandOrControl+Shift+T', () => {
    if (mainWindow) {
      mainWindow.show();
      mainWindow.webContents.send('focus-input');
    }
  });
}

function convertClipboard() {
  const text = clipboard.readText();
  if (!text || text.length < 3) return;

  const result = convertWithPython(text);

  if (result) {
    clipboard.writeText(result);
    new Notification({
      title: 'Markdown Converter',
      body: `Converted! ${text.length} → ${result.length} chars`,
    }).show();
  }
}

function convertWithPython(text) {
  try {
    const python = spawn('python3', ['-m', 'mdconvert.cli', 'convert', '-t', text, '-f', 'claude']);
    let output = '';

    python.stdout.on('data', (data) => {
      output += data.toString();
    });

    python.stderr.on('data', (data) => {
      console.error(`Python error: ${data}`);
    });

    python.on('close', (code) => {
      if (code === 0) {
        mainWindow?.webContents.send('convert-result', output);
      }
    });

    return output.trim();
  } catch (error) {
    console.error('Python conversion failed:', error);
    return null;
  }
}

// IPC handlers
ipcMain.handle('convert', async (event, text, options) => {
  return new Promise((resolve) => {
    try {
      const args = ['-m', 'mdconvert.cli', 'convert', '-t', text, '-f', options.format || 'claude'];
      if (options.stats) args.push('-s');

      const python = spawn('python3', args);
      let output = '';
      let errorOutput = '';

      python.stdout.on('data', (data) => {
        output += data.toString();
      });

      python.stderr.on('data', (data) => {
        errorOutput += data.toString();
      });

      python.on('close', (code) => {
        if (code === 0) {
          resolve({ success: true, markdown: output.trim() });
        } else {
          resolve({ success: false, error: errorOutput });
        }
      });
    } catch (error) {
      resolve({ success: false, error: error.message });
    }
  });
});

ipcMain.handle('copy-to-clipboard', async (event, text) => {
  clipboard.writeText(text);
  return true;
});

ipcMain.handle('get-history', async () => {
  return store.get('history', []);
});

ipcMain.handle('save-to-history', async (event, entry) => {
  const history = store.get('history', []);
  history.unshift({
    id: Date.now(),
    input: entry.input,
    output: entry.output,
    timestamp: new Date().toISOString(),
    title: entry.input.split('\n')[0].slice(0, 100)
  });
  store.set('history', history.slice(0, 50));
  return true;
});

ipcMain.handle('clear-history', async () => {
  store.set('history', []);
  return true;
});

ipcMain.handle('window-minimize', () => {
  mainWindow?.minimize();
});

ipcMain.handle('window-maximize', () => {
  if (mainWindow?.isMaximized()) {
    mainWindow.unmaximize();
  } else {
    mainWindow?.maximize();
  }
});

ipcMain.handle('window-close', () => {
  mainWindow?.close();
});

app.whenReady().then(() => {
  createWindow();
  createTray();
  registerShortcuts();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('will-quit', () => {
  globalShortcut.unregisterAll();
});