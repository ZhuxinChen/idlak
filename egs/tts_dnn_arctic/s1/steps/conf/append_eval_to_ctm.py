#!/bin/env python

# Copyright 2015  Brno University of Technology (author: Karel Vesely)
# Apache 2.0

import sys,operator

# Append Levenshtein alignment of 'hypothesis' and 'reference' into 'CTM':
# (i.e. the output of 'align-text' post-processed by 'wer_per_utt_details.pl')

# The tags in the appended column are:
#  'C' = correct
#  'S' = substitution
#  'I' = insertion
#  'U' = unknown (not part of scored segment)

if len(sys.argv) != 4:
  print 'Usage: %s eval-in ctm-in ctm-eval-out' % __file__
  sys.exit(1)
dummy, eval_in, ctm_in, ctm_eval_out = sys.argv

if ctm_eval_out == '-': ctm_eval_out = '/dev/stdout'

# Read the evalutation,
eval_vec = dict()
with open(eval_in, 'r') as f:
  while True:
    # Reading 4 lines encoding one utterance,
    ref = f.readline()
    hyp = f.readline()
    op = f.readline()
    csid = f.readline()
    if not ref: break
    # Parse the input,
    utt,tag,hyp_vec = hyp.split(' ',2)
    assert(tag == 'hyp')
    utt,tag,op_vec = op.split(' ',2)
    assert(tag == 'op')
    hyp_vec = hyp_vec.split()
    op_vec = op_vec.split()
    # Fill create eval vector with symbols 'C', 'S', 'I',
    assert(utt not in eval_vec)
    eval_vec[utt] = []
    for op,hyp in zip(op_vec, hyp_vec):
      if hyp != '<eps>': eval_vec[utt].append(op)

# Load the 'ctm' into dictionary,
ctm = dict()
with open(ctm_in) as f:
  for l in f:
    utt, ch, beg, dur, wrd, conf = l.split()
    if not utt in ctm: ctm[utt] = []
    ctm[utt].append((utt, ch, float(beg), float(dur), wrd, float(conf)))

# Build the 'ctm' with 'eval' column added,
ctm_eval = []
for utt,ctm_part in ctm.iteritems():
  ctm_part.sort(key = operator.itemgetter(2)) # Sort by 'beg' time,
  # extending the 'tuple' by '+':
  merged = [ tup + (evl,) for tup,evl in zip(ctm_part,eval_vec[utt]) ]
  ctm_eval.extend(merged)

# Sort again,
ctm_eval.sort(key = operator.itemgetter(0,1,2))

# Store,
with open(ctm_eval_out,'w') as f:
  for tup in ctm_eval:
    f.write('%s %s %f %f %s %f %s\n' % tup)

