## Dialog

### Localization

If you want to make your xml dialog language-independent or customize it for various purposes you can use following scripts which allow you to use the same dialog structure for different languages or customers. Use them directly before `dialog_xml2json.py` or `update_all.py` in the pipeline.

##### Encoding
You can replace all language-dependent fields with _replacement codes_ using the script `dialog_text2code`. Following command replaces all values of `<values>` tags and all values of `text` tags which has no `values` subtags in the input file `chitchat.xml` with _replacement codes_ and creates a `chitchat-resource-en.json` file with translations.

```bash
python scripts/dialog_text2code.py "example/en_app/dialogs/chitchat.xml" "chitchat-resource-en.json" -o "chitchat-encoded.xml" -v

```

###### Input

`chitchat.xml` file

```xml
...
	<output>
		<textValues>
			<values>My name is $botName. What is your name?</values>
		</textValues>
	</output>
...
```

###### Output

`chitchat-encoded.xml` file

```xml
...
	<output>
		<textValues>
			<values>%%TXT17</values>
		</textValues>
	</output>
...
```

`chitchat-resource-en.json` file

```json
{
...
	"TXT17": "My name is $botName. What is your name?",
...
}
```

You can set different prefix of _replacement codes_ using the `-p CHITCHAT_` switch and it is also possible to add more tags to be replaced by specifying the `-t` tag. Next command will replace all `text` tags which has no `values` subtags, all `values` tags and all `condition` tags with _replacement codes_ prefixed by "CHITCHAT_".

```bash
python scripts/dialog_text2code.py "example/en_app/dialogs/chitchat.xml" "chitchat-resource-en.json" -o "chitchat-encoded.xml" -p "CHITCHAT_" -t "//text[not(values)]" "//values" "//condition" -v

```

###### Input

`chitchat.xml` file

```xml
...
	<condition>#ALL_ABOUT_ME_WHAT_IS_YOUR_NAME or input.text.contains('name')</condition>
...
```

###### Output

`chitchat-encoded.xml` file

```xml
...
	<condition>%%CHITCHAT_7</condition>
...
```

`chitchat-resource-en.json` file

```json
{
...
	"CHITCHAT_7": "#ALL_ABOUT_ME_WHAT_IS_YOUR_NAME or input.text.contains('name')",
...
}
```

For more information on this script please type

```bash
python scripts/dialog_text2code.py --help
```

##### Decoding
Having `chitchat-encoded.xml` file and `chitchat-resource-cz.json` file with czech translations, you can create czech version of source dialog in the following way:

```bash
python scripts/dialog_code2text.py "chitchat-encoded.xml" "chitchat-resource-cz.json" -o "chitchat-cz.xml" -t "//text[not(values)]" "//values" "//condition" -v
```

###### Input

`chitchat-encoded.xml` file

```xml
...
	<condition>%%CHITCHAT_7</condition>
...
	<output>
		<textValues>
			<values>%%CHITCHAT_17</values>
		</textValues>
	</output>
...
```

`chitchat-resource-cz.json` file

```json
{
...
	"CHITCHAT_7": "#ALL_ABOUT_ME_WHAT_IS_YOUR_NAME or input.text.contains('jméno')",
...
	"CHITCHAT_17": "Jmenuji se $botName. Jak se jmenuješ ty?",
...
}
```

###### Output

`chitchat-cz.xml` file

```xml
...
	<condition>#ALL_ABOUT_ME_WHAT_IS_YOUR_NAME or input.text.contains('jméno')</condition>
...
	<output>
		<textValues>
			<values>Jmenuji se $botName. Jak se jmenuješ ty?</values>
		</textValues>
	</output>
...
```

For more information on this script please type

```bash
python scripts/dialog_code2text.py --help
```
