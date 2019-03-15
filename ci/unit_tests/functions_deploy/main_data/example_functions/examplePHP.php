
<?php
function main(array $args) : array
{
    $name = $args["name"] ?? "World";
    $greeting = "Hello $name!";
    echo $greeting;
    return ["greeting" => $greeting];
}
