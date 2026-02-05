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


import sys

def ask_to_exit():
    input('Press Enter to exit.')
    sys.exit()

# check for python 3.12+
if not sys.version_info >= (3, 12):
    print('This script requires Python 3.12 or higher.')
    ask_to_exit()

import os
import subprocess
import re
from pathlib import Path
import tkinter as tk
from tkinter import filedialog
from tqdm import tqdm

# the path to the config file
config_file_path = Path(Path.cwd() / 'config.txt')
pbrify_log_path = Path(Path.cwd() / 'pbrify_log.txt')

# the model to use for the conversion
allowed_checkpoints = ['s4', 's4_alt']
default_checkpoint = 's4'
# the texture format to output
allowed_texture_formats = ['dds', 'png']
default_texture_format = 'dds'
# the tile size
allowed_tile_sizes = ['1024', '2048']
default_max_tile_size = '1024'

# populate empty settings
settings = {
    'mods_directory': None,
    'output_directory': None,
    'create_pbr_path': None,
    'checkpoint': default_checkpoint,
    'texture_format': default_texture_format,
    'max_tile_size': default_max_tile_size
}

# checks if the provided path is a valid path to a file
def is_valid_file(path: Path) -> bool:
    return path is not None and path.exists() and path.is_file()

# checks if the provided path is a valid path to a directory
def is_valid_directory(path: Path) -> bool:
    return path is not None and path.exists() and path.is_dir()

# read the config file if it exists
if config_file_path.exists():
    with open(config_file_path, 'r') as config_file:
        lines = config_file.readlines()
        lines = [line.strip() for line in lines if '=' in line]
        line = {key.strip(): value.strip() for key, value in (l.split('=', 1) for l in lines)}

        # validate config values
        if ('mods_directory' in line):
            config_mods_directory = Path(line['mods_directory'])
            if is_valid_directory(config_mods_directory):
                settings['mods_directory'] = config_mods_directory
        
        if ('output_directory' in line):
            config_output_directory = Path(line['output_directory'])
            if is_valid_directory(config_output_directory):
                settings['output_directory'] = config_output_directory
        
        if ('create_pbr_path' in line):
            config_create_pbr_path = Path(line['create_pbr_path'])
            if is_valid_file(config_create_pbr_path) and config_create_pbr_path.name.lower() == 'create_pbr.exe':
                settings['create_pbr_path'] = config_create_pbr_path
        
        if ('checkpoint' in line) and (line['checkpoint'] in allowed_checkpoints):
            settings['checkpoint'] = line['checkpoint']
        
        if ('texture_format' in line) and (line['texture_format'] in allowed_texture_formats):
            settings['texture_format'] = line['texture_format']
        
        if ('max_tile_size' in line) and (line['max_tile_size'] in allowed_tile_sizes):
            settings['max_tile_size'] = line['max_tile_size']

# use tkinter to open a file dialog to select the mods directory
root = tk.Tk()
root.withdraw()  # hide the main window

# asks the user to select a directory until they select a valid directory or cancel
# prompt: the prompt to display in the console
# title: the title of the dialog
# initialdir: the directory to start the dialog in
# returns the selected directory as a Path or exits the program if cancelled
def ask_directory(prompt: str, title: str, initialdir: Path | None = Path.cwd()) -> Path:
    chosen = None
    while (chosen is None) or (not is_valid_directory(chosen)):
        print(prompt)
        response = filedialog.askdirectory(title=title, initialdir=initialdir)
        # check if the user cancelled the dialog (or something went wrong and we got None for safety)
        if (response is None) or (len(response) == 0):
            root.destroy()
            ask_to_exit()
        
        chosen = Path(response)
        # check if the user selected a valid directory
        if not is_valid_directory(chosen):
            print(f'The specified directory does not exist: {chosen}')
    return chosen

