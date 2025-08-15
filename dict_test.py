
class FUNCDICTL():
    def __init__(self):
        """
        This packages simple functions together with initial parameter estimates for the coefficients a1, a2 ...
        The 'nlf' string must match nlf equation conventions.
        The functions (i.e. fn1, fn2) are python implementations.
        It seems a bit excessive, but it helps with using correlated ureals for a1, a2.NLF produces these but Delphi
        does not handle them as an input to the functions.
        The functions enter the coefficients as a list from nlf gtcfit.
        This anticipates using nlf for prediction curves for all our capacitors.
        """
        func1 = {'fn': self.fn1, 'param': [0, 0], 'nlf': 'a1 + a2*x'}
        func2 = {'fn': self.fn2, 'param': [0, 0, 0], 'nlf':'a1 + a2*x +a2*x^2'}

        self.f_dict = {
            'func1': func1,
            'func2': func2
             }


    def fn1(self, coeff, x):
        return coeff[0] + coeff[1] * x

    def fn2(self, coeff, x):
        return coeff[0] + coeff[1] * x + coeff[2] * x**2

if __name__ == '__main__':

    fn = FUNCDICTL()
    result = fn.f_dict['func1']['fn']([1, 2], 3)  # note that the coefficients are now in a list
    print(result)
