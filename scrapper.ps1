# Function to detect the first available USB Drive
function Get-USBDrive {
    $usb = Get-WmiObject Win32_LogicalDisk | Where-Object { $_.DriveType -eq 2 } | Select-Object -First 1 DeviceID
    if ($usb) { return $usb.DeviceID + "\" }
    else { return $null }
}

# Detect USB Drive
$usbPath = Get-USBDrive

# If no USB found, exit script
if (-not $usbPath) {
    Write-Host "❌ No USB Drive Detected. Insert a USB and try again."
    exit
}

# Define output paths
$outputFile = "$usbPath\SystemData.json"
$backupDir = "$usbPath\BrowserHistory"

# Create directory if not exists
New-Item -ItemType Directory -Path $backupDir -Force | Out-Null

# Initialize hashtable for data
$data = @{}

# Function to retrieve registry data
function Get-RegistryValue {
    param ($path)
    if (Test-Path $path) {
        Get-ItemProperty -Path $path | Select-Object *
    } else {
        return "Not Found"
    }
}

# System Information
$data["SystemInformation"] = @{
    "ComputerName" = $env:COMPUTERNAME
    "OSDetails" = Get-ComputerInfo | Select-Object WindowsProductName, WindowsVersion, OsArchitecture
    "Timezone" = (Get-TimeZone).Id
}

# Recently Used Files
$data["RecentFiles"] = @{
    "RecentDocuments" = Get-ChildItem "$env:APPDATA\Microsoft\Windows\Recent" | Sort-Object LastWriteTime -Descending | Select-Object Name, LastWriteTime
    "EXE" = Get-ChildItem "$env:APPDATA\Microsoft\Windows\Recent" -Filter "*.exe" | Sort-Object LastWriteTime -Descending | Select-Object Name, LastWriteTime
    "Media" = Get-ChildItem "$env:APPDATA\Microsoft\Windows\Recent" -Filter "*.mp3" | Sort-Object LastWriteTime -Descending | Select-Object Name, LastWriteTime
    "Excel" = Get-ChildItem "$env:APPDATA\Microsoft\Windows\Recent" -Filter "*.xlsx" | Sort-Object LastWriteTime -Descending | Select-Object Name, LastWriteTime
    "PowerPoint" = Get-ChildItem "$env:APPDATA\Microsoft\Windows\Recent" -Filter "*.pptx" | Sort-Object LastWriteTime -Descending | Select-Object Name, LastWriteTime
    "Word" = Get-ChildItem "$env:APPDATA\Microsoft\Windows\Recent" -Filter "*.docx" | Sort-Object LastWriteTime -Descending | Select-Object Name, LastWriteTime
    "WinZip" = Get-ChildItem "$env:APPDATA\Microsoft\Windows\Recent" -Filter "*.zip" | Sort-Object LastWriteTime -Descending | Select-Object Name, LastWriteTime
}

# Autorun Software & Services
$data["AutorunSoftware"] = @{
    "StartupPrograms" = Get-RegistryValue "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
    "Services" = Get-Service | Select-Object Name, Status, StartType
}

# Removable Devices (Including Printers & Other Devices)
$data["RemovableDevices"] = Get-PnpDevice | Where-Object { $_.Class -match "USB|Printer|Phone" } | 
    Select-Object FriendlyName, Status, Class

# User/Group Details
$data["UserDetails"] = Get-LocalUser | Select-Object Name, Enabled, LastLogon
$data["GroupDetails"] = Get-LocalGroup | Select-Object Name

# Installed Network Cards
$data["NetworkCards"] = Get-NetAdapter | Select-Object Name, Status, MacAddress

# Installed Software
$data["InstalledSoftware"] = Get-ItemProperty "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\*" | Select-Object DisplayName, DisplayVersion

# Installed Drivers
$data["InstalledDrivers"] = Get-WmiObject Win32_PnPSignedDriver | Select-Object DeviceName, DriverVersion, Manufacturer

# Copy Browser History Databases
$browserDBs = @{
    "Chrome"  = "$env:LOCALAPPDATA\Google\Chrome\User Data\Default\History"
    "Edge"    = "$env:LOCALAPPDATA\Microsoft\Edge\User Data\Default\History"
    "Firefox" = (Get-ChildItem "$env:APPDATA\Mozilla\Firefox\Profiles\*" | Where-Object { $_.PSIsContainer } | Select-Object -First 1 -ExpandProperty FullName) + "\places.sqlite"
}

$data["BrowserHistory"] = @{}

foreach ($browser in $browserDBs.Keys) {
    $src = $browserDBs[$browser]
    if (Test-Path $src) {
        Copy-Item -Path $src -Destination "$backupDir\${browser}History.db" -Force
        $data["BrowserHistory"][$browser] = "$browser history copied to $backupDir\${browser}History.db"
    }
}

# Extract and save Internet Explorer History
$ieHistoryPath = "HKCU:\Software\Microsoft\Internet Explorer\TypedURLs"
$ieHistory = Get-RegistryValue $ieHistoryPath
$data["IE_History"] = if ($ieHistory -ne "Not Found") { $ieHistory.PSObject.Properties | ForEach-Object { $_.Value } } else { "Not Found" }

# Save Data to JSON
$data | ConvertTo-Json -Depth 3 | Out-File -Encoding utf8 $outputFile
Write-Host " All data has been extracted and saved to $outputFile"
