# pcgp_tools/archiver.py
import shutil
from pathlib import Path
import datetime

class PCGPArchiver:
    def archive_old_files(self):
        print("?? �A�[�J�C�u�����J�n")
        archive_dir = Path("archive/misc")
        archive_dir.mkdir(parents=True, exist_ok=True)

        ARCHIVE_FILES = ["structure.txt", "filelist.txt"]
        for fname in ARCHIVE_FILES:
            f = Path(fname)
            if f.exists():
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                target = archive_dir / f"{timestamp}_{fname}"
                shutil.move(str(f), str(target))
                print(f"? {fname} -> archive/misc/")
        print("?? �A�[�J�C�u��������\n")