# asks the user to select a file until they select a valid file or cancel
# prompt: the prompt to display in the console
# title: the title of the dialog
# initialdir: the directory to start the dialog in
# filetypes: the tkinter-style filetypes filter to use e.g. [('DDS Files', '*.dds'), ('PNG Files', '*.png')]
# allowed_filenames: a list of allowed filenames including extension. if empty, any filename is allowed. all whitelisted names must be lowercase.
# returns the selected file as a Path or exits the program if cancelled
def ask_file(prompt: str, title: str, initialdir: Path | None = Path.cwd(), filetypes: list = [('Any File', '*')], allowed_filenames: list[str] = []) -> Path:
    chosen = None
    while (chosen is None) or (not is_valid_file(chosen)) or (len(allowed_filenames) > 0 and chosen.name.lower() not in allowed_filenames):
        print(prompt)
        response = filedialog.askopenfilename(title=title, initialdir=initialdir, filetypes=filetypes)
        # check if the user cancelled the dialog (or something went wrong and we got None for safety)
        if (response is None) or (len(response) == 0):
            root.destroy()
            ask_to_exit()
        
        chosen = Path(response)
        # notify the user if their selection was invalid or did not exist
        if not is_valid_file(chosen):
            print(f'The specified file does not exist: {chosen.resolve(strict=False)}')
        # notify the user if their selection was not in the allowed filenames
        elif len(allowed_filenames) > 0 and chosen.name.lower() not in allowed_filenames:
            print(f'The specified file is not allowed: {chosen.resolve(strict=False)}')
    return chosen

# asks the user to select the mods directory
def ask_mods_directory(initialdir: Path = Path.cwd()) -> Path:
    return ask_directory('Please select the Mods Directory', 'Select Mods Directory', initialdir=initialdir)

# asks the user to select the output directory
def ask_output_directory(initialdir: Path = Path.cwd()) -> Path:
    return ask_directory('Please select the Output Directory', 'Select Output Directory', initialdir=initialdir)

# asks the user to select the create_pbr.exe path
def ask_create_pbr_path(initialdir: Path = Path.cwd()) -> Path:
    return ask_file('Please select create_pbr.exe', 'Select create_pbr.exe', initialdir=initialdir, filetypes=[('Executable Files', '*.exe')], allowed_filenames=['create_pbr.exe'])

# asks the user to select the checkpoint
def ask_checkpoint() -> str:
    selected_checkpoint = ''
    while selected_checkpoint not in allowed_checkpoints:
        print('Specify the model to use.')
        print(f'Allowed values: {", ".join(allowed_checkpoints)}')
        selected_checkpoint = input(f'Checkpoint [default {default_checkpoint}]: ').strip().lower()
        if selected_checkpoint == '':
            selected_checkpoint = default_checkpoint
            print(f'Defaulting to {selected_checkpoint}\n')
        elif selected_checkpoint in allowed_checkpoints:
            print(f'Selected checkpoint: {selected_checkpoint}\n')
        else:
            print(f'Invalid checkpoint: {selected_checkpoint}')
    return selected_checkpoint

# asks the user to select the texture format
def ask_texture_format() -> str:
    selected_format = ''
    while selected_format not in allowed_texture_formats:
        print('Specify the texture format to output.')
        print('Using a format other than DDS not recommended unless you plan on editing the textures after conversion.')
        print('The textures must be in DDS format for the game to read them efficiently.')
        print(f'Allowed values: {", ".join(allowed_texture_formats)}')
        selected_format = input(f'Texture Format [default {default_texture_format}]: ').strip().lower()
        if selected_format == '':
            selected_format = default_texture_format
            print(f'Defaulting to {selected_format}\n')
        elif selected_format in allowed_texture_formats:
            print(f'Selected texture format: {selected_format}\n')
        else:
            print(f'Invalid texture format: {selected_format}')
    return selected_format

# asks the user to select the max tile size
def ask_max_tile_size() -> str:
    selected_size = ''
    while selected_size not in allowed_tile_sizes:
        print('Specify the maximum tile size for the output textures.')
        print('Using 2048 will most likely result in very large textures and long processing times due to VRAM bottlencking.')
        print('Only use 1024 unless you have all textures under 1k or you have unlimited VRAM/time.')
        print(f'Allowed values: {", ".join(allowed_tile_sizes)}')
        selected_size = input(f'Max Tile Size [default {default_max_tile_size}]: ').strip()
        if selected_size == '':
            selected_size = default_max_tile_size
            print(f'Defaulting to {selected_size}\n')
        elif selected_size in allowed_tile_sizes:
            print(f'Selected max tile size: {selected_size}\n')
        else:
            print(f'Invalid max tile size: {selected_size}')
    return selected_size

# Check if the mods_directory setting is valid, otherwise ask the user to select it
if (settings['mods_directory'] is None) or (not is_valid_directory(settings['mods_directory'])):
    settings['mods_directory'] = ask_mods_directory()

