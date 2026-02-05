# Author: shak
# Description: A script to batch convert mod textures to PBR using create_pbr.exe
# Requirements: Python 3.12+, tqdm
# Usage: python3 pbrify.py

# !!! WARNING !!!-------------------------------------------------
# USE AT YOUR OWN RISK
# This software is provided as-is, use at your own risk.
# I is not responsible for any damage caused by this software.
# I am not responsible for damage to your system, data loss, or any other issues that may arise from using this software.
# ----------------------------------------------------------------
# I cannot guarantee the stability or safety of this script.
# Use at your own risk.
# I have tried to put checks to avoid bugs, but I cannot guarantee it will work perfectly.
# There is a posibility that this script could spawn hundreds of create_pbr.exe processes which WILL crash your system.
# You have been warned.
# ----------------------------------------------------------------
# I will not guarantee support for this script.
# This has only been tested on Windows 11 with Python 3.14.
# ----------------------------------------------------------------
# This script will rename files on your disk to sanitize texture suffixes.
# This is not intended to change the texture paths but bugs may occur.
# ----------------------------------------------------------------
# This script can result in very large output sizes depending on the number of mods and textures.
# Make sure you have enough disk space before running this script.
# ----------------------------------------------------------------
# This script has the capability to create directories and write files to the disk.
# ----------------------------------------------------------------

# CREDIT DISCLOSURE-----------------------------------------------
# create_pbr.exe is provided as AI PBR Converter https://www.nexusmods.com/skyrimspecialedition/mods/156542
# I did not create create_pbr.exe nor do I own any rights to it.
# This script is simply a batch processing tool to interface with create_pbr.exe
# ----------------------------------------------------------------

# What does this do?----------------------------------------------
# This script will batch convert mod textures to PBR using create_pbr.exe
# create_pbr.exe is provided as AI PBR Converter https://www.nexusmods.com/skyrimspecialedition/mods/156542
# This does not include create_pbr.exe, nor does it reference any of its code.
# 
# The script will look for mods in the specified mods directory.
# The script is expecting Mod Organizer 2 style mod directories.
# Example: [Mods Directory]/[Mod Name]/textures/
# 
# For each mod, if a textures/ folder is found and there is no textures/pbr/ folder,
# the script will run create_pbr.exe on that mod and output the results to the specified output directory.
# The output will have the same structure as a MO2 mod, allowing for easy installation.
# Example: [Output Directory]/[Mod Name] PBR/
# 
# For more information on the settings and usage, please refer to 

# LICENSE---------------------------------------------------------
# Do whatever you want with it. You may modify it, distribute it, sell it, and do anything legal with it.
# Credit me if you want.
# You are solely responsible for any derivative works you create with this code.
# I will not provide support for derivative works nor will I guarantee support for this.
# This software is provided as-is, use at your own risk.
# I am not responsible for any damage caused by this software.
# ----------------------------------------------------------------

# AI Disclosure---------------------------------------------------
# GPT-5 mini was used to concoct regex patterns and parts of the file name sanitization code.
# Autocompletions by GitHub Copilot were used to speed up writing boilerplate code.
# This is a tool specifically designed to interface with create_pbr.exe, which is a third-party tool that uses AI to convert textures to PBR.
# This script does not use AI itself. It is simply a batch processing tool.
# ----------------------------------------------------------------

# Update log:
# 1.0.0
# - Initial release
#
# 1.1.0
# - Removed vestigial code from debugging
# - Switched to using pathlib for paths for better compatibility and safer path handling