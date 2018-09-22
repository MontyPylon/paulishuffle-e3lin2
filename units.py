import unittest
import numpy as np
import math
import diag
import basicshuffle

I = np.matrix('1 0; 0 1')
X = np.matrix('0 1; 1 0')
Y = np.matrix('0 -1;1 0')*complex(0,1)
Z = np.matrix('1 0; 0 -1')
paulis = [I,X,Y,Z]

class TestDiag(unittest.TestCase):
    def test_trivial_decomp(self):
        self.assertEqual(diag.decompose(0,I),[1,0,0,0])
        self.assertEqual(diag.decompose(0,X),[0,1,0,0])
        self.assertEqual(diag.decompose(0,Y),[0,0,1,0])
        self.assertEqual(diag.decompose(0,Z),[0,0,0,1])

    def test_trivial_pi(self):
        self.assertEqual(np.allclose(diag.decompose(math.pi,I),[1,0,0,0]),True)
        self.assertEqual(np.allclose(diag.decompose(math.pi,X),[0,1,0,0]),True)
        self.assertEqual(np.allclose(diag.decompose(math.pi,Y),[0,0,1,0]),True)
        self.assertEqual(np.allclose(diag.decompose(math.pi,Z),[0,0,0,1]),True)

    def test_decomp(self):
        self.assertEqual(basicshuffle.decompose_1d((I+X)/2),[0.5,0.5,0,0])
        self.assertEqual(basicshuffle.decompose_1d((I+Y)/2),[0.5,0,0.5,0])
        self.assertEqual(basicshuffle.decompose_1d((I+Z)/2),[0.5,0,0,0.5])

if __name__ == '__main__':
    unittest.main()
