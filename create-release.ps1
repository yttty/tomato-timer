pyinstaller --noconfirm .\tomato-timer.spec
Copy-Item scripts\install.ps1 .\dist\
Compress-Archive -Path .\dist\* -DestinationPath release\tomato-timer-release-v0.1.1.zip -Force
