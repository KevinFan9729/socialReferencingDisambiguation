test = ['a','b','c','d','e']

def reorder(ls, order):
    reorder_ls = [None] * len(order)
    for i in range(len(order)):
        reorder_ls[i] = ls[order[i]]
    return reorder_ls

order=[1,3,4,0,2]
# [b,d,e,a,c]
sim_score=[0.3, 0.4, 0.5, 0.2, 0.6]
#[4,2,1,0,3]

def find_order(sim_ls):
    order = [None] * len(sim_ls)
    for i in range(len(sim_ls)):
        index = sim_ls.index(max(sim_ls))
        order[i] = index
        sim_ls[index] = -1 
    return order
print(reorder(test,order))
print(find_order(sim_score))