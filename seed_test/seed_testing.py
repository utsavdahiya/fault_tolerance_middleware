import random
import numpy as np
from collections import defaultdict, Counter
import pickle

START_SEED = 0
NUM_LOCATIONS = 4
NUM_VM_SET = 500
SET_SIZE = 3
NUM_ITERATIONS = 100
OUTPUT_FILE = './default_output.pkl'

def place_vm():
    total_result = []
    location_array = [i for i in range(NUM_LOCATIONS)]
    seed = START_SEED
    for i in range(NUM_ITERATIONS):
        print("Iter start------------------")
        random.seed(seed)

        seed_result = {
            'seed': seed,
            'score': 0,
            'togetherness': {},
            'placement': [0] * NUM_LOCATIONS
        }

        #now place the sets
        for Set in range(NUM_VM_SET):
            togetherness = {}
            placement = [0] * NUM_LOCATIONS
            
            for vm in range(SET_SIZE):
                loc = random.choice(location_array)
                placement[loc] += 1
            #now calc togetherness of this placement
            for loc in range(NUM_LOCATIONS):
                num = placement[loc]
                if(num == 1):
                    if(togetherness.get(0, None)):
                        togetherness[0] += 1
                    else:
                        togetherness[0] = 1
                else:
                    #if any are together
                    if togetherness.get(num, None):
                        togetherness[num] += 1
                    else:
                        togetherness[num] = 1

            #updating the result
            seed_result['placement'] = [sum(i) for i in zip(seed_result['placement'], placement)]
            seed_result['togetherness'] = Counter(seed_result['togetherness']) + Counter(togetherness)

        #calculating score for this
        score = 0
        for key, val in seed_result['togetherness'].items():
            score += key * val  #a weighted sum of the togetherness
        seed_result['score'] = score
        total_result.append(seed_result)
        
        seed += 1
    return seed, total_result

def main():
    total_result = []

    end_seed, total_result = place_vm()
    print(f"ENDING at seed: {end_seed}")

    sorted(total_result, reverse=True, key=lambda seed: seed['score'])
    # store = {'seed_result':total_result}
    print(f"store: \n{total_result}")
    #writing the results to output file
    with open(OUTPUT_FILE, '+wb') as handle:
        print("file opened")
        store = pickle.dump(total_result, handle)

main()