'''
Created on 2012-12-02

@author: Sebastien Ouellet sebouel@gmail.com
'''
import gamelogic

import pickle

def main():
    savefile = open("best_mapping.sav", "rb")
    influence_dna = pickle.load(savefile)
    gamelogic.viewed = True
    gamelogic.simulate(influence_dna)    
    
if __name__ == "__main__":
    main()
