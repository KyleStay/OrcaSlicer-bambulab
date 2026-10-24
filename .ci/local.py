import os,pathlib,platform,shutil,subprocess
from common import ROOT,Incomplete,main,need,need_tool,run

def profiles():run(['python3','scripts/orca_extra_profile_check.py'])
def locale():
    need_tool('msgfmt')
    for file in sorted((ROOT/'localization/i18n').glob('*/OrcaSlicer_*.po')):
        output=ROOT/'.ci/work/locales'/file.parent.name/'OrcaSlicer.mo';output.parent.mkdir(parents=True,exist_ok=True)
        run(['msgfmt','--check-format','-o',str(output),str(file)])
def shellcheck():
    need_tool('shellcheck')
    tracked=subprocess.check_output(['git','ls-files','-z'],cwd=ROOT).split(b'\0')
    files=[os.fsdecode(p) for p in tracked if p and (p.endswith(b'.sh') or (p.startswith(b'scripts/linux.d/') and not p.endswith(b'.md')))]
    run(['shellcheck',*sorted(files)])
def build_tests():
    need_tool('cmake');need_tool('ctest')
    build=ROOT/'.ci/work/native-build'
    run(['cmake','-S',str(ROOT),'-B',str(build),'-DCMAKE_BUILD_TYPE=Release','-DORCA_TOOLS=ON','-DBUILD_TESTS=ON'])
    run(['cmake','--build',str(build),'--target','OrcaSlicer','--config','Release'])
    run(['cmake','--build',str(build),'--target','libslic3r_tests','fff_print_tests','slic3rutils_tests','sla_print_tests','libnest2d_tests','--config','Release'])
    run(['ctest','--test-dir',str(build),'--output-on-failure','--no-tests=error'])
def validator():
    binary=os.environ.get('ORCA_PROFILE_VALIDATOR');fixtures=os.environ.get('ORCA_PROFILE_FIXTURE')
    need(binary and pathlib.Path(binary).is_file(),'Provide the prebuilt local Linux profile validator through ORCA_PROFILE_VALIDATOR')
    need(platform.system()=='Linux','The original prebuilt profile validator requires local Linux')
    need(fixtures and pathlib.Path(fixtures).is_dir(),'Provide a disposable profile tree including the custom preset fixture through ORCA_PROFILE_FIXTURE')
    run([binary,'-p',str(ROOT/'resources/profiles'),'-l','2'])
    run([binary,'-p',fixtures,'-l','2'])
def matrix():raise Incomplete('Full matrix remains required on local Ubuntu 22/24, Fedora 41, Windows/MSBuild/WSL2, macOS arm64/x86_64 and universal. Choose native lanes explicitly; see archived job matrix. No hosted fallback.')
main({'profiles':profiles,'locale':locale,'shellcheck':shellcheck,'build-tests':build_tests,'profile-validator':validator,'matrix':matrix},['profiles','locale','shellcheck','build-tests','profile-validator','matrix'])
