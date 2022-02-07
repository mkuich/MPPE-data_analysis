###############################################################################
# script to read TTree with python and look at simple histograms              #
###############################################################################
import ROOT
import math

# open file and retrieve a tree with generated particles
file = ROOT.TFile("tree100.root",'read')
tree = file.Get("tree")

# create a few ROOT-style histograms
hist_E_proton = ROOT.TH1F('hpT_P', 'This is the E distribution of protons', 500, 0, 10 )

hist_pT_Kaon_plus = ROOT.TH1F('hpT_KP', 'This is the pT distribution of Kaons', 100, 0, 4 )

hist_y_pions = ROOT.TH1F('hy_PM', 'This is the y distribution of pions', 100, -4, 4 )

hist2D_mass_p = ROOT.TH2D('h_m_p', 'This is the mass vs p distribution', 100, 0, 10, 250, 0, 2.5)

for entry in tree:
    # create Lorentz Vector for each particle -> you gain automatic calculation of several useful variables
    particle = ROOT.Math.LorentzVector('ROOT::Math::PxPyPzM4D<double>')()
    particle.SetPx(entry.px)
    particle.SetPy(entry.py)
    particle.SetPz(entry.pz)
    #particle.SetE(math.sqrt(entry.px**2+entry.py**2+entry.pz**2+entry.m**2))
    particle.SetM(entry.m)
    
    # select protons based on the UrQMD ID number and charge and fill the histogram with their energy values
    if entry.ityp==1 and entry.charge==1:
        hist_E_proton.Fill(particle.E())
    
    # select positively charged kaons and fill the histogram with their pT values
    if entry.ityp==106 and entry.charge==1:
        hist_pT_Kaon_plus.Fill(particle.Pt())
    
    # select charged pions and fill the histogram with their rapidity values
    if entry.ityp==101 and (entry.charge==-1 or entry.charge==1):
        hist_y_pions.Fill(particle.Rapidity())
     
    # fill 2D histogram with particles' p and mass values 
    hist2D_mass_p.Fill(particle.P(),particle.M())

# create a ROOT-style canvas, in which you draw histograms    
canv = ROOT.TCanvas( 'canv', '', 500, 500 )    

# draw proton energy distribution
hist_E_proton.GetXaxis().SetTitle("Energy [GeV]")
hist_E_proton.GetYaxis().SetTitle("Entries")
hist_E_proton.Draw()
# save the canvas to a file
canv.Print("energy.pdf")

# draw charged pion y distribution
hist_y_pions.GetXaxis().SetTitle("y")
hist_y_pions.GetYaxis().SetTitle("Entries")
hist_y_pions.Draw()
# fit the histogram with predefined ROOT function, i.e. Gaussian distribution
hist_y_pions.Fit("gaus")
canv.Print("rapidity.pdf")

# draw positively charged kaon pT distribution
hist_pT_Kaon_plus.GetXaxis().SetTitle("p_{T} [GeV/c]")
hist_pT_Kaon_plus.GetYaxis().SetTitle("Entries")
hist_pT_Kaon_plus.SetMarkerStyle(20)
hist_pT_Kaon_plus.Draw("P")

# create a one dimensional Bolztman-like function and fit it to kaon pT distribution
boltzman = ROOT.TF1('boltzman', '[0]*x*TMath::Exp(-(TMath::Sqrt(x*x+[1]*[1])-[1])/[2])', 0, 4 )
boltzman.FixParameter(1, 0.4937) # kaon mass in GeV
boltzman.SetParameter(0, hist_pT_Kaon_plus.Integral())
boltzman.SetParameter(2, 0.18) # educated guess of order of T parameter magnitude
hist_pT_Kaon_plus.Fit("boltzman")
print('T parameter: ', round(boltzman.GetParameter(2), 4), '+/-', round(boltzman.GetParError(2),4), 'GeV')
canv.Update()
canv.Print("pT.pdf")

# draw a 2D histogram
hist2D_mass_p.Draw("colz")

# create a graphical cut on the histogram ??? To be added
canv.Print("m_vs_p.pdf")

file.Close()
