'''
Created on 2012-12-02

@author: Sebastien Ouellet sebouel@gmail.com
'''
import gamelogic

import random
import pickle

####### Parameters #######

iterations = 50
population_size = 50
crossover_probability = 0.8
mutation_probability = 0.2
large_mutation_probability = 0.20

tournament_size = 9
tournament_probability = 0.9

c_len = 13
number_genes = c_len*4

many_tests = 0

good_enough = -100

##########################

def min_or_max(scores):
    return min(scores)

def tournament(population, scores):
    chosen = random.sample(scores, tournament_size)
    if random.random() < tournament_probability:
        index = min_or_max(chosen)
        winner = population[index[1]]
        return winner
    else:
        return population[random.choice(chosen)[1]]

def selection(population, scores):
    selected = [tournament(population, scores) for _ in xrange(population_size)]
    return selected

def run_game(influence_dna):
    return gamelogic.simulate(influence_dna)

def fitness_test(population):    
    scores = [None]*population_size
    for i in xrange(population_size):
            influence_dna = population[i]
            score = run_game(influence_dna)
            scores[i] = (score,i)
    return scores

def generate_random():
    individual = [random.randint(-10,10) for _ in xrange(number_genes)]
    return individual

def generate_population():
    population = [generate_random() for _ in xrange(population_size)]
    return population

def two_crossover(parent1, parent2):
    max = number_genes-1
    first = random.randint(1,max)
    second = random.randint(1,max)
    
    if first > second:
        temp = first
        first = second
        second = temp
        
    child1 = list(parent1)
    child2 = list(parent2)
    
    for index in xrange(first,second):
        if random.random() < mutation_probability:
            child1[index] = mutate(parent2[index])
        else:
            child1[index] = parent2[index]
        if random.random() < mutation_probability:
            child2[index] = mutate(parent1[index])
        else:
            child2[index] = parent1[index]
    
    return child1, child2

def one_crossover(parent1, parent2):
    first = random.randint(1,number_genes-1)

    child1 = list(parent1)
    child2 = list(parent2)

    for index in xrange(first):
        if random.random() < mutation_probability:
            child1[index] = mutate(parent2[index])
        else:
            child1[index] = parent2[index]
        if random.random() < mutation_probability:
            child2[index] = mutate(parent1[index])
        else:
            child2[index] = parent1[index]
    
    return child1,child2

def mutate(allele):
    if random.random() < large_mutation_probability:
        return random.randint(-10,10)
    else:
        allele = allele+random.choice([-1,1])
        if allele > 10:
            allele = 10
        elif allele < -10:
            allele = -10
        return allele

def all_mutate(individual):
    for i in xrange(number_genes):
        if random.random() < mutation_probability:
            individual[i] = mutate(individual[i])

    return individual

def generate_offsprings(selected, scores, population):
    new_population = [None]*population_size
    fittest = min_or_max(scores)
    best = list(population[fittest[1]])
    for i in xrange(population_size):
        if random.random() < crossover_probability and i < population_size-1:
            #new_population[i], new_population[i+1] = one_crossover(selected[i],selected[i+1])
            new_population[i], new_population[i+1] = two_crossover(selected[i],selected[i+1])
        else:
            new_population[i] = all_mutate(selected[i])
    new_population[0] = best
    return new_population

def main():
    population = generate_population()
    scores = fitness_test(population)
    selected = selection(population, scores)
    for iteration in xrange(iterations):
        population = generate_offsprings(selected,scores,population)
        scores = fitness_test(population)
        selected = selection(population, scores)
        fittest = min_or_max(scores)
        print "Best score: "+str(fittest[0])
        #print "Individual:", population[fittest[1]]
        print "Generation: "+str(iteration)
        if fittest[0] < good_enough:
            break
    fittest = min_or_max(scores)
    print "Best score: "+str(fittest[0])
    print "Fittest individual: ", population[fittest[1]]
    
    if not many_tests:
        savefile = open("best_mapping.sav", "wb")
        pickle.dump(population[fittest[1]], savefile)

    if many_tests:
        return fittest[0]

if __name__ == "__main__":
    if many_tests:
        good = 0
        for _ in xrange(many_tests):
            if main() < 150:
                good += 1
        print "Finds a solution", good*100.0/many_tests, "% of the time"
    else:
        main()
        
        
        
