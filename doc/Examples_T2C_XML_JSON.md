#Examples of mapping T2C, XML and JSON#
We provide here some examples to illustrate how WAW T2C, WAW XML and WA JSON map in particular use cases.

## Buttons ##

**T2C format** (column B, we omit %%b if putting it to column C)
	%%bHospital=Pacient moved to hospital;Released soon= The patient will be released from hospital soon

 
**XML format**

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


**JSON**

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
