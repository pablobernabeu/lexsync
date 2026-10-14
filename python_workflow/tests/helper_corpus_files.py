"""Corpus files in the layouts lexsync's registry describes, with the lexicon each
normalises to.

R_workflow/tests/testthat/helper-corpus-files.R holds the same text, escape for escape,
so the two engines are held to one expected file. The Zipf values below were worked out
by hand from Zipf = log10(per million) + 3, rounded to three places, and each lies at
least 0.016 of a thousandth from a rounding boundary, so no engine's log10 can move it.
"""

# SUBTLEX-US as openlexicon serves it: tab-separated, the rate per million in SUBTLWF,
# and Lg10WF, which is log10(count + 1) and not a Zipf value.
SUBTLEX_US = (
    "Word\tFREQcount\tCDcount\tFREQlow\tCdlow\tSUBTLWF\tLg10WF\tSUBTLCD\tLg10CD\t"
    "Dom_PoS_SUBTLEX\n"
    "the\t1501908\t8388\t1339811\t8388\t29449.18\t6.1766\t100\t3.9237\tArticle\n"
    "You\t2134713\t8381\t2012\t62\t41857.12\t6.3293\t99.92\t3.9234\tPronoun\n"
    "dog\t9831\t2433\t9478\t2379\t192.76\t3.9926\t29.01\t3.3863\tNoun\n"
    "Cat\t3591\t1340\t3313\t1279\t70.41\t3.5553\t15.98\t3.1274\tNoun\n"
    "zebra\t94\t62\t91\t59\t1.84\t1.9777\t0.74\t1.7993\tNoun\n")
SUBTLEX_US_MAP = {"word": "Word", "freq_permillion": "SUBTLWF", "pos": "Dom_PoS_SUBTLEX"}
SUBTLEX_US_LEXICON = (
    "word,freq_zipf,freq_permillion,pos\n"
    "cat,4.848,70.41,Noun\n"
    "dog,5.285,192.76,Noun\n"
    "the,7.469,29449.18,Article\n"
    "you,7.622,41857.12,Pronoun\n"
    "zebra,3.265,1.84,Noun\n")

# A comma-separated table with a FreqPerMillion column, as SUBTLEX-ESP has, holding a
# capital, a decomposed e-acute and two words outside ASCII.
PER_MILLION = (
    "Word,FreqPerMillion\n"
    "de,41000.5\n"
    "Niño,120.33\n"
    "café,15.2\n"
    "árbol,30.07\n")
PER_MILLION_MAP = {"word": "Word", "freq_permillion": "FreqPerMillion"}
PER_MILLION_LEXICON = (
    "word,freq_zipf,freq_permillion\n"
    "café,4.182,15.2\n"
    "de,7.613,41000.5\n"
    "niño,5.08,120.33\n"
    "árbol,4.478,30.07\n")

# A tab-separated word list already on the Zipf scale, saved with a byte-order mark and
# a name whose extension says nothing of the delimiter.
TAB_ZIPF = "﻿word\tfreq_zipf\nHello\t5.12\nworld\t4.98\n"
TAB_ZIPF_LEXICON = "word,freq_zipf\nhello,5.12\nworld,4.98\n"

# Lexique 3.83 gives a homograph one row per lemma and category, and splits the form's
# frequency between them (New et al., Manuel de Lexique 3, freqfilms2).
LEXIQUE = (
    "ortho\tphon\tlemme\tcgram\tfreqfilms2\n"
    "danse\td@s\tdanse\tNOM\t38.62\n"
    "danse\td@s\tdanser\tVER\t18.46\n"
    "dansent\td@s\tdanser\tVER\t3.14\n"
    "dansé\td@se\tdanser\tVER\t5.27\n")
LEXIQUE_ENTRY = {"columns": {"word": "ortho", "freq_permillion": "freqfilms2"},
                 "duplicates": "sum"}
LEXIQUE_SUM = (
    "word,freq_zipf,freq_permillion\n"
    "danse,4.756,57.08\n"
    "dansent,3.497,3.14\n"
    "dansé,3.722,5.27\n")
LEXIQUE_FIRST = (
    "word,freq_zipf,freq_permillion\n"
    "danse,4.587,38.62\n"
    "dansent,3.497,3.14\n"
    "dansé,3.722,5.27\n")

# log10 of this rate plus 3, scaled by 1000, falls within 1e-12 of 3000.5, so an
# engine whose log10 differed in the last place could round it to 3.001 where another
# gives 3.
NEAR_BOUNDARY = "word,freq_permillion\nedge,1.0011519555381685\n"
