# Snake Game - Project Structure

## 📁 Complete Directory Structure

```
snake_game/
│
├── .cursor/                           # Cursor IDE configuration
│   ├── commands/                      # Custom Cursor commands
│   │   ├── start-snake-game.bat      # Windows launch script
│   │   ├── start-snake-game.sh       # Unix/Mac launch script
│   │   └── start-snake-game.json     # Command metadata
│   └── README.md                      # Cursor config documentation
│
├── .vscode/                           # VS Code/Cursor workspace settings
│   ├── launch.json                    # Debug/run configurations
│   ├── settings.json                  # Workspace settings
│   └── tasks.json                     # Build tasks configuration
│
├── snake_game_tkinter.py             # ⭐ Main game (Tkinter - Recommended)
├── snake_game.py                      # Alternative (Pygame version)
├── run_game.bat                       # Quick launch batch file
├── requirements.txt                   # Python dependencies (pygame)
├── .cursorrules                       # Cursor AI rules and commands
├── README.md                          # Main project documentation
└── STRUCTURE.md                       # This file
```

## 📝 File Descriptions

### Core Game Files

| File | Description | Dependencies |
|------|-------------|--------------|
| `snake_game.html` | Web version (runs in browser) | None - just a browser! |
| `snake_game_tkinter.py` | Python Tkinter version | None (built-in) |
| `snake_game.py` | Python Pygame version with animations | pygame |
| `run_game.bat` | Windows batch launcher | None |

### Configuration Files

| File | Purpose |
|------|---------|
| `.cursorrules` | Defines Cursor AI behavior and custom commands |
| `.vscode/tasks.json` | Build tasks (Ctrl+Shift+B) |
| `.vscode/launch.json` | Debug configurations (F5) |
| `.vscode/settings.json` | Workspace-specific settings |
| `.cursor/commands/*.json` | Custom command definitions |

### Documentation

| File | Content |
|------|---------|
| `README.md` | User guide and installation instructions |
| `STRUCTURE.md` | This file - project structure overview |
| `.cursor/README.md` | Cursor configuration documentation |

## 🎮 Ways to Run the Game

### 1. Web Version (Easiest!)
Just open `snake_game.html` in any browser - double-click the file!

### 2. Custom Cursor Command
```
/start-snake-game
```
Type this in Cursor AI chat or command palette

### 3. Keyboard Shortcut
```
Ctrl+Shift+B
```
Quick build task shortcut (runs Python version)

### 4. Terminal Command
```bash
python snake_game_tkinter.py
```

### 5. Batch File
```bash
.\run_game.bat
```

### 6. F5 Debug Launch
Press `F5` to run Python version in debug mode

## 🛠️ Technology Stack

### Python Versions
- **Language:** Python 3.7+
- **GUI Framework:** Tkinter (built-in) / Pygame (optional)

### Web Version
- **HTML5 Canvas** for graphics
- **Vanilla JavaScript** for game logic
- **CSS3** for styling
- **Platform:** Any modern web browser (Chrome, Firefox, Safari, Edge)

## 📦 Dependencies

### Web Version (snake_game.html)
- **None!** Just a web browser

### Python Versions
- Python 3.7 or higher
- Tkinter (included with Python)

### Optional
- Pygame 2.5.2+ (for enhanced graphics Python version)

## 🔧 Configuration Hierarchy

```
Project Root
    ↓
.cursorrules (Project-level AI rules)
    ↓
.cursor/commands/ (Custom commands)
    ↓
.vscode/ (IDE configurations)
```

## 🎯 Key Features

- ✅ No dependencies required (Tkinter version)
- ✅ Custom Cursor commands
- ✅ Multiple launch methods
- ✅ Cross-platform compatibility
- ✅ Well-documented structure
- ✅ Development guidelines included

## 📚 For Developers

### Adding New Features
1. Edit `snake_game_tkinter.py` or `snake_game.py`
2. Test using `python snake_game_tkinter.py`
3. Update documentation if needed

### Adding New Commands
1. Create script in `.cursor/commands/`
2. Add metadata JSON file
3. Document in `.cursorrules`

### Customizing AI Behavior
Edit `.cursorrules` to change how Cursor AI assists with this project

---

**Version:** 1.0  
**Last Updated:** October 19, 2025  
**Python Version:** 3.7+ (Tkinter version works with 3.14+)

