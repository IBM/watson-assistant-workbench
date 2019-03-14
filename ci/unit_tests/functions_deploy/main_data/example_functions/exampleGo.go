
package main

// Main is the function implementing the action
func Main(params map[string]interface{}) map[string]interface{} {
    // parse the input JSON
    name, ok := params["name"].(string)
    if !ok {
        name = "World"
    }
    msg := make(map[string]interface{})
    msg["greeting"] = "Hello " + name + "!"
    // return the output JSON
    return msg
}
