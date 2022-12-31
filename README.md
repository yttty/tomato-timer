# Yet Another Offline Tomato Timer

💻 A free and **offline** tomato timer for developers, and business experts to quickly create quality projects.

Currently, this app only supports Windows platform.

## How to Install
- Download the latest release from the [release page](https://github.com/yttty/tomato-timer/releases) and unzip
- Right-click on the `install.ps1` and select `Run with PowerShell` ![](/doc/install.png)

## Screenshots
![](/doc/focus.png)
![](/doc/rest.png)

## How to Contribute
1. Install the dependencies
```
pip install -r requirements.txt
```
2. Modify the code
3. Test building an executable package with `pyinstaller`
```
pyinstaller --noconfirm .\tomato-timer.spec
````
4. Generate and zip the package
```
# powershell script
create-release.ps1
```
