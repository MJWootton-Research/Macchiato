import os
import subprocess

def render(source, formats):
    for f in formats:
        assert source[-4:].lower() == ".dot"
        format = f.lower()
        subprocess.call('dot "%s" -T %s -O' % (source, format), shell=True)
        os.rename('%s.%s' % (source, format), '%s.%s' % (source[:-4], format))

def main():
    pass

if __name__ == '__main__':
    main()
