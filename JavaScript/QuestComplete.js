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
                
            }).catch(err => {
                activeQuestId = null;
                setTimeout(checkForQuests, 120000);
            });
        }
        
        checkForQuests();
    }
    
    tryInit();
})();
        `;
        
        window.webContents.executeJavaScript(questScript).catch(() => {});
        
    } catch (err) {}
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
