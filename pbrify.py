# AUTHORS: AlhimikPh, shak

# Thank you to AlhimikPh for cleaning up my messy code, implementing a proper UI,
# and giving me advice on PyInstaller compilation.
# - shak

import sys
import os
import subprocess
import re
import logging
import itertools
from pathlib import Path
from dataclasses import dataclass
from typing import Optional
from datetime import datetime

# ═══════════════════════════════════════════════════════════════════════════════
# PYSIDE6 IMPORTS
# ═══════════════════════════════════════════════════════════════════════════════

try:
    from PySide6.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QGridLayout, QLabel, QLineEdit, QPushButton, QComboBox,
        QProgressBar, QTextEdit, QGroupBox, QFileDialog, QMessageBox,
        QStatusBar, QFrame, QSplitter, QSizePolicy
    )
    from PySide6.QtCore import Qt, QThread, Signal, QObject
    from PySide6.QtGui import QFont, QIcon, QPalette, QColor
except ImportError:
    print("PySide6 is required. Install it with: pip install PySide6")
    sys.exit(1)

# ═══════════════════════════════════════════════════════════════════════════════
# CONSTANTS
# ═══════════════════════════════════════════════════════════════════════════════

PYTHON_MIN_VERSION = (3, 12)
CONFIG_FILE_NAME = 'config.txt'
LOG_FILE_NAME = 'pbrify_log.txt'

ALLOWED_CHECKPOINTS = ['s4', 's4_alt']
DEFAULT_CHECKPOINT = 's4'

ALLOWED_TEXTURE_FORMATS = ['dds', 'png']
DEFAULT_TEXTURE_FORMAT = 'dds'

ALLOWED_TILE_SIZES = ['1024', '2048']
DEFAULT_TILE_SIZE = '1024'

ALLOWED_NORMAL_SUFFIXES = ['n', 'norm', 'normal']
ALLOWED_DIFFUSE_SUFFIXES = ['d', 'diff', 'diffuse']
ALLOWED_GLOW_SUFFIXES = ['g', 'glow']
ALLOWED_SUFFIXES = ALLOWED_NORMAL_SUFFIXES + ALLOWED_DIFFUSE_SUFFIXES + ALLOWED_GLOW_SUFFIXES

# ═══════════════════════════════════════════════════════════════════════════════
# PHOTOSHOP-LIKE DARK THEME STYLESHEET
# ═══════════════════════════════════════════════════════════════════════════════

DARK_STYLESHEET = """
/* Main Window */
QMainWindow {
    background-color: #1e1e1e;
}

QWidget {
    background-color: #2d2d2d;
    color: #e0e0e0;
    font-family: "Segoe UI", Arial, sans-serif;
    font-size: 12px;
}

/* Group Boxes */
QGroupBox {
    background-color: #383838;
    border: 1px solid #4a4a4a;
    border-radius: 4px;
    margin-top: 12px;
    padding: 10px;
    padding-top: 20px;
    font-weight: bold;
    color: #ffffff;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 10px;
    padding: 0 5px;
    background-color: #383838;
    color: #9cdcfe;
}

/* Labels */
QLabel {
    background-color: transparent;
    color: #d4d4d4;
    padding: 2px;
}

/* Line Edits */
QLineEdit {
    background-color: #1e1e1e;
    border: 1px solid #4a4a4a;
    border-radius: 3px;
    padding: 6px 10px;
    color: #ffffff;
    selection-background-color: #264f78;
}

QLineEdit:focus {
    border: 1px solid #0078d4;
}

QLineEdit:disabled {
    background-color: #2d2d2d;
    color: #6d6d6d;
}

/* Buttons */
QPushButton {
    background-color: #0e639c;
    border: none;
    border-radius: 3px;
    padding: 8px 16px;
    color: #ffffff;
    font-weight: 500;
    min-width: 80px;
}

QPushButton:hover {
    background-color: #1177bb;
}

QPushButton:pressed {
    background-color: #0d5a8c;
}

QPushButton:disabled {
    background-color: #3d3d3d;
    color: #6d6d6d;
}

/* Secondary Buttons */
QPushButton[class="secondary"] {
    background-color: #3d3d3d;
    border: 1px solid #4a4a4a;
}

QPushButton[class="secondary"]:hover {
    background-color: #4a4a4a;
    border: 1px solid #5a5a5a;
}

/* Stop Button */
QPushButton[class="danger"] {
    background-color: #c42b1c;
}

QPushButton[class="danger"]:hover {
    background-color: #d63a2b;
}

QPushButton[class="danger"]:pressed {
    background-color: #a52515;
}

/* Combo Boxes */
QComboBox {
    background-color: #1e1e1e;
    border: 1px solid #4a4a4a;
    border-radius: 3px;
    padding: 6px 10px;
    color: #ffffff;
    min-width: 100px;
}

QComboBox:hover {
    border: 1px solid #5a5a5a;
}

QComboBox:focus {
    border: 1px solid #0078d4;
}

QComboBox::drop-down {
    border: none;
    width: 24px;
}

QComboBox::down-arrow {
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 6px solid #9cdcfe;
    margin-right: 8px;
}

QComboBox QAbstractItemView {
    background-color: #1e1e1e;
    border: 1px solid #4a4a4a;
    selection-background-color: #0e639c;
    selection-color: #ffffff;
    outline: none;
}

/* Progress Bars */
QProgressBar {
    background-color: #1e1e1e;
    border: 1px solid #4a4a4a;
    border-radius: 3px;
    height: 20px;
    text-align: center;
    color: #ffffff;
}

QProgressBar::chunk {
    background-color: #0e639c;
    border-radius: 2px;
}

/* Text Edit (Log) */
QTextEdit {
    background-color: #1e1e1e;
    border: 1px solid #4a4a4a;
    border-radius: 4px;
    padding: 8px;
    color: #d4d4d4;
    font-family: "Consolas", "Courier New", monospace;
    font-size: 11px;
    selection-background-color: #264f78;
}

/* Status Bar */
QStatusBar {
    background-color: #007acc;
    color: #ffffff;
    padding: 4px;
    font-size: 11px;
}

QStatusBar::item {
    border: none;
}

/* Scrollbars */
QScrollBar:vertical {
    background-color: #2d2d2d;
    width: 12px;
    border: none;
}

QScrollBar::handle:vertical {
    background-color: #5a5a5a;
    border-radius: 4px;
    min-height: 30px;
    margin: 2px;
}

QScrollBar::handle:vertical:hover {
    background-color: #6a6a6a;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    background-color: #2d2d2d;
    height: 12px;
    border: none;
}

QScrollBar::handle:horizontal {
    background-color: #5a5a5a;
    border-radius: 4px;
    min-width: 30px;
    margin: 2px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #6a6a6a;
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0px;
}

/* Frames */
QFrame[class="separator"] {
    background-color: #4a4a4a;
}

/* Tool Tips */
QToolTip {
    background-color: #1e1e1e;
    border: 1px solid #4a4a4a;
    color: #d4d4d4;
    padding: 4px;
}
"""

# ═══════════════════════════════════════════════════════════════════════════════
# LOGGING SETUP
# ═══════════════════════════════════════════════════════════════════════════════

class LogSignals(QObject):
    """Signals for thread-safe logging to UI."""
    message = Signal(str)


class QTextEditHandler(logging.Handler):
    """Logging handler that emits signals for thread-safe UI updates."""
    
    def __init__(self, signals: LogSignals):
        super().__init__()
        self.signals = signals
        
    def emit(self, record):
        msg = self.format(record)
        self.signals.message.emit(msg)


def setup_logging(log_signals: Optional[LogSignals] = None) -> logging.Logger:
    """Setup logging to file and optionally to a text widget."""
    logger = logging.getLogger('PBRify')
    logger.setLevel(logging.DEBUG)
    logger.handlers.clear()
    
    # File handler
    log_path = Path.cwd() / LOG_FILE_NAME
    file_handler = logging.FileHandler(log_path, mode='w', encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s', datefmt='%H:%M:%S')
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    # UI handler
    if log_signals:
        ui_handler = QTextEditHandler(log_signals)
        ui_handler.setLevel(logging.INFO)
        ui_formatter = logging.Formatter('[%(levelname)s] %(message)s')
        ui_handler.setFormatter(ui_formatter)
        logger.addHandler(ui_handler)
    
    return logger

# ═══════════════════════════════════════════════════════════════════════════════
# UTILITY FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

# Regex patterns
SUFFIX_CAPTURE_REGEX = re.compile(r'_(?P<suffix>[^_.]+)(\.dds)$', re.IGNORECASE)
DIGITS_AT_END_REGEX = re.compile(r'(\d+)\s*$')
NORMAL_MAP_REGEX = re.compile(fr'_({'|'.join(ALLOWED_NORMAL_SUFFIXES)})$', re.IGNORECASE)


def fix_suffix_case(filename: str, allowed_suffixes: list) -> str:
    """Fix the case of texture suffixes to lowercase."""
    allowed = {s.lower() for s in allowed_suffixes}
    m = SUFFIX_CAPTURE_REGEX.search(filename)
    # check if we matched any suffix (_[suffix].dds)
    if m:
        suffix = m.group('suffix')
        # check if the suffix is in the allowed list and if it contains any uppercase letters
        if suffix.lower() in allowed and any(c.isupper() for c in suffix):
            # fix the file name and return it
            return filename[:m.start('suffix')] + suffix.lower() + filename[m.end('suffix'):]
    # if anything above failed, then the filename is alright. just return as is.
    return filename


def has_textures_but_no_pbr(folder: Path) -> bool:
    """Check if folder has a textures folder but no pbr folder."""
    try:
        textures_paths = [p for p in folder.iterdir() if p.is_dir() and p.name.lower() == 'textures']
        
        # if len < 1: there is no textures folder
        # if len > 1: there are multiple textures folders (only possible on case-sensitive file systems)
        if len(textures_paths) != 1:
            return False
        
        pbr_paths = [p for p in textures_paths[0].iterdir() if p.is_dir() and p.name.lower() == 'pbr']
        if len(pbr_paths) > 0:
            return False
        
        return True
    except Exception:
        return False

def has_valid_pairs(mod_folder: Path) -> bool:
    """Check if the folder has valid diffuse/normal pairs to be processed."""
    try:
        if mod_folder is None or not mod_folder.is_dir():
            return False
        textures_folder = next(mod_folder.glob('textures', case_sensitive=False), None)
        if textures_folder is not None and textures_folder.is_dir():
            normal_iter = itertools.chain(
                textures_folder.rglob('*_n.dds', case_sensitive=False),
                textures_folder.rglob('*_norm.dds', case_sensitive=False),
                textures_folder.rglob('*_normal.dds', case_sensitive=False)
            )
            for normal in normal_iter:
                if normal.is_file():
                    normal_stem_without_suffix = NORMAL_MAP_REGEX.sub('', normal.stem)
                    diffuse_iter = itertools.chain(
                        normal.parent.glob(f'{normal_stem_without_suffix}.dds', case_sensitive=False),
                        normal.parent.glob(f'{normal_stem_without_suffix}_d.dds', case_sensitive=False),
                        normal.parent.glob(f'{normal_stem_without_suffix}_diff.dds', case_sensitive=False),
                        normal.parent.glob(f'{normal_stem_without_suffix}_diffuse.dds', case_sensitive=False)
                    )
                    found_diffuse = next(diffuse_iter, None)
                    if found_diffuse and found_diffuse.is_file():
                        return True
        return False
    except Exception:
        return False
                


# ═══════════════════════════════════════════════════════════════════════════════
# DATA CLASSES
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class Settings:
    """Application settings."""
    mods_directory: Optional[Path] = None
    output_directory: Optional[Path] = None
    create_pbr_path: Optional[Path] = None
    checkpoint: str = DEFAULT_CHECKPOINT
    texture_format: str = DEFAULT_TEXTURE_FORMAT
    max_tile_size: str = DEFAULT_TILE_SIZE
    
    def is_valid(self) -> bool:
        """Check if all required settings are valid."""
        return (
            self.mods_directory is not None and self.mods_directory.is_dir() and
            self.output_directory is not None and self.output_directory.is_dir() and
            self.create_pbr_path is not None and self.create_pbr_path.is_file() and
            self.create_pbr_path.name.lower() == 'create_pbr.exe'
        )
    
    def save(self, path: Path) -> bool:
        """Save settings to a config file. Returns False on failure."""
        try:
            with open(path, 'w', encoding='utf-8') as f:
                if self.mods_directory:
                    f.write(f'mods_directory={self.mods_directory.resolve()}\n')
                if self.output_directory:
                    f.write(f'output_directory={self.output_directory.resolve()}\n')
                if self.create_pbr_path:
                    f.write(f'create_pbr_path={self.create_pbr_path.resolve()}\n')
                f.write(f'checkpoint={self.checkpoint}\n')
                f.write(f'texture_format={self.texture_format}\n')
                f.write(f'max_tile_size={self.max_tile_size}\n')
            return True
        except Exception:
            return False
    
    @classmethod
    def load(cls, path: Path) -> Settings:
        """Load settings from a config file."""
        settings = cls()
        if not path.exists():
            return settings
            
        try:
            with open(path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            config = {}
            for line in lines:
                line = line.strip()
                if '=' in line:
                    key, value = line.split('=', 1)
                    config[key.strip()] = value.strip()
            
            if 'mods_directory' in config:
                p = Path(config['mods_directory'])
                if p.is_dir():
                    settings.mods_directory = p
            
            if 'output_directory' in config:
                p = Path(config['output_directory'])
                if p.is_dir():
                    settings.output_directory = p
            
            if 'create_pbr_path' in config:
                p = Path(config['create_pbr_path'])
                if p.is_file() and p.name.lower() == 'create_pbr.exe':
                    settings.create_pbr_path = p
            
            if 'checkpoint' in config and config['checkpoint'] in ALLOWED_CHECKPOINTS:
                settings.checkpoint = config['checkpoint']
            
            if 'texture_format' in config and config['texture_format'] in ALLOWED_TEXTURE_FORMATS:
                settings.texture_format = config['texture_format']
            
            if 'max_tile_size' in config and config['max_tile_size'] in ALLOWED_TILE_SIZES:
                settings.max_tile_size = config['max_tile_size']
                
        except Exception:
            pass
        
        return settings


@dataclass
class ProcessingStats:
    """Statistics for the processing run."""
    total_mods: int = 0
    processed_mods: int = 0
    skipped_mods: int = 0
    failed_mods: int = 0
    total_textures: int = 0
    processed_textures: int = 0
    skipped_textures: int = 0
    renamed_files: int = 0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    
    def reset(self):
        """Reset all statistics."""
        self.total_mods = 0
        self.processed_mods = 0
        self.skipped_mods = 0
        self.failed_mods = 0
        self.total_textures = 0
        self.processed_textures = 0
        self.skipped_textures = 0
        self.renamed_files = 0
        self.start_time = None
        self.end_time = None
    
    def get_duration(self) -> str:
        """Get the duration of processing as a formatted string."""
        if self.start_time is None:
            return "N/A"
        end = self.end_time or datetime.now()
        delta = end - self.start_time
        total_seconds = int(delta.total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        if hours > 0:
            return f"{hours}h {minutes}m {seconds}s"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        else:
            return f"{seconds}s"
    
    def get_summary(self) -> str:
        """Get a summary of the processing run."""
        lines = [
            "═" * 50,
            "PROCESSING COMPLETE - SUMMARY",
            "═" * 50,
            f"Duration: {self.get_duration()}",
            f"Total mods found: {self.total_mods}",
            f"Mods processed: {self.processed_mods}",
            f"Mods skipped: {self.skipped_mods}",
            f"Mods failed: {self.failed_mods}",
            f"Files renamed: {self.renamed_files}",
            f"Textures processed: {self.processed_textures}",
            f"Textures skipped: {self.skipped_textures}",
            "═" * 50,
        ]
        return "\n".join(lines)

# ═══════════════════════════════════════════════════════════════════════════════
# WORKER THREAD SIGNALS
# ═══════════════════════════════════════════════════════════════════════════════

class WorkerSignals(QObject):
    """Signals for the processing worker thread."""
    progress = Signal(int, int, str)  # current, total, mod_name
    mod_progress = Signal(int, int)   # current, total
    finished = Signal(object)         # ProcessingStats
    error = Signal(str)

# ═══════════════════════════════════════════════════════════════════════════════
# PROCESSOR WORKER THREAD
# ═══════════════════════════════════════════════════════════════════════════════

class ProcessorWorker(QThread):
    """Worker thread for mod processing."""
    
    def __init__(self, settings: Settings, logger: logging.Logger):
        super().__init__()
        self.settings = settings
        self.logger = logger
        self.signals = WorkerSignals()
        self.stats = ProcessingStats()
        self.should_stop = False
        self.current_process: Optional[subprocess.Popen] = None
    
    def stop(self):
        """Request to stop processing."""
        self.should_stop = True
        if self.current_process:
            try:
                self.current_process.terminate()
            except Exception:
                pass
    
    def get_mods_to_process(self) -> list:
        """Get list of mods that need processing."""
        mods = []
        try:
            if (self.settings.mods_directory is None or
                not self.settings.mods_directory.is_dir()
                or self.settings.output_directory is None or
                not self.settings.output_directory.is_dir()):
                return []
            
            all_folders = [f for f in self.settings.mods_directory.iterdir() if f.is_dir()]
            
            for folder in all_folders:
                if has_textures_but_no_pbr(folder):
                    if has_valid_pairs(folder):
                        output_path = self.settings.output_directory / f'{folder.name} PBR'
                        if not output_path.exists():
                            mods.append(folder)
        except Exception as e:
            self.logger.error(f"Error scanning mods directory: {e}")
            return [] # in case of error, return empty list to avoid processing
        return mods
    
    def run(self):
        """Main processing loop."""
        self.should_stop = False
        self.stats.reset()
        self.stats.start_time = datetime.now()
        
        try:
            mods = self.get_mods_to_process()
            self.stats.total_mods = len(mods)
            
            if len(mods) == 0:
                self.logger.info("No mods to process.")
                self.stats.end_time = datetime.now()
                self.signals.finished.emit(self.stats)
                return
            
            self.logger.info(f"Found {len(mods)} mods to process.")
            
            for i, mod_path in enumerate(mods):
                if self.should_stop:
                    self.logger.warning("Processing stopped by user.")
                    break
                
                self.signals.progress.emit(i + 1, len(mods), mod_path.name)
                
                success = self.process_mod(mod_path)
                
                if success:
                    self.stats.processed_mods += 1
                elif self.should_stop:
                    break
                else:
                    self.stats.failed_mods += 1
                    
        except Exception as e:
            self.logger.error(f"Critical error during processing: {e}")
            self.signals.error.emit(str(e))
        finally:
            self.stats.end_time = datetime.now()
            self.logger.info(self.stats.get_summary())
            self.signals.finished.emit(self.stats)
    
    def process_mod(self, mod_path: Path) -> bool:
        """Process a single mod. Returns True on success."""
        mod_name = mod_path.name
        self.logger.info(f"Processing: {mod_name}")
        
        try:
            if self.settings.output_directory is None or not self.settings.output_directory.is_dir():
                self.logger.error("Output directory is not set.")
                return False
    
            # Find textures folder
            textures_paths = [p for p in mod_path.iterdir() if p.is_dir() and p.name.lower() == 'textures']
            if not textures_paths:
                self.logger.warning(f"No textures folder found in {mod_name}")
                self.stats.skipped_mods += 1
                return False
            
            output_path = self.settings.output_directory / f'{mod_name} PBR'
            
            # Check if already processed
            if output_path is not None and output_path.is_dir():
                self.logger.info(f"{mod_name} already processed, skipping.")
                self.stats.skipped_mods += 1
                return False
            
            # Create output directory
            os.makedirs(output_path, exist_ok=False) # explicitly fail if the directory exists to avoid overwriting in case of an error
            
            # Sanitize texture names
            self.sanitize_textures(mod_path)
            
            # Run create_pbr.exe
            success = self.run_create_pbr(mod_path, output_path, mod_name)
            
            if success:
                self.logger.info(f"Finished processing: {mod_name}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error processing {mod_name}: {e}")
            return False
    
    def sanitize_textures(self, mod_path: Path):
        """Sanitize texture file names."""
        try:
            all_textures = list(mod_path.rglob('*.dds', case_sensitive=False))
            for texture_path in all_textures:
                if texture_path.is_file():
                    sanitized_name = fix_suffix_case(texture_path.name, ALLOWED_SUFFIXES)
                    if sanitized_name != texture_path.name:
                        new_path = texture_path.with_name(sanitized_name)
                        self.logger.debug(f"Renaming: {texture_path} -> {sanitized_name}")
                        os.rename(texture_path, new_path)
                        self.stats.renamed_files += 1
        except Exception as e:
            self.logger.error(f"Error sanitizing textures: {e}")
    
    def run_create_pbr(self, mod_path: Path, output_path: Path, mod_name: str) -> bool:
        """Run create_pbr.exe on a mod."""
        try:
            # check paths for sanity
            if self.settings.create_pbr_path is None or not self.settings.create_pbr_path.is_file() or not self.settings.create_pbr_path.name.lower() == 'create_pbr.exe':
                self.logger.error("create_pbr.exe path is not set or invalid.")
                return False
            if self.settings.mods_directory is None or not self.settings.mods_directory.is_dir():
                self.logger.error(f"Mod path is invalid: {mod_path}")
                return False
            if self.settings.output_directory is None or not self.settings.output_directory.is_dir():
                self.logger.error(f"Output path is invalid: {output_path}")
                return False
            cmd = [
                str(self.settings.create_pbr_path.resolve()),
                '--input_dir', str(mod_path.resolve()),
                '--output_dir', str(output_path.resolve()),
                '--format', self.settings.texture_format,
                '--max_tile_size', self.settings.max_tile_size,
                '--segformer_checkpoint', self.settings.checkpoint,
                '--create_jsons', 'true'
            ]
            
            self.current_process = subprocess.Popen(
                cmd,
                bufsize=1,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True
            )
            
            if self.current_process.stdout is None:
                self.logger.error("Failed to create pipe for create_pbr.exe")
                return False
            
            # Create mod-specific log
            mod_log_path = output_path / f'{mod_name}_LOG.txt'
            texture_count = 0
            processed_count = 0
            
            with open(mod_log_path, 'w', encoding='utf-8') as mod_log:
                while self.current_process.poll() is None:
                    if self.should_stop:
                        self.current_process.terminate()
                        return False
                    
                    line = self.current_process.stdout.readline().strip()
                    if line:
                        mod_log.write(line + '\n')
                        self.logger.debug(line)
                        
                        if ': found' in line:
                            match = DIGITS_AT_END_REGEX.search(line)
                            if match:
                                texture_count = int(match.group(1))
                                self.stats.total_textures += texture_count
                        elif 'PBR inference complete' in line:
                            processed_count += 1
                            self.stats.processed_textures += 1
                            if texture_count > 0:
                                self.signals.mod_progress.emit(processed_count, texture_count)
                        elif ' Skipping ' in line:
                            texture_count -= 1
                            self.stats.skipped_textures += 1
            
            self.current_process.wait()
            return_code = self.current_process.returncode
            self.current_process = None
            
            return return_code == 0 or return_code is None
            
        except Exception as e:
            self.logger.error(f"Error running create_pbr.exe: {e}")
            return False

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN WINDOW
# ═══════════════════════════════════════════════════════════════════════════════

class PBRifyWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("PBRify - Texture Converter")
        self.setMinimumSize(850, 750)
        self.resize(900, 800)
        
        # Load settings
        self.config_path = Path.cwd() / CONFIG_FILE_NAME
        self.settings = Settings.load(self.config_path)
        
        # Worker thread
        self.worker: Optional[ProcessorWorker] = None
        
        # Setup logging signals
        self.log_signals = LogSignals()
        self.log_signals.message.connect(self.append_log)
        
        # Setup UI
        self.setup_ui()
        
        # Setup logging
        self.logger = setup_logging(self.log_signals)
        self.logger.info("PBRify initialized.")
        
    def setup_ui(self):
        """Setup the user interface."""
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)

        # ─────────────────────────────────────────────────────────────────────
        # Header
        # ─────────────────────────────────────────────────────────────────────
        header_widget = QWidget()
        header_widget.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        header_layout = QVBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(2)

        header_label = QLabel("PBRify")
        header_label.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #9cdcfe;
                padding: 0px;
            }
        """)
        header_layout.addWidget(header_label)

        subtitle_label = QLabel("Batch PBR Texture Converter for Mods")
        subtitle_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #808080;
                padding: 0px;
            }
        """)
        header_layout.addWidget(subtitle_label)

        main_layout.addWidget(header_widget)

        # ─────────────────────────────────────────────────────────────────────
        # Paths Section
        # ─────────────────────────────────────────────────────────────────────
        paths_group = QGroupBox("Paths")
        paths_group.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        paths_layout = QGridLayout(paths_group)
        paths_layout.setSpacing(8)
        paths_layout.setContentsMargins(10, 20, 10, 10)

        # Mods Directory
        mods_label = QLabel("Mods Directory:")
        mods_label.setFixedWidth(110)
        paths_layout.addWidget(mods_label, 0, 0, Qt.AlignmentFlag.AlignLeft)

        self.mods_dir_edit = QLineEdit()
        self.mods_dir_edit.setText(str(self.settings.mods_directory or ""))
        self.mods_dir_edit.setPlaceholderText("Select the folder containing your mods...")
        self.mods_dir_edit.setMinimumHeight(30)
        paths_layout.addWidget(self.mods_dir_edit, 0, 1)

        mods_browse_btn = QPushButton("Browse...")
        mods_browse_btn.setProperty("class", "secondary")
        mods_browse_btn.setFixedWidth(90)
        mods_browse_btn.clicked.connect(self.browse_mods_dir)
        paths_layout.addWidget(mods_browse_btn, 0, 2)

        # Output Directory
        output_label = QLabel("Output Directory:")
        output_label.setFixedWidth(110)
        paths_layout.addWidget(output_label, 1, 0, Qt.AlignmentFlag.AlignLeft)

        self.output_dir_edit = QLineEdit()
        self.output_dir_edit.setText(str(self.settings.output_directory or ""))
        self.output_dir_edit.setPlaceholderText("Select where to save converted mods...")
        self.output_dir_edit.setMinimumHeight(30)
        paths_layout.addWidget(self.output_dir_edit, 1, 1)

        output_browse_btn = QPushButton("Browse...")
        output_browse_btn.setProperty("class", "secondary")
        output_browse_btn.setFixedWidth(90)
        output_browse_btn.clicked.connect(self.browse_output_dir)
        paths_layout.addWidget(output_browse_btn, 1, 2)

        # create_pbr.exe Path
        pbr_label = QLabel("create_pbr.exe:")
        pbr_label.setFixedWidth(110)
        paths_layout.addWidget(pbr_label, 2, 0, Qt.AlignmentFlag.AlignLeft)

        self.create_pbr_edit = QLineEdit()
        self.create_pbr_edit.setText(str(self.settings.create_pbr_path or ""))
        self.create_pbr_edit.setPlaceholderText("Select create_pbr.exe...")
        self.create_pbr_edit.setMinimumHeight(30)
        paths_layout.addWidget(self.create_pbr_edit, 2, 1)

        pbr_browse_btn = QPushButton("Browse...")
        pbr_browse_btn.setProperty("class", "secondary")
        pbr_browse_btn.setFixedWidth(90)
        pbr_browse_btn.clicked.connect(self.browse_create_pbr)
        paths_layout.addWidget(pbr_browse_btn, 2, 2)

        paths_layout.setColumnStretch(0, 0)
        paths_layout.setColumnStretch(1, 1)
        paths_layout.setColumnStretch(2, 0)

        main_layout.addWidget(paths_group)

        # ─────────────────────────────────────────────────────────────────────
        # Options Section
        # ─────────────────────────────────────────────────────────────────────
        options_group = QGroupBox("Conversion Options")
        options_group.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        options_layout = QGridLayout(options_group)
        options_layout.setSpacing(10)
        options_layout.setContentsMargins(10, 20, 10, 10)

        # Model
        options_layout.addWidget(QLabel("Model:"), 0, 0, Qt.AlignmentFlag.AlignLeft)
        self.checkpoint_combo = QComboBox()
        self.checkpoint_combo.addItems(ALLOWED_CHECKPOINTS)
        self.checkpoint_combo.setCurrentText(self.settings.checkpoint)
        self.checkpoint_combo.setMinimumWidth(120)
        self.checkpoint_combo.setMinimumHeight(30)
        options_layout.addWidget(self.checkpoint_combo, 1, 0)

        # Format
        options_layout.addWidget(QLabel("Output Format:"), 0, 1, Qt.AlignmentFlag.AlignLeft)
        self.format_combo = QComboBox()
        self.format_combo.addItems(ALLOWED_TEXTURE_FORMATS)
        self.format_combo.setCurrentText(self.settings.texture_format)
        self.format_combo.setMinimumWidth(120)
        self.format_combo.setMinimumHeight(30)
        options_layout.addWidget(self.format_combo, 1, 1)

        # Tile Size
        options_layout.addWidget(QLabel("Max Tile Size:"), 0, 2, Qt.AlignmentFlag.AlignLeft)
        self.tile_combo = QComboBox()
        self.tile_combo.addItems(ALLOWED_TILE_SIZES)
        self.tile_combo.setCurrentText(self.settings.max_tile_size)
        self.tile_combo.setMinimumWidth(120)
        self.tile_combo.setMinimumHeight(30)
        options_layout.addWidget(self.tile_combo, 1, 2)

        # Spacer
        options_layout.setColumnStretch(3, 1)

        # Info
        info_label = QLabel("⚠ Using 2048 tile size requires significant VRAM")
        info_label.setStyleSheet("color: #d19a66;")
        options_layout.addWidget(info_label, 1, 3, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        main_layout.addWidget(options_group)

        # ─────────────────────────────────────────────────────────────────────
        # Progress Section
        # ─────────────────────────────────────────────────────────────────────
        progress_group = QGroupBox("Progress")
        progress_group.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        progress_layout = QGridLayout(progress_group)
        progress_layout.setSpacing(8)
        progress_layout.setContentsMargins(10, 20, 10, 10)

        # Overall progress
        overall_label_title = QLabel("Overall Progress:")
        overall_label_title.setFixedWidth(110)
        progress_layout.addWidget(overall_label_title, 0, 0, Qt.AlignmentFlag.AlignLeft)

        self.overall_progress = QProgressBar()
        self.overall_progress.setMinimum(0)
        self.overall_progress.setMaximum(100)
        self.overall_progress.setValue(0)
        self.overall_progress.setMinimumHeight(22)
        self.overall_progress.setTextVisible(False)
        progress_layout.addWidget(self.overall_progress, 0, 1)

        self.overall_label = QLabel("0 / 0")
        self.overall_label.setFixedWidth(80)
        self.overall_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        progress_layout.addWidget(self.overall_label, 0, 2)

        # Current mod progress
        mod_label_title = QLabel("Current Mod:")
        mod_label_title.setFixedWidth(110)
        progress_layout.addWidget(mod_label_title, 1, 0, Qt.AlignmentFlag.AlignLeft)

        self.mod_progress = QProgressBar()
        self.mod_progress.setMinimum(0)
        self.mod_progress.setMaximum(100)
        self.mod_progress.setValue(0)
        self.mod_progress.setMinimumHeight(22)
        self.mod_progress.setTextVisible(False)
        progress_layout.addWidget(self.mod_progress, 1, 1)

        self.mod_label = QLabel("0 / 0")
        self.mod_label.setFixedWidth(80)
        self.mod_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        progress_layout.addWidget(self.mod_label, 1, 2)

        # Status
        self.status_label = QLabel("● Ready")
        self.status_label.setStyleSheet("color: #4ec9b0; font-weight: bold;")
        progress_layout.addWidget(self.status_label, 2, 0, 1, 3, Qt.AlignmentFlag.AlignLeft)

        progress_layout.setColumnStretch(0, 0)
        progress_layout.setColumnStretch(1, 1)
        progress_layout.setColumnStretch(2, 0)

        main_layout.addWidget(progress_group)

        # ─────────────────────────────────────────────────────────────────────
        # Control Buttons
        # ─────────────────────────────────────────────────────────────────────
        buttons_widget = QWidget()
        buttons_widget.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        buttons_layout = QHBoxLayout(buttons_widget)
        buttons_layout.setContentsMargins(0, 5, 0, 5)
        buttons_layout.setSpacing(10)

        self.scan_btn = QPushButton("🔍 Scan Mods")
        self.scan_btn.setMinimumHeight(35)
        self.scan_btn.setMinimumWidth(120)
        self.scan_btn.clicked.connect(self.scan_mods)
        buttons_layout.addWidget(self.scan_btn)

        self.start_btn = QPushButton("▶ Start Processing")
        self.start_btn.setMinimumHeight(35)
        self.start_btn.setMinimumWidth(140)
        self.start_btn.clicked.connect(self.start_processing)
        buttons_layout.addWidget(self.start_btn)

        self.stop_btn = QPushButton("⬛ Stop")
        self.stop_btn.setProperty("class", "danger")
        self.stop_btn.setMinimumHeight(35)
        self.stop_btn.setMinimumWidth(100)
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self.stop_processing)
        buttons_layout.addWidget(self.stop_btn)

        buttons_layout.addStretch(1)

        self.save_btn = QPushButton("💾 Save Settings")
        self.save_btn.setProperty("class", "secondary")
        self.save_btn.setMinimumHeight(35)
        self.save_btn.setMinimumWidth(130)
        self.save_btn.clicked.connect(self.save_settings)
        buttons_layout.addWidget(self.save_btn)

        main_layout.addWidget(buttons_widget)

        # ─────────────────────────────────────────────────────────────────────
        # Log Section
        # ─────────────────────────────────────────────────────────────────────
        log_group = QGroupBox("Log Output")
        log_group.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        log_layout = QVBoxLayout(log_group)
        log_layout.setContentsMargins(10, 20, 10, 10)
        log_layout.setSpacing(8)

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        log_layout.addWidget(self.log_text, 1)

        # Clear log button
        clear_btn_layout = QHBoxLayout()
        clear_btn_layout.setContentsMargins(0, 0, 0, 0)
        clear_btn_layout.addStretch(1)

        clear_log_btn = QPushButton("Clear Log")
        clear_log_btn.setProperty("class", "secondary")
        clear_log_btn.setFixedWidth(100)
        clear_log_btn.setMinimumHeight(28)
        clear_log_btn.clicked.connect(self.clear_log)
        clear_btn_layout.addWidget(clear_log_btn)

        log_layout.addLayout(clear_btn_layout)

        main_layout.addWidget(log_group, 1)

        # ─────────────────────────────────────────────────────────────────────
        # Status Bar
        # ─────────────────────────────────────────────────────────────────────
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        self.statusbar.showMessage("Ready")
    
    def append_log(self, message: str):
        """Append a message to the log text widget."""
        self.log_text.append(message)
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def clear_log(self):
        """Clear the log text widget."""
        self.log_text.clear()
    
    def browse_mods_dir(self):
        """Browse for mods directory."""
        initial = self.mods_dir_edit.text() or str(Path.cwd())
        path = QFileDialog.getExistingDirectory(self, "Select Mods Directory", initial)
        if path:
            self.mods_dir_edit.setText(path)
            self.logger.info(f"Mods directory set to: {path}")
    
    def browse_output_dir(self):
        """Browse for output directory."""
        initial = self.output_dir_edit.text() or str(Path.cwd())
        path = QFileDialog.getExistingDirectory(self, "Select Output Directory", initial)
        if path:
            self.output_dir_edit.setText(path)
            self.logger.info(f"Output directory set to: {path}")
    
    def browse_create_pbr(self):
        """Browse for create_pbr.exe."""
        initial = self.create_pbr_edit.text() or str(Path.cwd())
        if initial and Path(initial).is_file():
            initial = str(Path(initial).parent)
        path, _ = QFileDialog.getOpenFileName(
            self, "Select create_pbr.exe", initial, "Executable Files (*.exe)"
        )
        if path:
            if Path(path).name.lower() == 'create_pbr.exe':
                self.create_pbr_edit.setText(path)
                self.logger.info(f"create_pbr.exe set to: {path}")
            else:
                QMessageBox.critical(self, "Invalid File", "Please select create_pbr.exe")
    
    def update_settings_from_ui(self):
        """Update settings from UI values."""
        mods_dir = self.mods_dir_edit.text()
        if mods_dir and Path(mods_dir).is_dir():
            self.settings.mods_directory = Path(mods_dir)
        else:
            self.settings.mods_directory = None
            
        output_dir = self.output_dir_edit.text()
        if output_dir and Path(output_dir).is_dir():
            self.settings.output_directory = Path(output_dir)
        else:
            self.settings.output_directory = None
            
        create_pbr = self.create_pbr_edit.text()
        if create_pbr and Path(create_pbr).is_file() and Path(create_pbr).name.lower() == 'create_pbr.exe':
            self.settings.create_pbr_path = Path(create_pbr)
        else:
            self.settings.create_pbr_path = None
            
        self.settings.checkpoint = self.checkpoint_combo.currentText()
        self.settings.texture_format = self.format_combo.currentText()
        self.settings.max_tile_size = self.tile_combo.currentText()
    
    def validate_settings(self) -> bool:
        """Validate current settings. Returns True if valid."""
        self.update_settings_from_ui()
        
        errors = []
        
        if not self.settings.mods_directory or not self.settings.mods_directory.is_dir():
            errors.append("• Mods directory is not set or does not exist.")
            
        if not self.settings.output_directory or not self.settings.output_directory.is_dir():
            errors.append("• Output directory is not set or does not exist.")
            
        if not self.settings.create_pbr_path or not self.settings.create_pbr_path.is_file():
            errors.append("• create_pbr.exe is not set or does not exist.")
        elif self.settings.create_pbr_path.name.lower() != 'create_pbr.exe':
            errors.append("• Selected file is not create_pbr.exe.")
            
        if self.settings.mods_directory and self.settings.output_directory:
            if self.settings.mods_directory.resolve() == self.settings.output_directory.resolve():
                errors.append("• Mods directory and output directory cannot be the same!")
        
        if errors:
            QMessageBox.critical(self, "Invalid Settings", "\n".join(errors))
            return False
            
        return True
    
    def save_settings(self):
        """Save current settings to config file."""
        self.update_settings_from_ui()
        if self.settings.save(self.config_path):
            self.logger.info("Settings saved successfully.")
            QMessageBox.information(self, "Settings Saved", f"Settings saved to:\n{self.config_path}")
        else:
            self.logger.error("Failed to save settings.")
            QMessageBox.critical(self, "Error", "Failed to save settings.")
    
    def scan_mods(self):
        """Scan for mods that need processing."""
        if not self.validate_settings():
            return
            
        self.logger.info("Scanning for mods...")
        self.statusbar.showMessage("Scanning...")
        QApplication.processEvents()
        
        try:
            temp_worker = ProcessorWorker(self.settings, self.logger)
            mods = temp_worker.get_mods_to_process()
            
            self.logger.info(f"Found {len(mods)} mods to process:")
            for mod in mods:
                self.logger.info(f"  → {mod.name}")
            
            self.overall_progress.setMaximum(max(len(mods), 1))
            self.overall_progress.setValue(0)
            self.overall_label.setText(f"0 / {len(mods)}")
            
            self.statusbar.showMessage(f"Found {len(mods)} mods to process.")
            
            if len(mods) == 0:
                QMessageBox.information(self, "Scan Complete", 
                    "No mods found that need processing.\n\n"
                    "Mods are skipped if:\n"
                    "• They don't have a 'textures' folder\n"
                    "• They already have a 'pbr' folder\n"
                    "• Diffuse and normal names do not match\n"
                    "• Output already exists")
            else:
                QMessageBox.information(self, "Scan Complete", 
                    f"Found {len(mods)} mods to process.\n\n"
                    "Click 'Start Processing' to begin.")
                
        except Exception as e:
            self.logger.error(f"Error scanning mods: {e}")
            QMessageBox.critical(self, "Error", f"Error scanning mods:\n{e}")
    
    def start_processing(self):
        """Start the processing worker thread."""
        if not self.validate_settings():
            return
        
        # Get mods count
        temp_worker = ProcessorWorker(self.settings, self.logger)
        mods = temp_worker.get_mods_to_process()
        
        if len(mods) == 0:
            QMessageBox.information(self, "No Mods", "No mods found to process.")
            return
        
        # Confirm
        reply = QMessageBox.question(self, "Confirm Processing",
            f"Ready to process {len(mods)} mods.\n\n"
            f"Source: {self.settings.mods_directory}\n"
            f"Output: {self.settings.output_directory}\n\n"
            "Continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        # Save settings
        self.settings.save(self.config_path)
        
        # Update UI
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.scan_btn.setEnabled(False)
        self.status_label.setText("● Processing...")
        self.status_label.setStyleSheet("color: #4fc1ff; font-weight: bold;")
        
        # Reset progress
        self.overall_progress.setMaximum(len(mods))
        self.overall_progress.setValue(0)
        self.mod_progress.setValue(0)
        self.mod_progress.setMaximum(100)
        
        # Create and start worker
        self.worker = ProcessorWorker(self.settings, self.logger)
        self.worker.signals.progress.connect(self.on_progress)
        self.worker.signals.mod_progress.connect(self.on_mod_progress)
        self.worker.signals.finished.connect(self.on_finished)
        self.worker.signals.error.connect(self.on_error)
        self.worker.start()
    
    def stop_processing(self):
        """Stop the processing."""
        if self.worker:
            self.logger.warning("Stopping processing...")
            self.status_label.setText("● Stopping...")
            self.status_label.setStyleSheet("color: #d19a66; font-weight: bold;")
            self.worker.stop()
    
    def on_progress(self, current: int, total: int, mod_name: str):
        """Handle overall progress updates."""
        self.overall_progress.setMaximum(total)
        self.overall_progress.setValue(current)
        self.overall_label.setText(f"{current} / {total}")
        self.statusbar.showMessage(f"Processing: {mod_name}")
        self.mod_progress.setValue(0)
        self.mod_label.setText("0 / 0")
    
    def on_mod_progress(self, current: int, total: int):
        """Handle current mod progress updates."""
        self.mod_progress.setMaximum(total)
        self.mod_progress.setValue(current)
        self.mod_label.setText(f"{current} / {total}")
    
    def on_finished(self, stats: ProcessingStats):
        """Handle processing completion."""
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.scan_btn.setEnabled(True)
        
        if self.worker and self.worker.should_stop:
            self.status_label.setText("● Stopped by user")
            self.status_label.setStyleSheet("color: #d19a66; font-weight: bold;")
            self.statusbar.showMessage("Processing stopped.")
        else:
            self.status_label.setText("● Complete!")
            self.status_label.setStyleSheet("color: #4ec9b0; font-weight: bold;")
            self.statusbar.showMessage(f"Complete! Processed {stats.processed_mods} mods in {stats.get_duration()}.")
        
        # Show summary
        QMessageBox.information(self, "Processing Complete",
            f"Processing finished!\n\n"
            f"Duration: {stats.get_duration()}\n"
            f"Mods processed: {stats.processed_mods}\n"
            f"Mods skipped: {stats.skipped_mods}\n"
            f"Mods failed: {stats.failed_mods}\n"
            f"Files renamed: {stats.renamed_files}\n"
            f"Textures processed: {stats.processed_textures}")
        
        self.worker = None
    
    def on_error(self, error_msg: str):
        """Handle processing errors."""
        QMessageBox.critical(self, "Processing Error", f"An error occurred:\n{error_msg}")
    
    def closeEvent(self, event):
        """Handle window close event."""
        if self.worker and self.worker.isRunning():
            reply = QMessageBox.question(self, "Quit",
                "Processing is still running.\nAre you sure you want to quit?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
            
            if reply == QMessageBox.StandardButton.Yes:
                self.worker.stop()
                self.worker.wait(3000)  # Wait up to 3 seconds
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    # Check Python version
    if sys.version_info < PYTHON_MIN_VERSION:
        print(f"This application requires Python {PYTHON_MIN_VERSION[0]}.{PYTHON_MIN_VERSION[1]} or higher.")
        print(f"Current version: {sys.version_info.major}.{sys.version_info.minor}")
        sys.exit(1)
    
    # Create application
    app = QApplication(sys.argv)
    app.setStyle("Fusion")  # Use Fusion style for consistent look
    
    # Apply dark stylesheet
    app.setStyleSheet(DARK_STYLESHEET)
    
    # Create and show window
    window = PBRifyWindow()
    window.show()
    
    # Run application
    sys.exit(app.exec())


if __name__ == '__main__':
    main()