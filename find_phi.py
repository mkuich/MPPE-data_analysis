###############################################################################
# script to read TTree with python and look for lambdas                       #
###############################################################################
import ROOT
import math
from tqdm import tqdm

# Open file and retrieve a tree with generated particles, later update it with phi histograms
file = ROOT.TFile("tree1000.root",'update')
tree = file.Get("tree")

hist_minv_phi__in_K_K = ROOT.TH1D('h_phi', 'Invariant mass of phi', 120, 0.98, 1.1 )
hist_minv_phi__in_K_K.Sumw2()
hist_minv_phi_background__in_K_K = ROOT.TH1D('h_phi_background', 'Invariant mass of lambda', 120, 0.98, 1.1 )
hist_minv_phi_background__in_K_K.Sumw2()

# progress bar
N = tree.GetEntries()
pbar = tqdm(total=N)
pbar.set_description("Tree processing... ")

for i,first in enumerate(tree):
  pbar.update(1)
  if first.ityp==106 and first.charge==1:
    particle1 = ROOT.Math.LorentzVector('ROOT::Math::PxPyPzE4D<double>')()
    particle1.SetPx(first.px)
    particle1.SetPy(first.py)
    particle1.SetPz(first.pz)
    particle1.SetE(math.sqrt(first.px**2+first.py**2+first.pz**2+first.m**2))
    nEv1=first.nEvent
    for j in range(N):
      tree.GetEntry(j)
      nEv2=tree.nEvent
      if tree.ityp==-106 and tree.charge==-1:
        particle2 = ROOT.Math.LorentzVector('ROOT::Math::PxPyPzE4D<double>')()
        particle2.SetPx(tree.px)
        particle2.SetPy(tree.py)
        particle2.SetPz(tree.pz)
        particle2.SetE(math.sqrt(tree.px**2+tree.py**2+tree.pz**2+tree.m**2))
        minv = (particle1+particle2).M()
        if nEv1==nEv2:
          hist_minv_phi__in_K_K.Fill(minv) # signal
        else:
          hist_minv_phi_background__in_K_K.Fill(minv) # mixed-events background
          
pbar.close()

canv = ROOT.TCanvas( 'canv', '', 500, 500 )    

#print(hist_minv_phi__in_K_K.GetEntries(), hist_minv_phi_background__in_K_K.GetEntries())
hist_minv_phi__in_K_K.Draw()
canv.Print("phi.pdf")
hist_minv_phi_background__in_K_K.Draw()
canv.Print("phi_background.pdf")

# update the tree with new histograms
hist_minv_phi__in_K_K.Write()
hist_minv_phi_background__in_K_K.Write()

#hist_minv_phi_background__in_K_K.Scale(hist_minv_phi__in_K_K.GetEntries()/hist_minv_phi_background__in_K_K.GetEntries())
#hist_phi_signal = hist_minv_phi__in_K_K - hist_minv_phi_background__in_K_K
#hist_phi_signal.Draw()
#canv.Print("phi_signal.pdf")

file.Close()
