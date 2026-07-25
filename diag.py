import sys, subprocess, shutil, os

print('sys.executable:', sys.executable)
print('sys.version:', sys.version)

def run_cmd(cmd):
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=10, shell=False)
        print('\nCMD:', cmd)
        print('returncode:', p.returncode)
        print('stdout:', p.stdout)
        print('stderr:', p.stderr)
    except FileNotFoundError as e:
        print('\nFileNotFoundError for', cmd, e)
    except Exception as e:
        print('\nError for', cmd, e)

run_cmd([sys.executable, '-c', "print('hello from python')"])
run_cmd(['bash', '-lc', 'echo hello from bash'])
run_cmd(['adb', 'version'])
run_cmd(['adb', 'devices'])
