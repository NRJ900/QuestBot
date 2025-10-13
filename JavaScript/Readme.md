# Discord Quest Bot - JavaScript Functions Explained

# How to use:
- 1.Copy the .js script.
- 2.Open DiscordPTB or Discord.
- 3.Enable developer mode under "Advanced" in settings.
- 4.Press ctr+shift+i.
- 5.Go to console and type allow pasting.
- 6.Paste the code on the console and Accept the quests.

## 🎯 Complete JavaScript Breakdown

---

## 📦 **Main Injection Wrapper**

```javascript
// Quest Bot - Continuous Auto-Completion
const {BrowserWindow} = require('electron');
const {app} = require('electron');
```
**Purpose:** Import Electron modules to interact with Discord's window system
- `BrowserWindow` - Controls Discord windows
- `app` - Electron application lifecycle

---

## 🪟 **Window Creation Listener**

```javascript
app.on('browser-window-created', (event, window) => {
    window.webContents.on('dom-ready', () => {
        setTimeout(() => {
            if (!window.isDestroyed()) {
                injectQuestBot(window);
            }
        }, 3000);
    });
    
    window.webContents.on('did-navigate', () => {
        setTimeout(() => {
            if (!window.isDestroyed()) {
                injectQuestBot(window);
            }
        }, 2000);
    });
    
    window.webContents.on('did-navigate-in-page', () => {
        setTimeout(() => {
            if (!window.isDestroyed()) {
                injectQuestBot(window);
            }
        }, 2000);
    });
});
```

**What it does:**
- Listens for Discord windows being created
- Waits for page to load (`dom-ready`)
- Waits 3 seconds for Discord to fully initialize
- Injects bot when navigating pages (for persistence)

**Why delays?**
- Discord needs time to load its internal modules
- `isDestroyed()` check prevents crashes if window closes

***

## 🚀 **Main Injection Function**

```javascript
function injectQuestBot(window) {
    if (!window || !window.webContents || window.isDestroyed() || window.webContents.isDestroyed()) {
        return;
    }
    
    try {
        const questScript = `
            // All bot code goes here as a string
        `;
        
        window.webContents.executeJavaScript(questScript).catch(() => {});
        
    } catch (err) {}
}
```

**What it does:**
- Safety checks: ensures window exists and isn't destroyed
- Executes JavaScript code in Discord's renderer process
- Catches errors silently to prevent crashes

**Why string template?**
- Code runs in renderer (webpage), not main process
- Must be sent as a string to `executeJavaScript()`

***

## 🔄 **Initialization Loop**

```javascript
(function() {
    console.log('[QUEST BOT] Starting continuous quest automation...');
    
    let initAttempts = 0;
    const maxAttempts = 120;
    let activeQuestId = null;
    
    function tryInit() {
        initAttempts++;
        
        if (initAttempts % 10 === 0) {
            console.log('[QUEST BOT] Waiting for Discord... attempt', initAttempts);
        }
        
        if (!window.webpackChunkdiscord_app) {
            if (initAttempts < maxAttempts) {
                setTimeout(tryInit, 1000);
            }
            return;
        }
        
        console.log('[QUEST BOT] Webpack found!');
        
        // Continue initialization...
    }
    
    tryInit();
})();
```

**What it does:**
- **IIFE (Immediately Invoked Function Expression)** - Runs immediately, keeps variables private
- Tries to find Discord's webpack module (up to 120 times = 2 minutes)
- Logs progress every 10 attempts
- Waits 1 second between attempts

**Why loop?**
- Discord's webpack loads asynchronously
- Need to wait for it before accessing internal modules

***

## 🔌 **Webpack Access**

```javascript
try {
    var w = webpackChunkdiscord_app.push([[Symbol()], {}, r => r]);
    webpackChunkdiscord_app.pop();
    
    var R = Object.values(w.c).find(x => x?.exports?.ZP?.getRunningGames)?.exports?.ZP;
    var Q = Object.values(w.c).find(x => x?.exports?.Z?.__proto__?.getQuest)?.exports?.Z;
    var F = Object.values(w.c).find(x => x?.exports?.Z?.__proto__?.flushWaitQueue)?.exports?.Z;
    var A = Object.values(w.c).find(x => x?.exports?.tn?.get)?.exports?.tn;
    
    if (!R || !Q || !F || !A) {
        setTimeout(tryInit, 2000);
        return;
    }
    
    console.log('[QUEST BOT] All stores loaded!');
    startContinuousQuestBot(R, Q, F, A);
}
```

