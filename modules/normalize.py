from .utils import readNgramsAsDict, segmentIntoTwoWords, getStandardized
from .utils import P, Pint, logP

import logging
FORMAT="%(asctime)s %(levelname)s %(message)s"
logging.basicConfig (format=FORMAT, level=logging.INFO)

class NGramsNormalizer (object):
	def __init__ (self, unigrams, bigrams, trigrams):
		self.g1 = unigrams
		self.g2 = bigrams
		self.g3 = trigrams

		self.n1 = sum(self.g1.values())
		self.n2 = sum(self.g2.values())
		self.n3 = sum(self.g3.values())

	@classmethod
	def fromFiles (cls, unigrams_file, bigrams_file, trigrams_file, verbose=False):
		g1 = readNgramsAsDict (unigrams_file)
		if verbose: logging.info ("Unigrams loaded")
		g2 = readNgramsAsDict (bigrams_file)
		if verbose: logging.info ("Bigrams loaded")
		g3 = readNgramsAsDict (trigrams_file)
		if verbose: logging.info ("Trigrams loaded")
		return NGramsNormalizer (g1, g2, g3)

	def byLikelihoodRatio (self, token, smoothing=1, threshold=1):
		V = len (self.g1)

		denom = P(self.g1[(token,)], self.n1, V, s=smoothing)
		ratios = [(c1,c2,P(self.g2[(c1,c2)], self.n2, V*V, s=smoothing)/denom)
				  for c1,c2 in segmentIntoTwoWords (token)]

		return getStandardized (ratios, token, threshold=threshold)

	def byContextualLikelihoodRatio (self, token, left_context, right_context, interpolation=False, bigram_lambdas=(0.9,0.1), trigram_lambdas=(0.7,0.2,0.1), smoothing=1, threshold=1):
		def getNumLRNonInterpolated (lc, c1, c2, rc, lenV, smoothing):
			num = P(self.g3[(c1,c2,rc)], self.g2[(c1,c2)], lenV, s=smoothing) * P(self.g3[(lc,c1,c2)], self.g2[(lc,c1)], lenV, s=smoothing) * P(self.g2[(lc,c1)], self.g1[(lc,)], lenV, s=smoothing)
			return num

		def getDenomLRNonInterpolated (lc, t, rc, lenV, smoothing):
			denom = P(self.g3[(lc, t, rc)], self.g2[(lc,t)], lenV, s=smoothing) * P(self.g2[(lc, t)], self.g1[(lc,)], lenV, s=smoothing)
			return denom

		def getNumLRInterpolated (lc, c1, c2, rc, lenV, smoothing, bigram_lambdas, trigram_lambdas):
			num = Pint([P(self.g3[(c1,c2,rc)], self.g2[(c1,c2)], lenV, s=smoothing), P(self.g2[(c2,rc)], self.g1[(c2,)], lenV, s=smoothing), P(self.g1[(rc,)], self.n1, lenV, s=smoothing)], trigram_lambdas) * Pint([P(self.g3[(lc,c1,c2)], self.g2[(lc,c1)], lenV, s=smoothing), P(self.g2[(c1,c2)], self.g1[(c1,)], lenV, s=smoothing), P(self.g1[(c2,)], self.n1, lenV, s=smoothing)], trigram_lambdas) * Pint([P(self.g2[(lc,c1)], self.g1[(lc,)], lenV, s=smoothing), P(self.g1[(c1,)], self.n1, lenV, s=smoothing)], bigram_lambdas)
			return num

		def getDenomLRInterpolated (lc, t, rc, lenV, smoothing, bigram_lambdas, trigram_lambdas):
			denom = Pint([P(self.g3[(lc, t, rc)], self.g2[(lc,t)], lenV, s=smoothing), P(self.g2[(t, rc)], self.g1[(t,)], lenV, s=smoothing), P(self.g1[(rc,)], self.n1, lenV, s=smoothing)], trigram_lambdas) * Pint([P(self.g2[(lc, t)], self.g1[(lc,)], lenV, s=smoothing), P(self.g1[(t,)], self.n1, lenV, s=smoothing)], bigram_lambdas)
			return denom

		V = len (self.g1)

		if not interpolation:
			denom = getDenomLRNonInterpolated (left_context, token, right_context, V, smoothing)
			ratios = [(c1, c2, getNumLRNonInterpolated (left_context, c1, c2, right_context, V, smoothing)/denom) 
					   for c1,c2 in segmentIntoTwoWords (token)]
		else:
			denom = getDenomLRInterpolated (left_context, token, right_context, V, smoothing, bigram_lambdas, trigram_lambdas)
			ratios = [(c1, c2, getNumLRInterpolated (left_context, c1, c2, right_context, V, smoothing, bigram_lambdas, trigram_lambdas)/denom)
					  for c1,c2 in segmentIntoTwoWords (token)]
		
		return getStandardized (ratios, token, threshold=threshold)
