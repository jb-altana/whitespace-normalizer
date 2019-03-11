import argparse
import glob
import sys
import os
import logging
import errno
import json

if "../" not in sys.path: sys.path.append ("../")

from modules import utils
from modules.normalize import NGramsNormalizer

FORMAT="%(asctime)s %(levelname)s %(message)s"
logging.basicConfig(format=FORMAT, level=logging.INFO)

def getArgs ():
	parser = argparse.ArgumentParser ()
	parser.add_argument ("--srcdir", required=True, help="directory containing input files")
	parser.add_argument ("--tgtdir", required=True, help="directory containing corrected output files")
	parser.add_argument ("--gramfiles", nargs="+", required=True, help="files containing the dictionaries")
	parser.add_argument ("--debugfile", required=False, dest="debugfile", action="store", default="summary.jsonl", help="file in which summary statistics per file are added")
	
	return parser.parse_args ()

# Taken from https://stackoverflow.com/a/600612/119527
def mkdir_p(path):
	try:
		os.makedirs(path, exist_ok=True)
	except OSError as exc: # Python >2.5
		if exc.errno == errno.EEXIST and os.path.isdir(path):
			pass
		else: raise

# Taken from https://stackoverflow.com/a/23794010
def safe_open_w(path):
	""" Open "path" for writing, creating any parent directories as needed.
	"""
	mkdir_p(os.path.dirname(path))
	return open(path, 'w')

def correctText (text, grams):
	tokens = [token for token in text.split ()]
	corrected_text = " ".join (tokens)
	return corrected_text 

def main ():
	args = getArgs ()
	os.makedirs (args.tgtdir, exist_ok=True)
	gramfiles = args.gramfiles

	grams = NGramsNormalizer.fromFiles (gramfiles[0],
										gramfiles[1],
										gramfiles[2],
										verbose=True)	
	
	logging.info ("Begin processing files in {0}".format (args.srcdir))
	nFiles = 0
	with open (args.debugfile, "w") as dout:
		for srcsubdir, dirs , files in os.walk (args.srcdir):
			if len (dirs) > 0: continue
			tgtsubdir = os.path.join (args.tgtdir, os.path.relpath(srcsubdir, start=args.srcdir))
			for filename in files:
				with open (os.path.join (srcsubdir, filename), encoding="utf-8", errors="ignore") as fin:
					text = fin.read()

				corrected_text, debug_dict = grams.normalizeText (text, contextual=True, interpolation=True, debug=True, smoothing=0.1, threshold=1)
				debug_dict["filename"] = os.path.join (srcsubdir, filename)
				with safe_open_w (os.path.join (tgtsubdir, filename)) as fout:
					fout.write (corrected_text + "\n")	

				dout.write ("{0}\n".format (json.dumps(debug_dict)))

			logging.info ("Finished processing {1} files in {0}".format (srcsubdir, len (files)))
			nFiles += len (files)
			

	logging.info ("Finished processing all {1} files in {0}".format (args.srcdir, nFiles))
if __name__ == "__main__":
	main ()
