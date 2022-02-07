###############################################################################
# script to parse UrQMD files                                                 #
# run with: python3 parse_UrQMD.py <input_file> ...                           #
# Output tree.root with nEvent, nTracks, px, py, pz, m, ityp, iso, charge     #
# dEdx and smeared m^2 distributions to be added                              #
###############################################################################
import re
import sys
import numpy as np
from array import array
import ROOT

FILES=sys.argv[1:]

nEvent, nTracks, proj_mass, proj_charge, tar_mass, tar_charge = array('i', [0]), array('i', [0]), array('i', [0]), array('i', [0]), array('i', [0]), array('i', [0])

b, snn = array('f',[0]), array('f',[0])

r0, rx, ry, rz, p0, px, py, pz, m = array('f',[0]), array('f',[0]), array('f',[0]), array('f',[0]), array('f',[0]), array('f',[0]), array('f',[0]), array('f',[0]), array('f',[0])

ityp, iso, charge = array('i', [0]), array('i', [0]), array('i', [0])

Event_counter = 0
# create a tree of a size given by even limit
limit=200
TreeFile = ROOT.TFile("tree200.root", "RECREATE")
tree = ROOT.TTree("tree", "Au+Au example")
tree.Branch('nEvent', nEvent, 'nEvent/I')
tree.Branch('nTracks', nTracks, 'nTracks/I')
tree.Branch('px', px, 'px/F')
tree.Branch('py', py, 'py/F')
tree.Branch('pz', pz, 'pz/F')
tree.Branch('m', m, 'm/F')
tree.Branch('ityp', ityp, 'ityp/I')
tree.Branch('iso', iso, 'iso/I')
tree.Branch('charge', charge, 'charge/I')

for FILE in FILES:
  with open(FILE, 'r') as f:
    contents = f.readlines()
    for i,line in enumerate(contents):
      if Event_counter>limit:
        continue
      if "UQMD" in line:
        Event_counter+=1
      if "projectile" in line and "target" in line:
        proj_mass[0]=int(re.findall(r'\d+', line)[0])
        proj_charge[0]=int(re.findall(r'\d+', line)[1])
        tar_mass[0]=int(re.findall(r'\d+', line)[2])
        tar_charge[0]=int(re.findall(r'\d+', line)[3])
      if "impact_parameter_real/min/max(fm)" in line:
        b[0]=float(re.findall(r'\d+\.\d+', line)[0])
      if "sqrt(s)(GeV)" in line:
        snn[0]=float(re.findall(r'\d+\.\d+E.\d+', line)[1])
      if "event#" in line:
        nEvent[0]=int(re.findall(r'\d+', line)[0])
      if "pvec" in line:
        if len(contents[i+1].split()) > 1:
          nTracks[0]=int(re.findall(r'\d+', contents[i+1])[0])
          # starting from 3rd line
          for j in range(0, nTracks[0]):
            r0[0], rx[0],ry[0],rz[0],p0[0],px[0],py[0],pz[0],m[0]=[float(val) for val in re.findall(r'.\d+\.\d+E.\d+', contents[i+3+j])]
            ityp[0], iso[0], charge[0], *others=[int(val) for val in contents[i+3+j].split() if not "E" in val]
            tree.Fill()
            
tree.Write()
TreeFile.Close()

