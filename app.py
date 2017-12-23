import sys
from kt_ocr.process import main

if __name__ == '__main__':
    main(quiet="-q" in sys.argv[1:], force="-f" in sys.argv[1:])
