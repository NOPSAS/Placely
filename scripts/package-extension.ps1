# Pakker Placely SketchUp-extensionen til .rbz

$root = Split-Path $PSScriptRoot
$src  = Join-Path $root "sketchup-extension"
$dst  = Join-Path $root "placely.rbz"

if (Test-Path $dst) { Remove-Item $dst }

Add-Type -AssemblyName System.IO.Compression.FileSystem
[System.IO.Compression.ZipFile]::CreateFromDirectory($src, $dst)

Write-Host "Pakket: $dst" -ForegroundColor Green
Write-Host "Installer i SketchUp: Window -> Extension Manager -> Install Extension"
