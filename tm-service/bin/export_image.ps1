$prevPwd = $PWD; Set-Location -ErrorAction Stop -LiteralPath $PSScriptRoot
Set-Location ..
try
{
    $env_path = $args[0]
    #     if is empty
    #     $env_path = ./src/resources/.env
    #### LOAD ENV ######
    Get-Content "$env_path" | foreach  {
        $name, $value = $_.split('=', 2)
        if (!([string]::IsNullOrWhiteSpace($name) -OR $name.Contains('#')))
        {
            set-Content env:\$name $value
        }
        #        else { }
    }
    #    Get-ChildItem env:
    $image_name = "${env:REGISTRY_DOMAIN}/${env:REGISTRY_PROJECT}/${env:REGISTRY_APPLICATION}"
    echo "building: ${image_name}:${env:IMAGE_TAG}"
    $image_id = docker image ls "${image_name}:latest" --format "{{.ID}}"
    if ($image_id)
    {
        #remove 'latest'
        docker image rm -f $image_id
    }
    docker-compose -f .\compose\local.yaml --env-file $env_path build --no-cache tm-service
    docker save -o "d:/tmp/${env:REGISTRY_PROJECT}.${env:REGISTRY_APPLICATION}_${env:IMAGE_TAG}.tar" "${image_name}:latest"  "${image_name}:${env:IMAGE_TAG}"

}
finally
{
    $prevPwd | Set-Location
}