# Check if the output_directory setting is valid, otherwise ask the user to select it
if (settings['output_directory'] is None) or (not is_valid_directory(settings['output_directory'])):
    settings['output_directory'] = ask_output_directory()

# Check if the create_pbr_path setting is valid, otherwise ask the user to select it
if (settings['create_pbr_path'] is None) or (not is_valid_file(settings['create_pbr_path'])) or (not settings['create_pbr_path'].name.lower() == 'create_pbr.exe'):
    settings['create_pbr_path'] = ask_create_pbr_path()

# Failsafe checks
needs_to_exit = False
if (settings['mods_directory'] is None) or (not is_valid_directory(settings['mods_directory'])):
    print(f'The specified mods_directory does not exist: {settings["mods_directory"]}')
    needs_to_exit = True

if (settings['output_directory'] is None) or (not is_valid_directory(settings['output_directory'])):
    print(f'The specified output_directory does not exist: {settings["output_directory"]}')
    needs_to_exit = True

if (settings['create_pbr_path'] is None) or (not is_valid_file(settings['create_pbr_path'])) or (not settings['create_pbr_path'].name.lower() == 'create_pbr.exe'):
    print(f'The specified create_pbr_path is not create_pbr.exe: {settings["create_pbr_path"]}')
    needs_to_exit = True

if needs_to_exit:
    root.destroy()
    ask_to_exit()

# presents the prompt to the user and returns their yes/no answer
# if default is True, then hitting enter counts as yes
# if default is False, then hitting enter counts as no
# if allow_exit is True, then the user can also enter 'e' to exit the program
def user_confirm(prompt: str, default: bool, allow_exit: bool=False) -> bool:
    # the allowed answers to display to the user
    # uppercase means the default option
    answer_prompt = 'Y/n' if default else 'y/N'
    if allow_exit:
        answer_prompt += ' or e to exit'
    # the list of answers to accept
    allowed_answers = ['y', 'yes', 'n', 'no', '']
    if allow_exit:
        allowed_answers.append('e')
        allowed_answers.append('exit')
    # build the full prompt that will be displayed to the user
    full_prompt = f'{prompt} ({answer_prompt}): '
    # get the user's answer
    confirm = input(full_prompt).strip().lower()
    # loop until we get a valid answer
    while confirm not in allowed_answers:
        if allow_exit:
            print('Please enter "y" for yes, "n" for no, or "e" to exit.')
        else:
            print('Please enter "y" for yes or "n" for no.')
        confirm = input(full_prompt).strip().lower()
    if (confirm == 'e') or (confirm == 'exit'):
        print('Exiting...')
        root.destroy()
        ask_to_exit()
    if confirm == '':
        return default
    return (confirm == 'y') or (confirm == 'yes')

# checks the provided settings with the user
# if the user does not confirm, this will ask them to validate each setting individually
# giving them the option to change each one
# returns the confirmed/corrected settings
def check_settings(user_settings: dict) -> dict:
    # print the current settings
    print('\nCurrent Settings:')
    print(f"Source     {user_settings['mods_directory'].resolve()}")
    print(f"Output     {user_settings['output_directory'].resolve()}")
    print(f"create_pbr {user_settings['create_pbr_path'].resolve()}")
    print(f"Checkpoint {user_settings['checkpoint']}")
    print(f"Format     {user_settings['texture_format']}")
    print(f"Tile Size  {user_settings['max_tile_size']}")
    print()
    print('WARNING: Misconfigured source/destination may have disastrous consequences.')
    print()
    # create a copy of the settings to modify
    new_settings = {
        'mods_directory': user_settings['mods_directory'],
        'output_directory': user_settings['output_directory'],
        'create_pbr_path': user_settings['create_pbr_path'],
        'checkpoint': user_settings['checkpoint'],
        'texture_format': user_settings['texture_format'],
        'max_tile_size': user_settings['max_tile_size']
    }
    # ask the user to confirm the settings
    user_confirmed_settings = user_confirm('Are these settings correct?', True, allow_exit=True)

    if not user_confirmed_settings:
        # the user did not confirm the settings, so ask them to validate each one individually
        # and recursively call this function again afterward to verify the new settings
        print(f"Source: {new_settings['mods_directory'].resolve()}")
        if not user_confirm('Is Source correct?', True):
            new_settings['mods_directory'] = ask_mods_directory()
        print(f"Output: {new_settings['output_directory'].resolve()}")
        if not user_confirm('Is Output correct?', True):
            new_settings['output_directory'] = ask_output_directory()
        print(f"create_pbr.exe Path: {new_settings['create_pbr_path'].resolve()}")
        if not user_confirm('Is create_pbr.exe path correct?', True):
            new_settings['create_pbr_path'] = ask_create_pbr_path()
        print(f"Checkpoint: {new_settings['checkpoint']}")
        if not user_confirm('Is Checkpoint correct?', True):
            new_settings['checkpoint'] = ask_checkpoint()
        print(f"Texture Format: {new_settings['texture_format']}")
        if not user_confirm('Is Texture Format correct?', True):
            new_settings['texture_format'] = ask_texture_format()
        print(f"Max Tile Size: {new_settings['max_tile_size']}")
        if not user_confirm('Is Max Tile Size correct?', True):
            new_settings['max_tile_size'] = ask_max_tile_size()
        # start from the top again to confirm all settings
        return check_settings(new_settings)
    else:
        # the user confirmed the settings
        return new_settings

