import os
import sys
import glob
import subprocess

def render(source, formats):
    for f in formats:
        assert source[-4:].lower() == ".dot"
        format = f.lower()
        subprocess.call('dot "%s" -T %s -O' % (source, format), shell=True)
        os.rename('%s.%s' % (source, format), '%s.%s' % (source[:-4], format))

def main():
    os.chdir(os.path.join(sys.argv[1]))
    if len(sys.argv) > 2:
        formats = sys.argv[2:]
    else:
        sys.exit("\nCannot produce images. No file formats specifed.\n")
    for dFile in glob.glob1(os.path.join(os.getcwd(), sys.argv[1]),"*.dot"):
        render(dFile, formats)

if __name__ == '__main__':
    main()
