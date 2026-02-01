(function () {
    console.log('[QUEST BOT] Starting unified quest automation...');

    // --- Environment Spoofing (adapted from video_quest.js) ---
    try {
        Object.defineProperty(document, 'hidden', { get: () => false, configurable: true });
        Object.defineProperty(document, 'visibilityState', { get: () => 'visible', configurable: true });
        const blockEvents = (e) => e.stopImmediatePropagation();
        window.addEventListener('visibilitychange', blockEvents, true);
        document.addEventListener('visibilitychange', blockEvents, true);
        window.addEventListener('blur', blockEvents, true);

        // Prevent video pausing
        const originalPause = HTMLMediaElement.prototype.pause;
        HTMLMediaElement.prototype.pause = function () {
            console.log('[QUEST BOT] Blocked video pause attempt');
            return;
        };
    } catch (e) {

    }

    // --- Webpack & Store Resolution ---
    let wpRequire;
    if (window.webpackChunkdiscord_app) {
        wpRequire = webpackChunkdiscord_app.push([[Symbol()], {}, r => r]);
        webpackChunkdiscord_app.pop();
    } else {
        console.log('[QUEST BOT] Webpack not found. Waiting...');
        return;
    }

    let ApplicationStreamingStore = Object.values(wpRequire.c).find(x => x?.exports?.Z?.__proto__?.getStreamerActiveStreamMetadata)?.exports?.Z;
    let RunningGameStore, QuestsStore, ChannelStore, GuildChannelStore, FluxDispatcher, api;


    if (!ApplicationStreamingStore) {
        ApplicationStreamingStore = Object.values(wpRequire.c).find(x => x?.exports?.A?.__proto__?.getStreamerActiveStreamMetadata)?.exports?.A;
        RunningGameStore = Object.values(wpRequire.c).find(x => x?.exports?.Ay?.getRunningGames)?.exports?.Ay;
        QuestsStore = Object.values(wpRequire.c).find(x => x?.exports?.A?.__proto__?.getQuest)?.exports?.A;
        ChannelStore = Object.values(wpRequire.c).find(x => x?.exports?.A?.__proto__?.getAllThreadsForParent)?.exports?.A;
        GuildChannelStore = Object.values(wpRequire.c).find(x => x?.exports?.Ay?.getSFWDefaultChannel)?.exports?.Ay;
        FluxDispatcher = Object.values(wpRequire.c).find(x => x?.exports?.h?.__proto__?.flushWaitQueue)?.exports?.h;
        api = Object.values(wpRequire.c).find(x => x?.exports?.Bo?.get)?.exports?.Bo;
    } else {
        RunningGameStore = Object.values(wpRequire.c).find(x => x?.exports?.ZP?.getRunningGames)?.exports?.ZP;
        QuestsStore = Object.values(wpRequire.c).find(x => x?.exports?.Z?.__proto__?.getQuest)?.exports?.Z;
        ChannelStore = Object.values(wpRequire.c).find(x => x?.exports?.Z?.__proto__?.getAllThreadsForParent)?.exports?.Z;
        GuildChannelStore = Object.values(wpRequire.c).find(x => x?.exports?.ZP?.getSFWDefaultChannel)?.exports?.ZP;
        FluxDispatcher = Object.values(wpRequire.c).find(x => x?.exports?.Z?.__proto__?.flushWaitQueue)?.exports?.Z;
        api = Object.values(wpRequire.c).find(x => x?.exports?.tn?.get)?.exports?.tn;
    }

    if (!QuestsStore || !FluxDispatcher || !api) {
        console.log('[QUEST BOT] ⚠️ Could not find required stores. Aborting.');
        return;
    }

    const supportedTasks = ["WATCH_VIDEO", "PLAY_ON_DESKTOP", "STREAM_ON_DESKTOP", "PLAY_ACTIVITY", "WATCH_VIDEO_ON_MOBILE"];
    let quests = [...QuestsStore.quests.values()].filter(x =>
        x.userStatus?.enrolledAt &&
        !x.userStatus?.completedAt &&
        new Date(x.config.expiresAt).getTime() > Date.now() &&
        supportedTasks.find(y => Object.keys((x.config.taskConfig ?? x.config.taskConfigV2).tasks || {}).includes(y))
    );

    // Style: [QUEST BOT] Message
    function log(msg) {
        console.log('[QUEST BOT] ' + msg);
    }

    // Progress bar 
    function getProgressString(progress, total) {
        const percent = Math.min(100, Math.floor((progress / total) * 100));
        const timeLeft = Math.ceil((total - progress) / 60);
        return `${progress}/${total} (${percent}%) ~${timeLeft} min left`;
    }

    if (quests.length === 0) {
        log("No active supported quests found.");
        return;
    }

    log(`Found ${quests.length} quest(s)`);
    quests.forEach((q, i) => {
        const task = Object.keys(q.config.taskConfig?.tasks || q.config.taskConfigV2.tasks || {})[0];
        const target = q.config.taskConfig?.tasks?.[task]?.target || 'unknown';
        log(`Quest ${i + 1}: ${q.config.messages.questName} (${task}) - Target: ${target} sec`);
    });

    let doJob = function () {
        const quest = quests.pop();
        if (!quest) {
            log('🎉🎉🎉 ALL QUESTS COMPLETED! 🎉🎉🎉');
            return;
        }

        const pid = Math.floor(Math.random() * 30000) + 1000;
        const applicationId = quest.config.application.id;
        const applicationName = quest.config.application.name;
        const questName = quest.config.messages.questName;
        const taskConfig = quest.config.taskConfig ?? quest.config.taskConfigV2;
        const taskName = supportedTasks.find(x => taskConfig.tasks?.[x] != null);

        if (!taskName) {
            log(`⚠️ No supported task found in quest ${questName}. Skipping...`);
            doJob();
            return;
        }

        let secondsNeeded;
        try {
            secondsNeeded = taskConfig.tasks[taskName]?.target ??
                taskConfig.tasks[taskName]?.durationSeconds ??
                taskConfig.tasks[taskName]?.goal ??
                900;
            if (!secondsNeeded || isNaN(secondsNeeded)) {
                secondsNeeded = 900;
            }
        } catch (e) {
            secondsNeeded = 900;
        }

        let secondsDone = quest.userStatus?.progress?.[taskName]?.value ??
            quest.userStatus?.progress?.[taskName]?.progress ?? 0;

        log(`Starting quest: ${questName}`);
        log(`🎮 Task: ${taskName}`);
        log(`⏱️ Duration needed: ${secondsNeeded} seconds`);

        // --- WATCH VIDEO ---
        if (taskName === "WATCH_VIDEO" || taskName === "WATCH_VIDEO_ON_MOBILE") {
            const maxFuture = 10, speed = 7, interval = 1;
            const enrolledAt = new Date(quest.userStatus.enrolledAt).getTime();
            let completed = false;

            let fn = async () => {
                while (true) {
                    const maxAllowed = Math.floor((Date.now() - enrolledAt) / 1000) + maxFuture;
                    const diff = maxAllowed - secondsDone;
                    const timestamp = secondsDone + speed;

                    if (diff >= speed) {
                        try {
                            const res = await api.post({
                                url: `/quests/${quest.id}/video-progress`,
                                body: { timestamp: Math.min(secondsNeeded, timestamp + Math.random()) }
                            });
                            completed = res.body.completed_at != null;
                            secondsDone = Math.min(secondsNeeded, timestamp);

                            log('📊 PROGRESS: ' + getProgressString(secondsDone, secondsNeeded));
                        } catch (err) {
                            console.error('[QUEST BOT] API Error:', err);
                        }
                    }

                    if (timestamp >= secondsNeeded || completed) {
                        break;
                    }
                    await new Promise(resolve => setTimeout(resolve, interval * 1000));
                }

                if (!completed) {
                    try {
                        await api.post({ url: `/quests/${quest.id}/video-progress`, body: { timestamp: secondsNeeded } });
                    } catch (e) { }
                }

                log('🎉🎉🎉 QUEST COMPLETE! 🎉🎉🎉');
                log('Quest: ' + questName);
                doJob();
            };
            fn();
            log(`Spoofing video interaction for ${questName}...`);

            // --- PLAY ON DESKTOP ---
        } else if (taskName === "PLAY_ON_DESKTOP") {
            const isApp = typeof DiscordNative !== "undefined";
            if (!isApp) {
                log("⚠️ Desktop quests require the native Discord app. Skipping.");
                doJob();
                return;
            }

            api.get({ url: `/applications/public?application_ids=${applicationId}` }).then(res => {
                const appData = res.body[0];
                const exeName = appData.executables.find(x => x.os === "win32")?.name?.replace(">", "") || "game.exe";

                const fakeGame = {
                    cmdLine: `C:\\Program Files\\${appData.name}\\${exeName}`,
                    exeName,
                    exePath: `c:/program files/${appData.name.toLowerCase()}/${exeName}`,
                    hidden: false,
                    isLauncher: false,
                    id: applicationId,
                    name: appData.name,
                    pid: pid,
                    pidPath: [pid],
                    processName: appData.name,
                    start: Date.now(),
                };

                const realGames = RunningGameStore.getRunningGames();
                // Backup
                const realGetRunningGames = RunningGameStore.getRunningGames;
                const realGetGameForPID = RunningGameStore.getGameForPID;

                // Spoof
                RunningGameStore.getRunningGames = () => [fakeGame];
                RunningGameStore.getGameForPID = (pid) => pid === fakeGame.pid ? fakeGame : null;

                FluxDispatcher.dispatch({ type: "RUNNING_GAMES_CHANGE", removed: realGames, added: [fakeGame], games: [fakeGame] });

                log(`✅✅✅ GAME SPOOFED: ${applicationName} ✅✅✅`);

                let fn = data => {
                    try {
                        let progress = quest.config.configVersion === 1
                            ? data.userStatus.streamProgressSeconds
                            : Math.floor(data.userStatus.progress.PLAY_ON_DESKTOP.value || 0);

                        log('📊 PROGRESS: ' + getProgressString(progress, secondsNeeded));

                        if (progress >= secondsNeeded) {
                            log('🎉🎉🎉 QUEST COMPLETE! 🎉🎉🎉');
                            log('Quest: ' + questName);

                            // Restore
                            RunningGameStore.getRunningGames = realGetRunningGames;
                            RunningGameStore.getGameForPID = realGetGameForPID;
                            FluxDispatcher.dispatch({ type: "RUNNING_GAMES_CHANGE", removed: [fakeGame], added: [], games: [] });
                            FluxDispatcher.unsubscribe("QUESTS_SEND_HEARTBEAT_SUCCESS", fn);

                            doJob();
                        }
                    } catch (e) {
                        // Ignore heartbeats that might be malformed or irrelevant
                    }
                };
                FluxDispatcher.subscribe("QUESTS_SEND_HEARTBEAT_SUCCESS", fn);

            }).catch(e => {
                log(`API error for ${questName}: ${e.message}`);
                doJob();
            });

            // --- STREAM ON DESKTOP ---
        } else if (taskName === "STREAM_ON_DESKTOP") {
            const isApp = typeof DiscordNative !== "undefined";
            if (!isApp) {
                log("⚠️ Stream quests require the native Discord app. Skipping.");
                doJob();
                return;
            }

            let realFunc = ApplicationStreamingStore.getStreamerActiveStreamMetadata;
            ApplicationStreamingStore.getStreamerActiveStreamMetadata = () => ({
                id: applicationId,
                pid,
                sourceName: null
            });

            log(`✅ Stream spoofed to ${applicationName}.`);
            log(`ℹ️ You need to be streaming a window in a VC with at least 1 other person.`);

            let fn = data => {
                try {
                    let progress = quest.config.configVersion === 1
                        ? data.userStatus.streamProgressSeconds
                        : Math.floor(data.userStatus.progress.STREAM_ON_DESKTOP.value || 0);

                    log('📊 PROGRESS: ' + getProgressString(progress, secondsNeeded));

                    if (progress >= secondsNeeded) {
                        log('🎉🎉🎉 QUEST COMPLETE! 🎉🎉🎉');
                        log('Quest: ' + questName);

                        ApplicationStreamingStore.getStreamerActiveStreamMetadata = realFunc;
                        FluxDispatcher.unsubscribe("QUESTS_SEND_HEARTBEAT_SUCCESS", fn);

                        doJob();
                    }
                } catch (e) { }
            };
            FluxDispatcher.subscribe("QUESTS_SEND_HEARTBEAT_SUCCESS", fn);

            // --- PLAY ACTIVITY ---
        } else if (taskName === "PLAY_ACTIVITY") {
            const channelId = ChannelStore.getSortedPrivateChannels()[0]?.id ??
                Object.values(GuildChannelStore.getAllGuilds()).find(x => x != null && x.VOCAL.length > 0)?.VOCAL[0]?.channel.id;

            if (!channelId) {
                log("⚠️ Could not find a suitable voice channel/DM for activity heartbeat.");
                doJob();
                return;
            }

            const streamKey = `call:${channelId}:1`;
            log(`Using Stream Key: ${streamKey}`);

            let fn = async () => {
                while (true) {
                    try {
                        const res = await api.post({ url: `/quests/${quest.id}/heartbeat`, body: { stream_key: streamKey, terminal: false } });
                        const progress = res.body.progress.PLAY_ACTIVITY.value || 0;

                        log('📊 PROGRESS: ' + getProgressString(progress, secondsNeeded));

                        await new Promise(resolve => setTimeout(resolve, 20 * 1000));

                        if (progress >= secondsNeeded) {
                            await api.post({ url: `/quests/${quest.id}/heartbeat`, body: { stream_key: streamKey, terminal: true } });
                            break;
                        }
                    } catch (e) {
                        console.error('[QUEST BOT] Heartbeat error:', e);
                        await new Promise(resolve => setTimeout(resolve, 5000));
                    }
                }

                log('🎉🎉🎉 QUEST COMPLETE! 🎉🎉🎉');
                log('Quest: ' + questName);
                doJob();
            };
            fn();
        }
    };

    doJob();
})();