**What it does:**

### **Step 1: Hijack Webpack**
```javascript
var w = webpackChunkdiscord_app.push([[Symbol()], {}, r => r]);
webpackChunkdiscord_app.pop();
```
- Pushes empty module to webpack
- Gets module resolver function (`r`)
- Pops it back out (cleans up)
- Result: Access to all Discord modules via `w.c`

### **Step 2: Find Stores**
```javascript
var R = Object.values(w.c).find(x => x?.exports?.ZP?.getRunningGames)?.exports?.ZP;
```
- **R** = `RunningGameStore` - Tracks which games are running
- **Q** = `QuestsStore` - Stores quest data
- **F** = `FluxDispatcher` - Event system for state changes
- **A** = `API` - HTTP request handler

**How it finds them:**
- Loops through all webpack modules (`w.c`)
- Looks for specific function signatures
- Uses optional chaining (`?.`) to prevent errors

### **Step 3: Validate**
```javascript
if (!R || !Q || !F || !A) {
    setTimeout(tryInit, 2000);
    return;
}
```
- If any store is missing, wait 2 seconds and retry
- Ensures all required modules are loaded

***

## 🎮 **Continuous Quest Bot**

```javascript
function startContinuousQuestBot(R, Q, F, A) {
    console.log('[QUEST BOT] 🔄 Continuous quest mode enabled');
    
    function checkForQuests() {
        try {
            var q = [...Q.quests.values()].find(x => 
                x.userStatus?.enrolledAt && 
                !x.userStatus?.completedAt &&
                new Date(x.config.expiresAt).getTime() > Date.now()
            );
            
            if (!q) {
                console.log('[QUEST BOT] ⏳ No active quest. Checking in 1 minute...');
                setTimeout(checkForQuests, 60000);
                return;
            }
            
            if (activeQuestId !== q.id) {
                activeQuestId = q.id;
                console.log('[QUEST BOT] ✅ NEW QUEST:', q.config.messages.questName);
                startQuest(q, R, Q, F, A);
            } else {
                setTimeout(checkForQuests, 30000);
            }
            
        } catch (e) {
            setTimeout(checkForQuests, 120000);
        }
    }
    
    checkForQuests();
}
```

**What it does:**

### **Quest Detection**
```javascript
var q = [...Q.quests.values()].find(x => 
    x.userStatus?.enrolledAt &&              // Quest is accepted
    !x.userStatus?.completedAt &&            // Not completed yet
    new Date(x.config.expiresAt) > Date.now() // Not expired
);
```
- Gets all quests from QuestsStore
- Finds first active quest that meets criteria

### **Quest ID Tracking**
```javascript
if (activeQuestId !== q.id) {
    activeQuestId = q.id;
    startQuest(q, R, Q, F, A);
}
```
- Prevents re-starting same quest
- Only runs when new quest detected

### **Retry Logic**
- No quest found: Check again in 60 seconds (1 minute)
- Same quest active: Check again in 30 seconds
- Error occurred: Check again in 120 seconds (2 minutes)

---

## 🎯 **Start Quest Function**

```javascript
function startQuest(q, R, Q, F, A) {
    var p = Math.floor(Math.random() * 30000) + 1000;
    var id = q.config.application.id;
    var taskConfig = q.config.taskConfig ?? q.config.taskConfigV2;
    var taskName = Object.keys(taskConfig.tasks)[0];
    var need = taskConfig.tasks[taskName].target;
    
    if (taskName !== 'PLAY_ON_DESKTOP') {
        activeQuestId = null;
        setTimeout(checkForQuests, 120000);
        return;
    }
```

**What it does:**

### **Generate Random PID**
```javascript
var p = Math.floor(Math.random() * 30000) + 1000;
```
- Creates fake process ID between 1000-31000
- Makes spoofed game look realistic

