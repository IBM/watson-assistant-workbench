## Entities
Values of each entity are specified in a separate file with the name corresponding to the entity name
e.g. `first_name.csv`
There is one entity value per row of the file. The Value can be followed by its synonyms separated by semicolumns
**Example:**
```
amy
john;johny;johnny;ian
susanne;susan
```
**Recommendation:** Entities files are typically placed to a separate directory `<app_root>/entities` or directories.

###Patterns
For pattern entities the pattern should be prefixed by ~
**Example:**
```
~email;\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b
~fullUSphone;(\d{3})-(\d{3})-(\d{4})
```

###Naming conventions

**Only english letters, numbers, hyphens and underscores are allowed in entities names.**

You are supposed not to use entities names starting with `sys-` as Conversation tool offers some system entities with this prefix.

_Following are only recommendations, intent name has no impact on the behavior of the conversation._

- The entity name should be lower-cased
- There shouldn't be any domain prefix as entity is usually cross-domain (e.g. color)

**Example:**`first_name`


