'''
Created on 2012-12-09

@author: Sebastien Ouellet sebouel@gmail.com
'''
import gamelogic1
import gamelogic2

import os
import pickle

def main():
    mappings = "mappings"
    files = os.listdir(mappings)
    for mapping in files:
        if mapping == "frontdefense.sav" or mapping == "detour.sav":
            simulation = gamelogic2
        else:
            simulation = gamelogic1
        print mapping
        savefile = open(os.path.join(mappings, mapping), "rb")
        influence_dna = pickle.load(savefile)
        simulation.viewed = True
        simulation.simulate(influence_dna)    
        

if __name__ == "__main__":
    main()