# pcgp_manager.py
from pcgp_tools.validator import PCGPValidator
from pcgp_tools.repairer import PCGPRepairer
from pcgp_tools.archiver import PCGPArchiver
import sys

def main():
    print("=== Libral Core PCGP �����O���[�~���O�J�n ===")
    
    # 1. Validator: �\���`�F�b�N (��肠��Α���~)
    validator = PCGPValidator()
    if not validator.check_initial_state():
        print("? �v���I�ȏ�����Ԃ̌���: �����𒆒f���܂��B")
        sys.exit(1)

    # 2. Repairer: �\�������ƃt�@�C���ړ�
    try:
        r = PCGPRepairer()
        r.create_pcgp_directories()
        r.enforce_structure()
        r.enforce_large_folders()
    except Exception as e:
        print(f"? �v���I�ȏC���G���[: {e}")
        sys.exit(1)

    # 3. Archiver: �Â��t�@�C�����A�[�J�C�u
    PCGPArchiver().archive_old_files()

    print("=== PCGP �����O���[�~���O����: Git �R�~�b�g�̏������� ===")
    print("?? Git�p�l���ɖ߂�A�S�Ă̕ύX���R�~�b�g���v�b�V�����Ă��������B")

if __name__ == "__main__":
    main()
