import os
import psutil
import subprocess
import shutil
import time
import threading

def monitor_discord_and_restore(exe_path, asar_file, asar_backup):
    """Monitor Discord and restore original when closed"""
    print("\n[*] Monitoring Discord process...")
    
    time.sleep(5)
    
    discord_running = True
    while discord_running:
        discord_running = False
        for proc in psutil.process_iter(['name', 'exe']):
            try:
                if proc.info['exe'] and exe_path in proc.info['exe']:
                    discord_running = True
                    break
            except:
                pass
        
        time.sleep(2)
    
    print("\n[*] Discord closed, restoring original...")
    time.sleep(1)
    
    try:
        if os.path.exists(asar_file):
            os.remove(asar_file)
        
        if os.path.exists(asar_backup):
            shutil.copy2(asar_backup, asar_file)
            os.remove(asar_backup)
            print("[+] Original Discord restored!")
        else:
            print("[!] Backup not found")
    except Exception as e:
        print(f"[-] Error restoring: {e}")

def kill_discord():
    killed = 0
    for p in psutil.process_iter(['name']):
        try:
            if 'Discord' in p.info['name']:
                p.kill()
                killed += 1
        except:
            pass
    
    if killed > 0:
        time.sleep(3)
    return killed

def find_discord():
    username = os.getenv('USERNAME')
    base = f"C:\\Users\\{username}\\AppData\\Local\\DiscordPTB"
    
    for root, dirs, files in os.walk(base):
        if 'DiscordPTB.exe' in files:
            return os.path.join(root, 'DiscordPTB.exe'), os.path.join(root, 'resources')
    return None, None

def extract_asar(asar_file, extract_dir):
    return os.system(f'npx asar extract "{asar_file}" "{extract_dir}"') == 0

def pack_asar(source_dir, asar_file):
    return os.system(f'npx asar pack "{source_dir}" "{asar_file}"') == 0

