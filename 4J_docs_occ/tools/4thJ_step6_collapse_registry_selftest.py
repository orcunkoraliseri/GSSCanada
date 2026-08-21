# -*- coding: utf-8 -*-
"""The addendum's §4 guard, seen REFUSING. Nothing on disk is touched."""
import sys, importlib
sys.path.insert(0, '.')
m = importlib.import_module('4thJ_step6_g61_rake_folds')

print('registered triples:')
for k, v in sorted(m.REGISTERED_COLLAPSES.items()):
    print('   %-16s %-10s -> %-14s  %s' % (k[0], k[1], k[2], v))

print('\n1. the three real per-fold dicts, as built:')
for c, coll in (
        ('es', {'strat_hh_type': {'unknown': 'other_complex'},
                'strat_econ_status': {'homemaker': 'other_inactive'}}),
        ('uk', {'strat_hh_type': {'unknown': 'other_complex'}}),
        ('it', {'strat_hh_type': {'unknown': 'other_complex'},
                'strat_econ_status': {'unknown': 'other_inactive'}})):
    print('   %s -> unregistered: %s' % (c, m.check_registered(coll) or 'none'))

print('\n2. SEEN FAILING -- a fourth collapse nobody registered:')
bad = {'strat_hh_type': {'unknown': 'other_complex'},
       'strat_econ_status': {'student': 'employed'}}
print('   %s' % m.check_registered(bad))

print('\n3. SEEN FAILING -- a REGISTERED variable/source with a NEW target:')
bad2 = {'strat_hh_type': {'unknown': 'one_person'}}
print('   %s' % m.check_registered(bad2))

print('\n4. no collapse at all:')
print('   %s' % (m.check_registered(None) or 'none'))

ok = (not m.check_registered({'strat_hh_type': {'unknown': 'other_complex'}})
      and len(m.check_registered(bad)) == 1
      and len(m.check_registered(bad2)) == 1)
print('\nGUARD %s' % ('OK -- passes what is registered, refuses what is not'
                      if ok else '!!! BROKEN'))
sys.exit(0 if ok else 1)