### **Get Quest Details**
```javascript
var id = q.config.application.id;          // Game application ID
var taskConfig = q.config.taskConfig ?? q.config.taskConfigV2;
var taskName = Object.keys(taskConfig.tasks)[0]; // Usually 'PLAY_ON_DESKTOP'
var need = taskConfig.tasks[taskName].target;    // Required playtime (seconds)
```

### **Task Type Validation**
```javascript
if (taskName !== 'PLAY_ON_DESKTOP') {
    // Only supports desktop play quests
    return;
}
```
- Bot only works for "Play on Desktop" quests
- Other quest types (streaming, etc.) are skipped

***

## 🌐 **Fetch Game Data**

```javascript
A.get({url: '/applications/public?application_ids=' + id}).then(r => {
    var a = r.body[0];
    var e = a.executables.find(x => x.os === 'win32').name.replace('>', '');
```

**What it does:**
- Calls Discord API to get game information
- Extracts Windows executable name
- Needed to create realistic fake game process

**API Response Example:**
```json
{
  "body": [{
    "id": "356869127241072640",
    "name": "VALORANT",
    "executables": [
      {
        "os": "win32",
        "name": "VALORANT-Win64-Shipping.exe"
      }
    ]
  }]
}
```

***

## 🎭 **Create Fake Game Process**

```javascript
var g = {
    cmdLine: 'C:\\\\\\\\Program Files\\\\\\\\' + a.name + '\\\\\\\\' + e,
    exeName: e,
    exePath: 'c:/program files/' + a.name.toLowerCase() + '/' + e,
    hidden: false,
    isLauncher: false,
    id: id,
    name: a.name,
    pid: p,
    pidPath: [p],
    processName: a.name,
    start: Date.now()
};
```

**What it does:**
Creates fake game object that looks like a real running process

**Properties:**
- `cmdLine` - Command line that launched the "game"
- `exeName` - Executable file name
- `exePath` - Full path to executable
- `pid` - Process ID (random number we generated)
- `start` - Timestamp when "game" started
- `name` - Game name (e.g., "VALORANT")

**Why backslashes?**
```javascript
'C:\\\\\\\\Program Files\\\\\\\\'
```
- JavaScript needs `\\` to represent single `\`
- String is inside a string (template), so extra escaping
- Result: `C:\Program Files\`

***

## 🔄 **Override Game Detection**

```javascript
var o1 = R.getRunningGames;
var o2 = R.getGameForPID;

R.getRunningGames = () => [g];
R.getGameForPID = x => x === p ? g : null;
```

**What it does:**

### **Backup Original Functions**
```javascript
var o1 = R.getRunningGames;
var o2 = R.getGameForPID;
```
- Saves original functions so we can restore them later

### **Override getRunningGames**
```javascript
R.getRunningGames = () => [g];
```
- Replaces Discord's game detection
- Always returns array with our fake game
- Discord thinks game is running

### **Override getGameForPID**
```javascript
R.getGameForPID = x => x === p ? g : null;
```
- If Discord checks specific PID, return our fake game
- Otherwise return null (no game)

***

## 📡 **Dispatch Game Running Event**

```javascript
F.dispatch({type: 'RUNNING_GAMES_CHANGE', removed: [], added: [g], games: [g]});

console.log('[QUEST BOT] ✅✅✅ GAME SPOOFED:', a.name, '✅✅✅');
```

**What it does:**
- Sends event to Discord's state management system
- Updates UI to show game is running
- Updates rich presence
- **Triggers quest progress tracking**

**Event Structure:**
```javascript
{
    type: 'RUNNING_GAMES_CHANGE',  // Event type
    removed: [],                    // Games that stopped
    added: [g],                     // Games that started (our fake one)
    games: [g]                      // Currently running games
}
```

***

## 📊 **Progress Monitoring**

```javascript
var progressHandler = function(d) {
    try {
        var pr = Math.floor(d.userStatus.progress.PLAY_ON_DESKTOP.value);
        var percent = Math.round(pr / need * 100);
        var timeLeft = Math.ceil((need - pr) / 60);
        
        console.log('[QUEST BOT] 📊 PROGRESS:', pr + '/' + need, '(' + percent + '%) ~' + timeLeft + ' min');
        
        if (pr >= need) {
            console.log('[QUEST BOT] 🎉🎉🎉 QUEST COMPLETE! 🎉🎉🎉');
            
            R.getRunningGames = o1;
            R.getGameForPID = o2;
            F.dispatch({type: 'RUNNING_GAMES_CHANGE', removed: [g], added: [], games: []});
            F.unsubscribe('QUESTS_SEND_HEARTBEAT_SUCCESS', progressHandler);
            
            activeQuestId = null;
            console.log('[QUEST BOT] 🔄 Checking in 1 minute...');
            setTimeout(checkForQuests, 60000);
        }
    } catch (err) {}
};

