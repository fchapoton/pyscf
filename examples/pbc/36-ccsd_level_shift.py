#!/usr/bin/env python

'''
Looks at a hydrogen metallic lattice and looks at using the level shift in
k-point ccsd.  While for most systems the level shift will not affect results,
this is one instance where the system will converge on a different ccsd solution
depending on whether one is using a level shift or not.
'''

import numpy as np

from pyscf.lib import finger
from pyscf.pbc import gto as pbcgto
from pyscf.pbc import scf as pbcscf

import pyscf.cc
import pyscf.pbc.cc as pbcc
from pyscf.pbc.lib import kpts_helper
#from pyscf.pbc.cc.kccsd_rhf import kconserve_pmatrix
import pyscf.pbc.cc.kccsd_t_rhf as kccsd_t_rhf

cell = pbcgto.Cell()
cell.atom = [['H', (0.000000000, 0.000000000, 0.000000000)],
             ['H', (0.000000000, 0.500000000, 0.250000000)],
             ['H', (0.500000000, 0.500000000, 0.500000000)],
             ['H', (0.500000000, 0.000000000, 0.750000000)]]
cell.unit = 'Bohr'
cell.a = [[1.,0.,0.],[0.,1.,0],[0,0,2.2]]
cell.verbose = 3
cell.spin = 0
cell.charge = 0
cell.basis = 'gth-szv'
cell.pseudo = 'gth-pade'
for i in range(len(cell.atom)):
    cell.atom[i][1] = tuple(np.dot(np.array(cell.atom[i][1]),np.array(cell.a)))
cell.build()

nmp = [2, 1, 1]

kmf = pbcscf.KRHF(cell)
kmf.kpts = cell.make_kpts(nmp, scaled_center=[0.0,0.0,0.0])
e = kmf.kernel()
#self.assertAlmostEqual(e, 2.30510338236481, 6)

mycc = pbcc.KCCSD(kmf)
eris = mycc.ao2mo(kmf.mo_coeff)
eris.mo_energy = [eris.fock[k].diagonal() for k in range(mycc.nkpts)]
print('\nCCSD energy w/o level shift and MP2 initial guess:')
ekccsd, t1, t2 = mycc.kernel(eris=eris)
#self.assertAlmostEqual(ekccsd, 0.02417522810234485, 6)

def _adjust_occ(mo_energy, nocc, shift):
    '''Modify occupied orbital energy'''
    mo_energy = mo_energy.copy()
    mo_energy[:nocc] += shift
    return mo_energy

madelung = 1.36540204381
eris.mo_energy = [_adjust_occ(mo_e, mycc.nocc, madelung) for mo_e in eris.mo_energy]
print('\nCCSD energy w/o level shift and previous t1/t2 as initial guess:')
ekccsd, _, _ = mycc.kernel(t1=t1, t2=t2, eris=eris)
#self.assertAlmostEqual(ekccsd, 0.02417522810234485, 6)

# Use adjusted occupied orbitals
print('\nCCSD energy w/ level shift and MP2 initial guess:')
ekccsd, t1, t2 = mycc.kernel(eris=eris)
#self.assertAlmostEqual(ekccsd, -0.11122802032348603, 6)

print('\nCCSD energy w/ level shift and previous t1/t2 as initial guess:')
ekccsd, _, _ = mycc.kernel(t1=t1, t2=t2, eris=eris)
#self.assertAlmostEqual(ekccsd, -0.11122802032348603, 6)
