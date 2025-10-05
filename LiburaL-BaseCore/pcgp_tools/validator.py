# pcgp_tools/validator.py
from pathlib import Path

class PCGPValidator:
    REQUIRED_ROOT_FILES = ["pyproject.toml", "package.json", "main.py", "docker-compose.yml"]

    def check_initial_state(self):
        print("?? �\���`�F�b�N�J�n: �K�{�t�@�C���̑��݊m�F")
        all_found = True
        for f in self.REQUIRED_ROOT_FILES:
            if not Path(f).exists():
                print(f"? ����: {f} �����[�g�Ɍ�����܂���B")
                all_found = False
            else:
                print(f"? ���݊m�F: {f}")
        if not all_found:
            print("?? �`�F�b�N���s: �����𒆒f���܂��B")
        else:
            print("?? �`�F�b�N����: ������Ԃ͐���ł��B")
        return all_found