F.subscribe('QUESTS_SEND_HEARTBEAT_SUCCESS', progressHandler);
console.log('[QUEST BOT] ✅ Bot active!');
```

**What it does:**

### **Subscribe to Progress Events**
```javascript
F.subscribe('QUESTS_SEND_HEARTBEAT_SUCCESS', progressHandler);
```
- Listens for Discord's quest heartbeat events
- Fires every ~2 minutes when Discord sends progress update
- `progressHandler` function runs each time

### **Calculate Progress**
```javascript
var pr = Math.floor(d.userStatus.progress.PLAY_ON_DESKTOP.value);
var percent = Math.round(pr / need * 100);
var timeLeft = Math.ceil((need - pr) / 60);
```
- `pr` - Current progress in seconds
- `percent` - Percentage complete
- `timeLeft` - Estimated minutes remaining

### **Quest Completion**
```javascript
if (pr >= need) {
    // Restore original functions
    R.getRunningGames = o1;
    R.getGameForPID = o2;
    
    // Tell Discord game stopped
    F.dispatch({
        type: 'RUNNING_GAMES_CHANGE',
        removed: [g],
        added: [],
        games: []
    });
    
    // Stop listening to progress events
    F.unsubscribe('QUESTS_SEND_HEARTBEAT_SUCCESS', progressHandler);
    
    // Reset and look for new quest
    activeQuestId = null;
    setTimeout(checkForQuests, 60000);
}
```

**Cleanup steps:**
1. Restore original game detection functions
2. Dispatch event showing game stopped
3. Unsubscribe from progress events (prevent memory leak)
4. Reset quest tracker
5. Wait 1 minute then check for new quests

***

## 🔥 **Error Handling**

```javascript
}).catch(err => {
    activeQuestId = null;
    setTimeout(checkForQuests, 120000);
});
```

**What it does:**
- If API call fails (network error, etc.)
- Reset quest tracker
- Wait 2 minutes and try again

***

## 📝 **Complete Flow Summary**

```
1. Discord starts
   ↓
2. Window created → inject bot code
   ↓
3. Wait for webpack to load (up to 2 min)
   ↓
4. Access Discord's internal stores
   ↓
5. Start checking for quests (every 60 sec)
   ↓
6. Quest found? → Get game details from API
   ↓
7. Create fake game process object
   ↓
8. Override getRunningGames() function
   ↓
9. Dispatch RUNNING_GAMES_CHANGE event
   ↓
10. Subscribe to quest progress events
   ↓
11. Discord sends heartbeat every ~2 min
   ↓
12. Progress updates logged to console
   ↓
13. Quest complete? → Restore functions, stop fake game
   ↓
14. Wait 1 minute, check for new quest
   ↓
15. Repeat from step 6
```

***

## 🎯 Key Functions Summary

| Function | Purpose |
|----------|---------|
| `tryInit()` | Wait for Discord's webpack to load |
| `startContinuousQuestBot()` | Main loop - checks for quests |
| `checkForQuests()` | Find active quests every minute |
| `startQuest()` | Begin spoofing for a specific quest |
| `progressHandler()` | Monitor and log quest progress |

***

## 🛡️ Safety Features

1. **Maximum attempts** - Won't retry forever if something's wrong
2. **Optional chaining** (`?.`) - Prevents crashes on missing properties
3. **Try-catch blocks** - Catches and handles errors gracefully
4. **Window destroyed checks** - Prevents accessing closed windows
5. **Function restoration** - Always restores original Discord functions

***