# confirm settings with the user
settings = check_settings(settings)

# we are done with tkinter
root.destroy()

# write the settings to the config file
with open(config_file_path, 'w') as config_file:
    config_file.write(f'mods_directory={settings["mods_directory"].resolve()}\n')
    config_file.write(f'output_directory={settings["output_directory"].resolve()}\n')
    config_file.write(f'create_pbr_path={settings["create_pbr_path"].resolve()}\n')
    config_file.write(f'checkpoint={settings["checkpoint"]}\n')
    config_file.write(f'texture_format={settings["texture_format"]}\n')
    config_file.write(f'max_tile_size={settings["max_tile_size"]}\n')

# have the user confirm that they know how to safely abort the program
print('\nAt any time you may hold Ctrl+C to abort the program.')
print('If you abort the program, please delete the last processed output mod folder in the output directory or else it will be skipped next time.\n')
input('Press Enter to confirm you have read and understood this message.')

# assign settings to variables for easier access
mods_directory: Path = settings['mods_directory']
output_directory: Path = settings['output_directory']
create_pbr_path: Path = settings['create_pbr_path']
checkpoint: str = settings['checkpoint']
texture_format: str = settings['texture_format']
max_tile_size: str = settings['max_tile_size']

# checks if the folder f has a textures folder, but does not have a pbr folder
def has_textures_but_no_pbr(f: Path) -> bool:
    textures_paths = list(f.glob('textures', case_sensitive=False))
    # There must be exactly one textures folder
    # 0 means no textures folder
    # >1 means multiple textures folders which would not only cause problems in the conversion, but likely also with the game.
    if len(textures_paths) == 1:
        # textures_paths[0] is guaranteed to be a folder named textures
        textures_path = textures_paths[0]
        if is_valid_directory(textures_path):
            # check if there is a pbr folder inside the textures folder
            all_pbr_paths = list(textures_path.glob('pbr', case_sensitive=False))
            if len(all_pbr_paths) == 0:
                # All checks passed, so return true
                return True
    # If any of the above checks failed, then return false
    return False

# list all of the mod names/paths
mods: list[Path] = [f for f in mods_directory.iterdir() if is_valid_directory(f)]

# filter out all mods that do not have textures or already have pbr
filtered_mods = []
with tqdm(mods, miniters=1, desc='Filtering for mods with textures and no PBR') as pbar:
    for mod_path in pbar:
        if has_textures_but_no_pbr(mod_path):
            filtered_mods.append(mod_path)
mods = filtered_mods

# filter out all mods that have already been converted
filtered_mods = []
with tqdm(mods, miniters=1, desc='Filtering existing conversions') as pbar:
    for mod_path in pbar:
        output_path = output_directory / f'{mod_path.name} PBR'
        if not output_path.exists():
            filtered_mods.append(mod_path)
mods = filtered_mods

# sanitize the suffixes of textures otherwise convert_pbr will fail to recognize them
# list of suffixes convert_pbr recognizes
allowed_suffixes = ['diffuse', 'diff', 'd', 'normal', 'norm', 'n', 'glow', 'g']
suffix_capture_regex = re.compile(r'_(?P<suffix>[^_.]+)(\.dds)$', re.IGNORECASE)
def fix_suffix_case(filename: str, allowed_suffixes: list[str]) -> str:
    allowed = {s.lower() for s in allowed_suffixes}
    m = suffix_capture_regex.search(filename)
    if not m:
        return filename
    suffix = m.group('suffix')
    if suffix.lower() in allowed and any(c.isupper() for c in suffix):
        return filename[:m.start('suffix')] + suffix.lower() + m.group(2)
    return filename

