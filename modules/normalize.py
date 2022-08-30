"""Implementation of an NGramsNormalizer"""
from .utils import readNgramsAsDict, segmentIntoTwoWords, getStandardized
from .utils import P, Pint
import logging

FORMAT = "%(asctime)s %(levelname)s %(message)s"
logging.basicConfig(format=FORMAT, level=logging.INFO)

logger = logging.getLogger(__name__)

class NGramsNormalizer:
    """Implementation of an NGramsNormalizer"""
    def __init__(self, unigrams, bigrams, trigrams):
        self.g1 = unigrams
        self.g2 = bigrams
        self.g3 = trigrams
        self.n1 = sum(self.g1.values())
        self.n2 = sum(self.g2.values())
        self.n3 = sum(self.g3.values())

    @classmethod
    def fromFiles(cls, unigrams_file, bigrams_file, trigrams_file, verbose=False):
        g1 = readNgramsAsDict(unigrams_file)
        before_level = logger.getEffectiveLevel()
        if verbose:
            logger.setLevel(logging.INFO)
        logger.info("Unigrams loaded")
        g2 = readNgramsAsDict(bigrams_file)
        logger.info("Bigrams loaded")
        g3 = readNgramsAsDict(trigrams_file)
        logger.info("Trigrams loaded")
        logger.setLevel(before_level)
        return NGramsNormalizer(g1, g2, g3)

    def byLikelihoodRatio(self, token, smoothing=1, threshold=1, return_ratio=False):
        V = len(self.g1)
        denom = P(self.g1[(token,)], self.n1, V, s=smoothing)
        ratios = [(c1, c2, P(self.g2[(c1, c2)], self.n2, V * V, s=smoothing) / denom) for c1, c2 in segmentIntoTwoWords(token)]
        return getStandardized(ratios, token, threshold=threshold, return_ratio=return_ratio)

    def byContextualLikelihoodRatio(
        self,
        token,
        left_context,
        right_context,
        interpolation=False,
        bigram_lambdas=(0.9, 0.1),
        trigram_lambdas=(0.7, 0.2, 0.1),
        smoothing=1,
        threshold=1,
    ):
        def getNumLRNonInterpolated(lc, c1, c2, rc, lenV, smoothing):
            num = (
                P(self.g3[(c1, c2, rc)], self.g2[(c1, c2)], lenV, s=smoothing)
                * P(self.g3[(lc, c1, c2)], self.g2[(lc, c1)], lenV, s=smoothing)
                * P(self.g2[(lc, c1)], self.g1[(lc,)], lenV, s=smoothing)
            )
            return num

        def getDenomLRNonInterpolated(lc, t, rc, lenV, smoothing):
            denom = P(self.g3[(lc, t, rc)], self.g2[(lc, t)], lenV, s=smoothing) * P(
                self.g2[(lc, t)], self.g1[(lc,)], lenV, s=smoothing
            )
            return denom

        def getNumLRInterpolated(lc, c1, c2, rc, lenV, smoothing, bigram_lambdas, trigram_lambdas):
            num = (
                Pint(
                    [
                        P(self.g3[(c1, c2, rc)], self.g2[(c1, c2)], lenV, s=smoothing),
                        P(self.g2[(c2, rc)], self.g1[(c2,)], lenV, s=smoothing),
                        P(self.g1[(rc,)], self.n1, lenV, s=smoothing),
                    ],
                    trigram_lambdas,
                )
                * Pint(
                    [
                        P(self.g3[(lc, c1, c2)], self.g2[(lc, c1)], lenV, s=smoothing),
                        P(self.g2[(c1, c2)], self.g1[(c1,)], lenV, s=smoothing),
                        P(self.g1[(c2,)], self.n1, lenV, s=smoothing),
                    ],
                    trigram_lambdas,
                )
                * Pint(
                    [P(self.g2[(lc, c1)], self.g1[(lc,)], lenV, s=smoothing), P(self.g1[(c1,)], self.n1, lenV, s=smoothing)],
                    bigram_lambdas,
                )
            )
            return num

        def getDenomLRInterpolated(lc, t, rc, lenV, smoothing, bigram_lambdas, trigram_lambdas):
            denom = Pint(
                [
                    P(self.g3[(lc, t, rc)], self.g2[(lc, t)], lenV, s=smoothing),
                    P(self.g2[(t, rc)], self.g1[(t,)], lenV, s=smoothing),
                    P(self.g1[(rc,)], self.n1, lenV, s=smoothing),
                ],
                trigram_lambdas,
            ) * Pint(
                [P(self.g2[(lc, t)], self.g1[(lc,)], lenV, s=smoothing), P(self.g1[(t,)], self.n1, lenV, s=smoothing)],
                bigram_lambdas,
            )
            return denom

        V = len(self.g1)
        if not interpolation:
            denom = getDenomLRNonInterpolated(left_context, token, right_context, V, smoothing)
            ratios = [
                (c1, c2, getNumLRNonInterpolated(left_context, c1, c2, right_context, V, smoothing) / denom)
                for c1, c2 in segmentIntoTwoWords(token)
            ]
        else:
            denom = getDenomLRInterpolated(left_context, token, right_context, V, smoothing, bigram_lambdas, trigram_lambdas)
            ratios = [
                (
                    c1,
                    c2,
                    getNumLRInterpolated(left_context, c1, c2, right_context, V, smoothing, bigram_lambdas, trigram_lambdas)
                    / denom,
                )
                for c1, c2 in segmentIntoTwoWords(token)
            ]
        return getStandardized(ratios, token, threshold=threshold)

    def normalizeText(
        self,
        text,
        keep_words={},
        contextual=False,
        interpolation=False,
        debug=False,
        bigram_lambdas=(0.9, 0.1),
        trigram_lambdas=(0.7, 0.2, 0.1),
        smoothing=1,
        threshold=1,
    ):
        tokens = [token for token in text.split()]
        corrected_tokens = list()
        debug_dict = {"ntokens": len(tokens), "corrected_tokens": [], "ncorrected": 0}
        if len(tokens) == 0:
            if debug:
                return " ".join(corrected_tokens), debug_dict
            else:
                return " ".join(corrected_tokens)
        if contextual:
            # no context on the left, so use non-contextual likleihood ratio
            if len(tokens) > 0:
                if len(keep_words) > 0 and tokens[0] in keep_words:
                    correct = tokens[0]
                else:
                    correct = self.byLikelihoodRatio(tokens[0], smoothing=smoothing, threshold=threshold)
                if correct != tokens[0]:
                    debug_dict["corrected_tokens"].append((tokens[0], correct))
                    debug_dict["ncorrected"] += 1
                corrected_tokens.extend(correct.split())
            # use context to both the left and the right
            for i in range(1, len(tokens) - 1):
                if not tokens[i].isalpha():
                    corrected_tokens.append(tokens[i])
                    continue
                if len(keep_words) > 0 and tokens[i] in keep_words:
                    corrected_tokens.append(tokens[i])
                    continue
                lc = corrected_tokens[-1]
                rc = tokens[i + 1]
                correct = self.byContextualLikelihoodRatio(
                    tokens[i],
                    lc,
                    rc,
                    interpolation=interpolation,
                    bigram_lambdas=bigram_lambdas,
                    trigram_lambdas=trigram_lambdas,
                    smoothing=smoothing,
                    threshold=threshold,
                )
                if correct != tokens[i]:
                    debug_dict["corrected_tokens"].append((tokens[i], correct))
                    debug_dict["ncorrected"] += 1
                corrected_tokens.extend(correct.split())
            # no context on the right, so use non-contextual likelihood ratio
            if len(keep_words) > 0 and tokens[-1] in keep_words:
                correct = tokens[-1]
            else:
                correct = self.byLikelihoodRatio(tokens[-1], smoothing=smoothing, threshold=threshold)
            if correct != tokens[-1]:
                debug_dict["corrected_tokens"].append((tokens[-1], correct))
                debug_dict["ncorrected"] += 1
            corrected_tokens.extend(correct.split())
        else:
            for token in tokens:
                if len(keep_words) > 0 and token in keep_words:
                    correct = token
                else:
                    correct = self.byLikelihoodRatio(token, smoothing=1, threshold=1)
                if correct != token:
                    debug_dict["corrected_tokens"].append((token, correct))
                    debug_dict["ncorrected"] += 1
                corrected_tokens.extend(correct.split())
        if debug:
            return " ".join(corrected_tokens), debug_dict
        else:
            return " ".join(corrected_tokens)
