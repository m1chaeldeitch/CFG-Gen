# Overall plan:
#   1) Utilize constrain.py to obtain all the constraints
#      in the form of "l_term = r_term"
#   2) Generate a collection of nodes for each term in the
#      constraint system
#   3) Implement the interface for union-find
#   4) Follow the algorithm for unifying
from operator import truediv


#collect constraint system
constraints = 5

#base for unification
while (constraints > 0):
    print(constraints)
    print(constraints)
    constraints = constraints - 1

if constraints < 3:
   x = 3 + 3

if constraints + 3 == 2:
    y = 0
elif constraints + 3 == 3:
    print("Testing elif")
else:
    print("Testing else")

z = 5