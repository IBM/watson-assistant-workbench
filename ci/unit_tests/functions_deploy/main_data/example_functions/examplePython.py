
def main(args):
    name = args.get("name", "World")
    greeting = "Hello " + name + "!"
    print(greeting)
    return {"greeting": greeting}
