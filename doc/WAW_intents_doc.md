## Intents

Each file represents one intent, name of the file is the name of the intent. On each row of this file there is one example sentence. Entities can be tagged with its entity name.
**Example:**
```
Hi
Ciao
Hallo <first_name>Hans</first_name>.
```
**Recommendation:** Intents files are typically placed to a separate directory `<app_root>/intents` or directories.

### Naming conventions
**Only english letters, numbers, hyphens and underscores are allowed in intent and domain names.**

_Following are only recommendations, intent name has no impact on the behavior of the conversation._

- The intent name should be upper-cased
- The part before the first underscore represents the name of the domain. The rest is the intent specification, which can be divided to "subintents" by another underscores.

**Example:**`CHITCHAT_GREETINGS-HELLO` stands for the domain `CHITCHAT` and the intent `GREETINGS-HELLO`
