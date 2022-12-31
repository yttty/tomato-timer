# Delete old version
$FileName = "$env:APPDATA\Tomato"
if (Test-Path $FileName) {
  Remove-Item -Recurse $FileName
}

# Copy to user's APPDATA
Copy-Item -Recurse "Tomato" "$env:APPDATA\"

# Create object
$WshShell = New-Object -comObject WScript.Shell

# Create shortcut in start menu
$Shortcut = $WshShell.CreateShortcut("$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Tomato.lnk")
$Shortcut.TargetPath = "$env:APPDATA\Tomato\tomato-timer.exe"
$Shortcut.Save()

# Create shortcut in startup for auto startup
$Shortcut = $WshShell.CreateShortcut("$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup\Tomato.lnk")
$Shortcut.TargetPath = "$env:APPDATA\Tomato\tomato-timer.exe"
$Shortcut.Save()