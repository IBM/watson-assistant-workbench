# Examples of mapping T2C, XML and JSON #
We provide here some examples to illustrate how WAW T2C, WAW XML and WA JSON map in particular use cases.

## Buttons ##

##### T2C format (column B, we omit %%b if putting it to column C)
**Example:** `%%BHospital=Pacient moved to hospital;Released soon= The patient will be released from hospital soon`

##### XML format

    <output>
      <suggestions structure="listItem">
        <label>Hospital</label>
        <value>Pacient moved to hospital</value>
      </suggestions>
      <suggestions structure="listItem">
        <label>Released soon</label>
        <value>The patient will be released from hospital soon</value>
      </suggestions>
    </output>
      ....
    </output>


##### JSON

    "output": {
      "suggestions": [
        {
            "label": "Hospital"
            "value": "Pacient moved to hospital"
        }, 
        {
            "label": "Released soon",
            "value": "The patient will be released from hospital soon"
        }
    ],
    "text": { ....


## Foldables ##

##### T2C format
**Example:** `%%Fclick on me=long form of text; title= very very long form of the article`

##### XML format

    <output>
      <textValues>
        <values structure="listItem">Example </values>
      </textValues>
      <more structure="listItem">
        <title>click on me</title>
        <body>long form of text</body>
      </more>
      <more structure="listItem">
        <title>title</title>
        <body>very very long form of the article</body>
      </more>
    </output>


##### JSON

    "output": {
        "text": {
            "values": [
                "Example"
            ]
        }, 
        "more": [
            {
                "body": "long form of text", 
                "title": "click on me"
            }, 
            {
                "body": "very very long form of the article", 
                "title": "title"
            }
        ]
    }
