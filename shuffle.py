import numpy as np
import math
import itertools
from scipy.linalg import expm

I = np.matrix('1 0; 0 1')
X = np.matrix('0 1; 1 0')
Y = np.matrix('0 -1;1 0')*complex(0,1)
Z = np.matrix('1 0; 0 -1')
paulis = [I,X,Y,Z]

H = np.matrix('1 1; 1 -1')*(1/math.sqrt(2))

# apply e^{i\beta X} to each qubit
def apply_B(beta, states):
    eiB = np.matrix([[math.cos(beta),complex(0,math.sin(beta))],[complex(0,math.sin(beta)),math.cos(beta)]])
    result = [] 
    for state in states[0]:
        # apply the B operator locally
        decomp = pick_pauli(eiB*state*np.conj(eiB))
        result.append(decomp[0])
        states[1] *= decomp[1]
        states[2] *= decomp[2]
    return [result, states[1], states[2]]

# apply e^{i\gamma Z_a Z_b Z_c} to equation containing variables a,b,c
def apply_C(gamma, states):
    # restrict to only qubit 1,2,3 for now
    result = []
    local_state = kron(states[0])
    eiC = np.asmatrix(expm(complex(0,1)*gamma*kron([Z,Z,Z])))
    decomp = pick_pauli(eiC*local_state*np.conj(eiC))
    states[1] *= decomp[1]
    states[2] *= decomp[2]
    return [decomp[0], states[1], states[2]]

# create the C observable
def create_C(would_be_set_of_equations):
    # if the equation exists then add this
    C = (1/2)*kron([Z,Z,Z])

    # return the final observable
    return C

# take the kronecker (tensor) product of a list of len(m) matrices
def kron(m):
    if len(m) == 1:
        return m
    total = np.kron(m[0], m[1])
    if len(m) > 2:
        for i in range(2, len(m)):
            total = np.kron(total, m[i])
    return total

# decompose a 2^n x 2^n matrix into n-qubit tensor products of Pauli matrices
def decompose(R):
    # take the cartesian product of the pauli matrices n times and tensor them together
    R = np.asmatrix(R)
    dim = int(np.log2(R.shape[0]))
    cart_prod = itertools.product(paulis, repeat=dim)
    basis = []
    if dim > 1:
        for prod in cart_prod:
            basis.append(kron(prod))
    else:
        basis = paulis
   
    # decompose matrix R into its components
    const = 1/(math.pow(2,dim))
    c = []
    for B in basis: 
        c.append(np.asscalar((const*R*B).trace()))
    return c

# from a state R, pick a pauli matrix from the probability distribution
def pick_pauli(R):
    # decompose the matrix into sum of paulis and get dimension
    R = np.asmatrix(R)
    consts = decompose(R)
    dim = int(np.log2(R.shape[0]))

    # find the normalized weights
    consts_sum = 0
    for i in consts: 
        consts_sum += abs(i)
    weights = []
    for i in consts: 
        weights.append(abs(i)/consts_sum)

    # pick a random weight
    choice = np.random.choice(int(math.pow(4,dim)), p=weights)

    # pick a pauli for each qubit from the weights
    pauli_choices = []
    for i in range(dim-1,-1,-1):
        pos = int((choice/math.pow(4,i)) % 4)
        pauli_choices.append(paulis[pos])

    '''
    P_CHOICE = 0
    for i in range(0,dim):
        pos = int((choice/math.pow(4,i)) % 4)
        if i == 0:
            P_CHOICE = paulis[pos]
        else:
            P_CHOICE = np.kron(paulis[pos],P_CHOICE)
    '''
    
    return [pauli_choices, consts[choice], weights[choice]]

def classical_circuit(INIT):
    result = (Z*X*H*INIT*H*X).trace()
    print(result)

def circuit(INIT):
    results = []
    samples = 10000
    for i in range(0,samples):
        # pick a pauli for INIT
        r1 = pick_pauli(INIT)
        STATE = r1[0]

        STATE = H*STATE*H
        r2 = pick_pauli(STATE)
        STATE = r2[0]

        STATE = X*STATE*X
        r3 = pick_pauli(STATE)
        STATE = r3[0]
        
        rf = r1[1]*r2[1]*r3[1]
        pf = r1[2]*r2[2]*r3[2]
        
        p_hat = (rf/pf)*(STATE*Z).trace()
        results.append(p_hat)

    avg = sum(results)/samples
    print(np.asscalar(avg))

def e3lin2(input_equations):
    # attempt to solve x_1 + x_2 + x_3 = 0
    C = create_C(a)
    rho = kron([0.5*(I+X),0.5*(I+X),0.5*(I+X)])
    #print(rho)
    
    scale = 10
    gamma = 0
    beta = math.pi/4
    for g in range(0,scale):
        results = []
        samples = 100
        for i in range(0,samples):
            # pick pauli, pass into B then C
            init = pick_pauli(C)
            op1 = apply_B(beta, init)
            op2 = apply_C(gamma, op1)
            
            #print(kron(op2[0]))
            p_hat = (op2[1]/op2[2])*(kron(op2[0])*rho).trace()
            results.append(p_hat)

        avg = sum(results)/samples
        expectation = np.real(np.asscalar(avg))
        print('gamma = %.2f, beta = %.2f, <C> = %.4f' % (gamma, beta, expectation))
        gamma += 2*math.pi/scale

if __name__ == '__main__':
    # input state is a\ket{0} + b\ket{1}
    a = 1/2
    b = math.sqrt(3)/2
    #a = 1
    #b = 0
    INIT = np.matrix([[a*a,a*b],[b*a,b*b]])
    #classical_circuit(INIT)
    #circuit(INIT)
    #pick_pauli(np.kron(X,Y))

    input_equations = []
    e3lin2(input_equations)

