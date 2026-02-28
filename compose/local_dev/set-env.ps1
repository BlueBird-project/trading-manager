# $env_path = $args[1]
$env_profile = $args[0]
$env_path = ".env"
if (  "default" -eq $env_profile ) {
    # $env_profile = ""
    $env_path = ".\compose\config\.env"
}
elseif ( "" -eq $env_profile -OR $null -eq $env_profile  ) {
    # $env_profile = ""
    $env_path = ".env"
}
else {
    $env_path = ".\compose\config\.env.${env_profile}"
}
if ( "" -eq $env_path  -OR $null -eq $env_path ) {
    # $env_profile = ""
    $env_path = "compose/config/"
}

Get-Content "$env_path" | foreach  {
    $name, $value = $_.split('=',2)
    # echo $name
    # echo $value
    if ([string]::IsNullOrWhiteSpace($name) -OR $name.Contains('#')) {

    }
    else {

        Set-Content env:\$name $value}
}
# Get-ChildItem env: