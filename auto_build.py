#!/usr/bin/python
# Build this project automaticly.
import os
from pathlib import Path
import shutil
import mpy_cross

cwd = Path('.')

# check mpy-corss
assert not os.system('mpy-cross'), "mpy-cross not found!"

# backup source
shutil.copy(
    src = cwd / 'urouter',
    dst = cwd / 'urouter_bak'
)

# compile code
for file in (cwd / 'urouter').iterdir():
    file: Path

    if file.name == '__init__.py':
        continue
        # skip
    else:
        new_file: Path = (file.parent / (file.stem() + ".mpy"))

        cmd = f'mpy-cross -s {file.absolute()}'
        os.system(cmd)

        assert new_file.exists(), f"Compile Failed: {new_file}"
        os.remove(file)

# build dist
            
        
