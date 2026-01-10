## Disabling Auto-Start

### Method 1: Using Setup Script
```bash
python setup_autostart.py
# Choose option 4: Disable auto-start
```

### Method 2: Windows Settings
1. `Win+R` → `shell:startup`
2. Delete "PRISM.lnk" if present

### Method 3: Registry Editor
1. `Win+R` → `regedit`
2. Navigate to `HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run`
3. Delete "PRISM" entry

### Method 4: Task Manager
1. `Ctrl+Shift+Esc` → Startup tab
2. Find "PRISM" → Disable

## Firewall Configuration

P.R.I.S.M connects to:
- `api.openai.com` (ChatGPT API)
- `api.cerebras.ai` (Cerebras LLM)
- `api.cohere.ai` (Cohere API)
- `google.serper.dev` (Search API)
- `api-inference.huggingface.co` (Image generation)

Allow outbound HTTPS (port 443) to these domains.

## Uninstallation

To completely remove P.R.I.S.M:

1. Disable auto-start (see above)
2. Delete project folder
3. Remove registry entry: `python setup_autostart.py` → option 4
4. (Optional) Revoke API keys on provider dashboards

## Reporting Security Issues

If you discover a security vulnerability:
1. Do NOT post publicly
2. Email: your-security-email@example.com
3. Include detailed description and reproduction steps
4. We'll respond within 48 hours

## Audit Trail

To monitor P.R.I.S.M activity:
- Check `Data/ChatLog.json` for conversation history
- Monitor `Screenshots/` folder for any captured screenshots
- Check `Images/` folder for generated images
- Review console output in `prism.log` (if logging enabled)

## Privacy Mode

Add this to `.env` for enhanced privacy:
```
PRIVACY_MODE=1
SAVE_CHAT_HISTORY=0
DISABLE_SCREENSHOTS=1
```

Then update `Chatbot.py`:
```python
import os
PRIVACY_MODE = os.getenv('PRIVACY_MODE') == '1'
SAVE_HISTORY = os.getenv('SAVE_CHAT_HISTORY', '1') == '1'

if not SAVE_HISTORY:
    # Don't save to ChatLog.json
    pass
```

## Security Updates

- Check for updates regularly: `git pull origin main`
- Review CHANGELOG.md for security patches
- Subscribe to repository notifications
- Enable Dependabot alerts (GitHub)

---

**Last Updated:** January 2026  
**Version:** 1.0.0