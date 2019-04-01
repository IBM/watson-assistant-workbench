
def main(args)
  name = args["name"] || "World"
  greeting = "Hello #{name}!"
  puts greeting
  { "greeting" => greeting }
end