digits_at_end_of_string_regex = re.compile(r'(\d+)\s*$')
with open(pbrify_log_path, 'w') as log_file:
    with tqdm(mods, miniters=1, position=0) as pbar:
        # main process:
        # for each mod...
        for mod_path in pbar:
            mod_name = mod_path.name
            message = f'Processing {mod_name}'
            log_file.write(message + '\n')
            pbar.set_description(message)

            # this will always succeed because of the earlier has_textures_but_no_pbr check
            textures_path = next(mod_path.glob('textures', case_sensitive=False))

            # the path to the converted files
            output_path = output_directory / f'{mod_name} PBR'

            # if there is already something at the output path, then it must have already been converted
            if is_valid_directory(output_path):
                message = f'{mod_name} has already been processed.'
                log_file.write(message + '\n')
                tqdm.write(message)
                continue

            # The above check should prevent os.makedirs from throwing an error,
            # since if the directory exists we skip to the next mod.
            # However it is safer to keep exists_ok=False, since if the logic were to fail
            # we would crash the program instead of potentially overwriting existing data.
            os.makedirs(output_path, exist_ok=False)
            
            # iterate through all the files in the mod to sanitize any bad names
            # this is necessary because create_pbr.exe is case-sensitive for suffixes
            all_textures = list(textures_path.rglob('*.dds', case_sensitive=False))
            for texture_path in all_textures:
                if is_valid_file(texture_path):
                    sanitized_name = fix_suffix_case(texture_path.name, allowed_suffixes)
                    if sanitized_name != texture_path.name:
                        new_path = texture_path.with_name(sanitized_name)
                        message = f'[Sanitize Case] Renaming {texture_path.relative_to(mod_path)} to {new_path.relative_to(mod_path)}'
                        log_file.write(message + '\n')
                        tqdm.write(message)
                        os.rename(texture_path, new_path)
            
            # this is where the magic happens
            process = subprocess.Popen([create_pbr_path.resolve(), '--input_dir', mod_path.resolve(), '--output_dir', output_path.resolve(), '--format', texture_format, '--max_tile_size', max_tile_size, '--segformer_checkpoint', checkpoint, '--create_jsons', 'true'], bufsize=1, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
            
            process_stdout = process.stdout
            if process_stdout is None:
                message = f'Failed to create pipe for create_pbr.exe log. Exit to be safe.'
                log_file.write(message + '\n')
                print('\n' + message)
                process.terminate()
                print('After exiting you should delete the last processed conversion output folder to avoid skipping it next time.')
                ask_to_exit()
                sys.exit()

            # create a log file for this specific mod
            with open(output_path / f'{mod_name}_LOG.txt', 'w') as mod_log_file:
                with tqdm(total=0, position=1, miniters=1, desc='Processing Pairs') as sub_pbar:
                    # constantly check the process for any new strings to print
                    # necessary to avoid messing up tqdm bar
                    # inefficient and i know there is a better way to do it but it is short and sweet and i don't care to change it
                    while process.poll() is None:
                        line = process_stdout.readline().strip()
                        if len(line) > 0:
                            # create_pbr.exe will print a line containing ": found X" when it starts processing
                            # where X is the number of texture pairs to process
                            if ': found' in line:
                                count_search = digits_at_end_of_string_regex.search(line)
                                if count_search:
                                    sub_pbar.total = int(count_search.group(1))
                                else:
                                    message = f'Could not parse texture count from line:\n {line}'
                                    log_file.write(message + '\n')
                            # When a pair is processed, create_pbr.exe will print a line containing "PBR inference complete"
                            elif 'PBR inference complete' in line:
                                sub_pbar.update(1)
                            # If texture is skipped, create_pbr.exe will print a line containing " Skipping "
                            elif ' Skipping ' in line:
                                sub_pbar.total -= 1
                            log_file.write(line + '\n')
                            mod_log_file.write(line + '\n')
                            tqdm.write(line)
            # make sure that if ANYTHING goes wrong above we wait gracefully instead of spawning hundreds of processes
            process.wait()
            
            message = f'Finished processing {mod_name}.'
            log_file.write(message + '\n\n')
            pbar.set_description(message)
            tqdm.write(message + '\n')

input('Complete! Press Enter to exit.')
