
def false_fluents_heuristic(start, goal, ops, ancestors, infOkay):
    return goal.easyH(start, 1)