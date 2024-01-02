@echo off
echo 正在尝试停用 Windows Defender
PowerShell -Command "& {Set-ItemProperty -Path 'HKLM:\SOFTWARE\Policies\Microsoft\Windows Defender' -Name 'DisableAntiSpyware' -Value 1}"
echo 完成