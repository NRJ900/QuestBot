***

# QuestBotPTB

**QuestBotPTB** is a powerful automation tool for Discord desktop applications. It streamlines operations like extracting and repacking Discord’s `app.asar` file, helping users manage themes and automate custom Discord actions, all through a modern graphical interface.

***

## ⚡ Features

- Intuitive GUI (Tkinter-based)
- One-click extraction/repacking of Discord’s `app.asar`
- Automated process management (using psutil)
- Node.js + asar integration for backend file manipulation
- Complete Windows installer with automatic dependency setup

***

## 🚨 Disclaimer

> **WARNING:**  
> This software is provided for educational purposes only. Automating or modifying Discord may violate Discord’s Terms of Service and could lead to suspension or banning of accounts.  
> Modifying `app.asar` can damage your Discord installation or cause instability.  
> Use at your own risk. The author(s) claim no liability for any outcome.

***

## 🖥️ System Requirements

- Windows 10/11, 64-bit
- Node.js x64 (auto-installed by setup)
- Python 3.8+ (required to run from source)
- `asar` npm package (setup will install automatically)

***

## 📦 Installation

**Installer Method (recommended):**
1. Download `QuestBotPTB_Setup_x64.exe`for DiscordPTB or `QuestBot_Setup_x64.exe` from the [Releases](https://github.com/NRJ900/QuestBot/releases) page.
2. Run the installer.  
   - Node.js will be installed automatically if needed.
   - The `asar` npm package is installed for you.
   - Desktop and Start Menu shortcuts are created.
3. Launch QuestBotPTB from the shortcut provided.

**Manual Method (for development):**
1. Clone this repository:
    ```bash
    git clone https://github.com/NRJ900/QuestBot.git
    cd QuestBot
    ```
2. Install required Python packages:
    ```bash
    pip install -r requirements.txt
    ```
3. Install Node.js x64 from [nodejs.org](https://nodejs.org/)
4. Install asar globally:
    ```bash
    npm install -g asar
    ```
5. Run QuestBotPTB:
    ```bash
    python your_script_name.py
    ```

***

## 🚀 Usage

1. Launch the app via shortcut or by running `questbotPTB.exe` or `questbot.exe`.
2. Selects your Discord installation (auto-detected).
3. Use the GUI buttons to extract or repack `app.asar`.
4. View status and logs for actions performed.
5. Restart Discord if needed.

***

## 📝 How It Works

- Uses Python’s `subprocess` to call `npx asar` for Discord file operations
- `psutil` ensures Discord processes are safely managed
- All dependencies and requirements are bundled in the setup

***

## 🛠️ Development

- All source code is in this repo.
- Use virtual environments for Python development.
- Modify GUI, logic, or add new automation actions as required.

***

## 🧾 License

Licensed under the [MIT License](LICENSE).

***

## 🤝 Contributions & Issues

- Pull requests, bug reports, and feature suggestions welcome!
- Please open an issue via GitHub for feedback.

***

## 📣 Credits

- Developed by NRJ900
- Open to contributions from the Discord automation community

***

**Automate Discord with ease and style — QuestBotPTB!**

***

You can copy and paste this into your README.md file. It covers features, installation, system requirements, disclaimer, usage instructions, license, and credits—giving your repo a clear, professional landing page for users and collaborators.

[1](https://github.com/NRJ900/QuestBot/edit/main/README.md)