def inject():
    print("="*60)
    print("DiscordPTB Quest Bot - Quest Completion")
    print("="*60)
    
    exe, resources = find_discord()
    if not exe:
        print("[-] DiscordPTB not found!")
        return
    
    print(f"[+] Found DiscordPTB")
    
    asar_file = os.path.join(resources, 'app.asar')
    asar_backup = os.path.join(resources, 'app.asar.backup')
    extract_dir = os.path.join(resources, 'app_extracted')
    
    # If backup exists, restore it first
    if os.path.exists(asar_backup):
        print("\n[!] Found backup from previous session")
        print("[*] Restoring original DiscordPTB...")
        
        killed = kill_discord()
        if killed > 0:
            print(f"[+] Closed {killed} Discord processes")
        
        if os.path.exists(asar_file):
            os.remove(asar_file)
        shutil.copy2(asar_backup, asar_file)
        os.remove(asar_backup)
        
        print("[+] Original restored")
    
    killed = kill_discord()
    if killed > 0:
        print(f"[+] Closed {killed} Discord processes")
    
    print("[*] Creating backup...")
    shutil.copy2(asar_file, asar_backup)
    print("[+] Backup created")
    
    if os.path.exists(extract_dir):
        shutil.rmtree(extract_dir)
    
    print("[*] Extracting asar...")
    if not extract_asar(asar_file, extract_dir):
        print("[-] Extraction failed!")
        return
    
    # Find index.js
    index_file = None
    for root, dirs, files in os.walk(extract_dir):
        if 'index.js' in files:
            potential = os.path.join(root, 'index.js')
            with open(potential, 'r', encoding='utf-8') as f:
                content = f.read()
                if 'require' in content and len(content) > 100:
                    index_file = potential
                    break
    
    if not index_file:
        print("[-] index.js not found!")
        return
    
    print(f"[+] Found index.js")
    
    # CONTINUOUS quest completion injection
    injection_code = r"""

// Quest Bot - Continuous Auto-Completion
const {BrowserWindow} = require('electron');
const {app} = require('electron');

function injectQuestBot(window) {
    if (!window || !window.webContents || window.isDestroyed() || window.webContents.isDestroyed()) {
        return;
    }
    
    try {
        const questScript = `
(function() {
    console.log('[QUEST BOT] Starting continuous quest automation...');
    
    let initAttempts = 0;
    const maxAttempts = 120;
    let activeQuestId = null;
    let checkInterval = null;
    
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
        
        try {
            var w = webpackChunkdiscord_app.push([[Symbol()], {}, r => r]);
            webpackChunkdiscord_app.pop();
            
            var R = Object.values(w.c).find(x => x?.exports?.ZP?.getRunningGames)?.exports?.ZP;
            var Q = Object.values(w.c).find(x => x?.exports?.Z?.__proto__?.getQuest)?.exports?.Z;
            var F = Object.values(w.c).find(x => x?.exports?.Z?.__proto__?.flushWaitQueue)?.exports?.Z;
            var A = Object.values(w.c).find(x => x?.exports?.tn?.get)?.exports?.tn;
            
            if (!R || !Q || !F || !A) {
                if (initAttempts < maxAttempts) {
                    setTimeout(tryInit, 2000);
                }
                return;
            }
            
            console.log('[QUEST BOT] All stores loaded!');
            startContinuousQuestBot(R, Q, F, A);
            
        } catch (e) {
            console.error('[QUEST BOT] Error:', e);
            if (initAttempts < maxAttempts) {
                setTimeout(tryInit, 2000);
            }
        }
    }
    
    function startContinuousQuestBot(R, Q, F, A) {
        console.log('[QUEST BOT] 🔄 Continuous quest mode enabled');
        console.log('[QUEST BOT] Will check for new quests every 1 minute after completion');
        
        function checkForQuests() {
            try {
                var q = [...Q.quests.values()].find(x => 
                    x.userStatus?.enrolledAt && 
                    !x.userStatus?.completedAt &&
                    new Date(x.config.expiresAt).getTime() > Date.now()
                );
                
                if (!q) {
                    console.log('[QUEST BOT] ⏳ No active quest found. Checking again in 1 minute...');
                    setTimeout(checkForQuests, 60000); // 1 minutes
                    return;
                }
                
                // If it's a new quest (different from active one)
                if (activeQuestId !== q.id) {
                    activeQuestId = q.id;
                    console.log('[QUEST BOT] ✅ NEW QUEST FOUND:', q.config.messages.questName);
                    console.log('[QUEST BOT] Quest ID:', q.id);
                    startQuest(q, R, Q, F, A);
                } else {
                    // Same quest still running, check again in 30 seconds
                    setTimeout(checkForQuests, 30000);
                }
                
            } catch (e) {
                console.error('[QUEST BOT] Error checking quests:', e);
                setTimeout(checkForQuests, 120000);
            }
        }
        
        function startQuest(q, R, Q, F, A) {
            var p = Math.floor(Math.random() * 30000) + 1000;
            var id = q.config.application.id;
            var taskConfig = q.config.taskConfig ?? q.config.taskConfigV2;
            var taskName = Object.keys(taskConfig.tasks)[0];
            var need = taskConfig.tasks[taskName].target;
            
            if (taskName !== 'PLAY_ON_DESKTOP') {
                console.log('[QUEST BOT] ⚠️ Quest type', taskName, 'not supported. Checking for next quest in 2 minutes...');
                activeQuestId = null;
                setTimeout(checkForQuests, 120000);
                return;
            }
            
            console.log('[QUEST BOT] 🎮 Task: PLAY_ON_DESKTOP');
            console.log('[QUEST BOT] ⏱️ Duration needed:', need, 'seconds (~' + Math.ceil(need/60) + ' minutes)');
            
            A.get({url: '/applications/public?application_ids=' + id}).then(r => {
                var a = r.body[0];
                var e = a.executables.find(x => x.os === 'win32').name.replace('>', '');
                
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
                
                var o1 = R.getRunningGames;
                var o2 = R.getGameForPID;
                
                R.getRunningGames = () => [g];
                R.getGameForPID = x => x === p ? g : null;
                F.dispatch({type: 'RUNNING_GAMES_CHANGE', removed: [], added: [g], games: [g]});
                
                console.log('[QUEST BOT] ✅✅✅ GAME SPOOFED:', a.name, '✅✅✅');
                
                var progressHandler = function(d) {
                    try {
                        var pr = Math.floor(d.userStatus.progress.PLAY_ON_DESKTOP.value);
                        var percent = Math.round(pr / need * 100);
                        var timeLeft = Math.ceil((need - pr) / 60);
                        
                        console.log('[QUEST BOT] 📊 PROGRESS:', pr + '/' + need, '(' + percent + '%) ~' + timeLeft + ' min left');
                        
                        if (pr >= need) {
                            console.log('[QUEST BOT] 🎉🎉🎉 QUEST COMPLETE! 🎉🎉🎉');
                            console.log('[QUEST BOT] Quest:', q.config.messages.questName);
                            
                            // Clean up
                            R.getRunningGames = o1;
                            R.getGameForPID = o2;
                            F.dispatch({type: 'RUNNING_GAMES_CHANGE', removed: [g], added: [], games: []});
                            F.unsubscribe('QUESTS_SEND_HEARTBEAT_SUCCESS', progressHandler);
                            
                            // Reset active quest and check for new one in 1 minute
                            activeQuestId = null;
                            console.log('[QUEST BOT] 🔄 Checking for new quests in 1 minute...');
                            setTimeout(checkForQuests, 60000); // 1 minute
                        }
                    } catch (err) {
                        console.error('[QUEST BOT] Progress handler error:', err);
                    }
                };
                
                F.subscribe('QUESTS_SEND_HEARTBEAT_SUCCESS', progressHandler);
                console.log('[QUEST BOT] ✅ Bot active! Monitoring progress...');
                
            }).catch(err => {
                console.error('[QUEST BOT] API ERROR:', err);
                activeQuestId = null;
                setTimeout(checkForQuests, 120000);
            });
        }
        
        // Start checking for quests immediately
        checkForQuests();
    }
    
    tryInit();
})();
        `;
        
        window.webContents.executeJavaScript(questScript).catch(() => {});
        
    } catch (err) {
        // Silently catch errors
    }
}

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
"""
    
    with open(index_file, 'a', encoding='utf-8') as f:
        f.write(injection_code)
    
    print("[+] Injected continuous quest bot")
    
    # Repack
    if os.path.exists(asar_file):
        os.remove(asar_file)
    
    print("[*] Repacking asar...")
    if not pack_asar(extract_dir, asar_file):
        print("[-] Packing failed!")
        shutil.copy2(asar_backup, asar_file)
        return
    
    print("[+] Repacked successfully")
    shutil.rmtree(extract_dir)
    
    print("\n[*] Starting DiscordPTB...")
    subprocess.Popen([exe])
    
    # Start monitoring
    monitor_thread = threading.Thread(
        target=monitor_discord_and_restore,
        args=(exe, asar_file, asar_backup),
        daemon=True
    )
    monitor_thread.start()
    
    print("\n" + "="*60)
    print("✅ CONTINUOUS QUEST BOT ACTIVE!")
    print("="*60)
    print("Features:")
    print("  ✓ Completes quests automatically")
    print("  ✓ After each quest, waits 1 minute then checks for new quests")
    print("  ✓ Runs until you re-open Discord")
    print("  ✓ Handles multiple quests in a row")
    print("  ✓ Auto-restores when Discord closes")
    print("  ✓ Safe to use")
    print("  ✓ Runs locally on you PC")
    print("\nHow it works:")
    print("  1. Finds and starts current quest")
    print("  2. Completes quest (~15-20 minutes)")
    print("  3. Waits 1 minutes")
    print("  4. Checks for new quests")
    print("  5. Repeats again")
    print("="*60)
    print("\n[*] Monitoring... (Keep this window open)")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[*] Stopped")

if __name__ == "__main__":
    inject()
