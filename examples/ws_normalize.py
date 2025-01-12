import argparse
import glob
import sys
import os
import logging
import errno
import json

if "../" not in sys.path:
    sys.path.append("../")
from modules import utils
from modules.normalize import NGramsNormalizer

FORMAT = "%(asctime)s %(levelname)s %(message)s"
logging.basicConfig(format=FORMAT, level=logging.INFO)


def getArgs():
    parser = argparse.ArgumentParser()
    parser.add_argument("--srcdir", required=True, help="directory containing input files")
    parser.add_argument("--tgtdir", required=True, help="directory containing corrected output files")
    parser.add_argument("--gramfiles", nargs="+", required=True, help="files containing the dictionaries")
    parser.add_argument("--keepfile", required=False, default=None, help="file contains words that should not split")
    parser.add_argument(
        "--debugfile",
        required=False,
        dest="debugfile",
        action="store",
        default="summary.jsonl",
        help="file in which summary statistics per file are added",
    )
    return parser.parse_args()


# Taken from https://stackoverflow.com/a/600612/119527
def mkdir_p(path):
    try:
        os.makedirs(path, exist_ok=True)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


# Taken from https://stackoverflow.com/a/23794010
def safe_open_w(path):
    """Open "path" for writing, creating any parent directories as needed."""
    mkdir_p(os.path.dirname(path))
    return open(path, "w")


def correctText(text, grams):
    tokens = [token for token in text.split()]
    corrected_text = " ".join(tokens)
    return corrected_text


def main():
    args = getArgs()
    os.makedirs(args.tgtdir, exist_ok=True)
    gramfiles = args.gramfiles
    grams = NGramsNormalizer.fromFiles(gramfiles[0], gramfiles[1], gramfiles[2], verbose=True)
    logging.info(f"Begin processing files in {args.srcdir}")
    keep_words = set()
    if args.keepfile is not None:
        with open(args.keepfile) as fin:
            for line in fin:
                parts = line.strip().split(",")
                keep_words.add(parts[0])
    nFiles = 0
    with open(args.debugfile, "w") as dout:
        for srcsubdir, dirs, files in os.walk(args.srcdir):
            if len(dirs) > 0:
                continue
            tgtsubdir = os.path.join(args.tgtdir, os.path.relpath(srcsubdir, start=args.srcdir))
            for filename in files:
                with open(os.path.join(srcsubdir, filename), encoding="utf-8", errors="ignore") as fin:
                    text = fin.read()
                corrected_text, debug_dict = grams.normalizeText(
                    text, keep_words=keep_words, contextual=True, interpolation=True, debug=True, smoothing=0.1, threshold=1
                )
                debug_dict["filename"] = os.path.join(srcsubdir, filename)
                with safe_open_w(os.path.join(tgtsubdir, filename)) as fout:
                    fout.write(corrected_text + "\n")
                dout.write(f"{json.dumps(debug_dict)}\n")
            logging.info(f"Finished processing {len(files)} files in {srcsubdir}")
            nFiles += len(files)
    logging.info(f"Finished processing all {nFiles} files in {args.srcdir}")


if __name__ == "__main__":
    main()
