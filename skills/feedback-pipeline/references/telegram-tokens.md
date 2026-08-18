# Telegram Bot Tokens

**Do not commit full bot tokens into git or paste them into issues/chats.**
Read live values from the agent environment / secret store. This file is a **routing map**.

| Profile | Bot Name | How to resolve token |
|---|---|---|
| default | Jett | Shell / Hermes secrets for default profile (feedback default) |
| writing | Orion | writing profile secrets |
| trading | Raven | trading profile secrets |

## Chat IDs

| ID | Name | Type |
|---|---|---|
| `8706254081` | Liz | DM |
| `-5272906740` | 生产：Liz肯定能成的 | Group |
| `-5273930457` | 写作：大作家修炼营 | Group |
| `-5294945057` | Daily：Liz 在认真生活孜孜以求 | Group |
| `-5269769084` | 投资：金融世界没人比钱快 | Group |
| `-5544201640` | GitHub（反馈群） | Group |

## API Quick Reference

```
# Send message to group
POST https://api.telegram.org/bot{TOKEN}/sendMessage
Body: {"chat_id": "-5544201640", "text": "Hello", "disable_web_page_preview": true}

# Get updates (recent messages)
GET https://api.telegram.org/bot{TOKEN}/getUpdates?limit=10

# Resolve new invite: add bot to group, then check getUpdates for chat ID
```

## Feedback Pipeline Defaults

| Key | Default |
|---|---|
| `TELEGRAM_BOT_TOKEN` | **Jett** (default profile) — load from env/secrets, never hardcode in app |
| `TELEGRAM_CHAT_ID` | `-5544201640` (GitHub 反馈群) |
| `GITHUB_REPO` | **Per project** (`owner/repo`) — never hardcode in skill |
| `GITHUB_TOKEN` | PAT with Issues write — Liz GitHub account / project secret |

Override `TELEGRAM_CHAT_ID` only when the project should notify a different group.
