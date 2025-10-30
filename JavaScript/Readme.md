# Discord Quest Bot - JavaScript Functions Explained

# How to use:
- 1.Copy the .js script.
- 2.Open DiscordPTB or Discord.
- 3.Enable developer mode under "Advanced" in settings.
- 4.Press ctr+shift+i.
- 5.Go to console and type allow pasting.
- 6.Paste the code on the console and Accept the quests.


---

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


## 🛡️ Safety Features

1. **Maximum attempts** - Won't retry forever if something's wrong
2. **Optional chaining** (`?.`) - Prevents crashes on missing properties
3. **Try-catch blocks** - Catches and handles errors gracefully
4. **Window destroyed checks** - Prevents accessing closed windows
5. **Function restoration** - Always restores original Discord functions
6. **Video Quest** - Allows user to switch to other tabs without discord detecting out of focus

***
