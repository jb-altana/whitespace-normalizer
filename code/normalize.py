from utils import readNgramsFromDict, segmentIntoTwoWords, getStandardized
from utils import P, Pint, logP

class NGramsNormalizer (object):
	def __init__ (self, unigrams, bigrams, trigrams):
		self.g1 = unigrams
		self.g2 = bigrams
		self.g3 = trigrams

		self.n1 = sum(self.g1.values())
		self.n2 = sum(self.g2.values())
		self.n3 = sum(self.g3.values())

	@classmethod
	def fromFiles (cls, unigrams_file, bigrams_file, trigrams_file):
		g1 = readNgramsFromDict (unigrams_file)
		g2 = readNgramsFromDict (bigrams_file)
		g3 = readNgramsFromDict (trigrams_file)
		return NGramsNormalizer (g1, g2, g3)

	def byLikelihoodRatio (self, token, smoothing=1, threshold=1):
		V = len (self.g1)
		subs = list ()

		denom = P(self.g1[(token,)], self.n1, V, s=smoothing)
		ratios = [(c1,c2,P(self.g2[(c1,c2)], self.n2, V*V, s=smoothing)/denom)
				  for c1,c2 in segmentIntoTwoWords (token)]

		return getStandardized (ratios, token, threshold=threshold)

	def byContextualLikelihoodRatio (self, token, left_context, right_context, interpolation=False):
		pass
