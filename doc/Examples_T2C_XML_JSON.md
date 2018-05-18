#Examples of mapping T2C, XML and JSON#
We provide here some examples to illustrate how WAW T2C, WAW XML and WA JSON map in particular use cases.

## Buttons ##

**T2C format** (column B, we omit %%b if putting it to column C)

    %%bHospital=moved to hospital;released soon= the patient will be released from hospital soon
 
**XML format**

    <output>
      <generic structure="listItem">
        <response_type>option</response_type>
        <preference>button</preference>
        <title>Fast selection buttons</title>
        <options>
          <label>Hospital</label>
          <value>
            <input>
              <text>moved to hospital</text>
            </input>
          </value>
        </options>
        <options>
          <label>released soon</label>
          <value>
            <input>
              <text>the patient will be released from hospital soon</text>
            </input>
          </value>
        </options>
      </generic>
      ....
    </output>


**JSON**

    "output": {
        "generic": [
            {
                "title": "Fast selection buttons", 
                "response_type": "option", 
                "preference": "button", 
                "options": [
                    {
                        "value": {
                            "input": {
                                "text": "moved to hospital"
                            }
                        }, 
                        "label": "hospital"
                    }, 
                    {
                        "value": {
                            "input": {
                                "text": "the patient will be released from hospital soon"
                            }
                        }, 
                        "label": "released soon"
                    }
                ]
            }
        ], 
        "text": { ....
