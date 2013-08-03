#!/usr/bin/env python

import itertools
import nltk
from nltk.corpus import stopwords
import string
import re

stop_words = stopwords.words('english')

LOWER_BOUND = .20 #The low end of shared words to consider
UPPER_BOUND = .90 #The high end, since anything above this is probably SEO garbage or a duplicate sentence

def is_unimportant(word):
    """Decides if a word is ok to toss out for the sentence comparisons"""
    return word in ['.', '!', ',', ] or '\'' in word or word in stop_words

def only_important(sent):
    """Just a little wrapper to filter on is_unimportant"""
    return filter(lambda w: not is_unimportant(w), sent)

def compare_sents(sent1, sent2):
    """Compare two word-tokenized sentences for shared words"""
    if not len(sent1) or not len(sent2):
        return 0
    return len(set(only_important(sent1)) & set(only_important(sent2))) / ((len(sent1) + len(sent2)) / 2.0)

def compare_sents_bounded(sent1, sent2):
    """If the result of compare_sents is not between LOWER_BOUND and
    UPPER_BOUND, it returns 0 instead, so outliers don't mess with the sum"""
    cmpd = compare_sents(sent1, sent2)
    if cmpd <= LOWER_BOUND or cmpd >= UPPER_BOUND:
        return 0
    return cmpd

def compute_score(sent, sents):
    """Computes the average score of sent vs the other sentences (the result of
    sent vs itself isn't counted because it's 1, and that's above
    UPPER_BOUND)"""
    if not len(sent):
        return 0
    return sum( compare_sents_bounded(sent, sent1) for sent1 in sents ) / float(len(sents))

def summarize_block(block):
    """Return the sentence that best summarizes block"""
    sents = nltk.sent_tokenize(block)
    word_sents = map(nltk.word_tokenize, sents)
    d = dict( (compute_score(word_sent, word_sents), sent) for sent, word_sent in zip(sents, word_sents) )
    return d[max(d.keys())]

def find_likely_body(b):
    """Find the tag with the most directly-descended <p> tags"""
    return max(b.find_all(), key=lambda t: len(t.find_all('p', recursive=False)))

class Summary(object):
    def __init__(self, url, article_html, title, summaries):
        self.url = url
        self.article_html = article_html
        self.title = title
        self.summaries = summaries

    def __repr__(self):
        return 'Summary({0}, {1}, {2}, {3}, {4})'.format(
            repr(self.url), repr(self.article_html), repr(self.title), repr(summaries)
        )

    def __str__(self):
        return "{0} - {1}\n\n{2}".format(self.title, self.url, '\n'.join(self.summaries))

def summarize_page(content):
    blocks= [c.strip() for c in content.split('\n') if len([x for x in c.strip().split(' ') if len(x) > 2]) > 4]
    summaries = map(lambda p: re.sub('\s+', ' ', summarize_block(p)).strip(), blocks)
    summaries = sorted(set(summaries), key=summaries.index) #dedpulicate and preserve order
    summaries = [ re.sub('\s+', ' ', summary.strip()) for summary in summaries if filter(lambda c: c.lower() in string.letters, summary) ]
    return summaries

if __name__ == '__main__':
    import sys
    body = '''The wait for a diesel Honda has been a long one. The company's first such car, the Amaze, which was launched on Thursday in India, may be coming four years late, if not more. Arguably, Honda has the best petrol cars, but the lack of diesel options has cost it dear, particularly in the last 2 years when the market switched fuels rather abruptly. 

Clutter breaking designLooking from the front, this car is unmistakably a Brio. The few alterations - a twin chrome line on the grille, for instance, and a bigger air dam - are cosmetic. The pear shaped headlamps are the same, the overall stance and demeanour identical. But the Brio is good-looking. So the Amaze too looks sharp and chiselled with strong lines. 
The rear is where most of the artistry has happened. The boot flows with the body, and though the Amaze is a sub-4 metre vehicle (to qualify for lower duties), neither does the boot look an after-thought, nor does it look as if it has been mercilessly hacked for the taxman's benefit.
Cosy interiorsThe interiors of the car are simplistic, with the focus on functionality than style. The dashboard and instrument panel are exactly the same as the Brio. While the fit and finish are good and quality is par for the course, one has to own up that the interior of the Dzire is more inspiring.  The Amaze's strong point is the space. Thanks to a very light and small diesel engine, the amount of space that Honda has managed to eke out at the back is clearly the benchmark for sub-4 metre sedans. 

The only other car that offers better leg-room is the Etios - which is not a sub-4 metre. The Amaze also has a much bigger boot - 400 litres to the Dzire's puny 316 - which makes it more suited for those weekend family outings. 

PerformanceThe car is powered by a 1.5-litre iDtec 4-cylinder diesel engine that has been developed "in-house" over the last four years. The petrol variant has the standard 1.2-litre iVtec engine that does duty on the Brio. The perceptible changes from the Brio include a heavier steering and a stiffer suspension, in line with a heaver and bigger car. 
The result is that the petrol car feels under-powered - just as all other truncated cars in the segment do. Only the Etios, with a proper 1.5-litre powertrain, feels adequate, both on paper and on the road. 
The diesel Honda would naturally be more in demand, and under greater scrutiny. On paper it is the most powerful, and also has more torque. In fact, that reflects on the road as well. It takes off well from as low as 1,200 RPM, making it a hassle free drive in city conditions. The mid-range is robust, so cruising on the highway will not be a problem either. On the downside, it is a wee bit noisy and has a fair bit of harshness. The headline grabbing figure would be the fuel economy of 25.8 kmpl, the most in a passenger car in the country. The claim may be a little over the top, but even when we pressed it to the hilt, it gave us nearly 18km per litre. Automotive Scrabble
VerdictIt will not be out of place to say that Honda has done with the Amaze exactly what we hoped the Toyota would do with the Etios two years ago - give the Maruti Dzire a real taste of competition. But while Toyota tried to create a whole new identity (and hence failed), Honda has only carried forward its legacy. The Amaze is impressive enough. It has space, quality, fuel economy, technology - and a premium branding courtesy the H badge. 
To top all that, it comes at a jaw dropping and un-Honda like price that mirrors the Dzire. Like in the case of the Etios, the expectation had been that Honda would price the Amaze higher to keep the premium image. Clearly, they have learnt from its competitors' mistakes. With so much going for it, it is difficult to not hedge one's bets on this one. The counter punch may be a tad late, but it is lethal. Honda is back in business.
    '''
    import json
    body = sys.argv[1]

    print json.dumps(summarize_page(body))