#  python3.8 som environment
from GTC import ureal, ucomplex
from json import dumps, loads
import csv
# imports below are just testing related
from GTC.reporting import budget  # just for checks
from math import pi, sqrt  # just for some number creation


class GTCSTORE(object):
    def ureal_to_dict(self, unr, **kwargs):
        """
        Turns a GTC uncertain real into a dictionary of its parts suitable for json storage.
        Retains nothing of the structure that created the uncertain real.
        A more useful label can be used if, for instance, it is an intermediate result.
        :param unr: a GTC uncertain real
        :param kwargs: 'new_label' if wanted
        :return: a dictionary with all the necessary parts of the ureal
        """
        this_label = unr.label
        for arg in kwargs.keys():
            if arg == 'new_label':
                this_label = kwargs[arg]
        chosen_label = this_label
        return {'x': unr.x, 'u': unr.u, 'df': unr.df, 'label': chosen_label}

    def dict_to_ureal(self, unr_dict):
        """
        Takes a dictionary created by ureal_to_dict and creates a GTC uncertain real.
        :param unr_dict: dictionary of parts of a GTC uncertain real.
        :return: GTC uncertain real
        """
        return ureal(unr_dict['x'], unr_dict['u'], unr_dict['df'], label=unr_dict['label'])

    def save_gtc(self, gtc_list, gtc_file):
        """
        Stores json strings in a csv file
        :param gtc_list: a list of json strings
        :param gtc_file: full name of a csv file
        :return: opens file, saves and closes before return
        """
        with open(gtc_file, 'w', newline='') as output_file_name:
            writer = csv.writer(output_file_name)
            writer.writerows(gtc_list)
            output_file_name.close()
        return

    def read_gtc(self, gtc_file):
        """
        Reads json strings in a csv file
        :param gtc_file: full name of a csv file
        :return: a list of json strings
        """
        input_list = []
        with open(gtc_file, newline='') as input_file_name:
            reader = csv.reader(input_file_name)
            for row in reader:
                input_list.append(row)
            input_file_name.close()
        return input_list

    def ureal_to_json(self, unr, **kwargs):
        """
        Turns a GTC uncertain real into a dictionary of its parts and then into a json string for storage.
        Retains nothing of the structure that created the uncertain real.
        A more useful label can be used if, for instance, it is an intermediate result.
        :param unr: a GTC uncertain real
        :param kwargs: 'new_label' if wanted
        :return: a json string with all the necessary parts of a dictionary to make a ureal
         """
        this_label = unr.label
        for arg in kwargs.keys():
            if arg == 'new_label':
                this_label = kwargs[arg]
        chosen_label = this_label
        return dumps({'x': unr.x, 'u': unr.u, 'df': unr.df, 'label': chosen_label})

    def json_to_ureal(self, unr_json):
        """
        Takes a json string as created by ureal_to_json and creates a GTC uncertain real.
        :param unr_json: a json string of a dictionary of parts of a GTC uncertain real.
        :return: GTC uncertain real
        """
        unr_dict = loads(unr_json)
        return ureal(unr_dict['x'], unr_dict['u'], unr_dict['df'], label=unr_dict['label'])

    def save_gtc_real(self, gtc_list, gtc_file):
        """
        Stores json strings in a csv file
        :param gtc_list: a list of gtc uncertain reals
        :param gtc_file: full name of a csv file
        :return: opens file, saves and closes before return
        """
        json_lst = []
        for unr in gtc_list:
            json_lst.append([self.ureal_to_json(unr)])

        with open(gtc_file, 'w', newline='') as output_file_name:
            writer = csv.writer(output_file_name)
            writer.writerows(json_lst)
            output_file_name.close()
        return

    def read_gtc_real(self, gtc_file):
        """
        Reads json strings in a csv file
        :param gtc_file: full name of a csv file
        :return: a list of gtc uncertain reals
        """
        input_list = []
        with open(gtc_file, newline='') as input_file_name:
            reader = csv.reader(input_file_name)
            for row in reader:
                tempx = self.json_to_ureal(row[0])  # putting this directly in append() causes an error???
                input_list.append(tempx)
            input_file_name.close()
        return input_list

    def ucomplex_to_dict(self, unc, **kwargs):
        """
        Turns a GTC uncertain complex into a dictionary of its parts suitable for json storage.
        Retains nothing of the structure that created the uncertain real.
        A more useful label can be used if, for instance, it is an intermediate result.
        :param unc: a GTC uncertain complex
        :param kwargs: 'new_label' if wanted
        :return: a dictionary with all the necessary parts of the ureal
        """
        this_label = unc.label
        for arg in kwargs.keys():
            if arg == 'new_label':
                this_label = kwargs[arg]
        chosen_label = this_label
        return {'xreal': unc.x.real, 'ximag': unc.x.imag, 'u': unc.u, 'v': unc.v, 'df': unc.df, 'label': chosen_label}

    def dict_to_ucomplex(self, unc_dict):
        """
        Takes a dictionary created by ucomplex_to_dict and creates a GTC uncertain complex.
        :param unc_dict: dictionary of parts of a GTC uncertain complex.
        :return: GTC uncertain complex
        """
        return ucomplex(unc_dict['xreal'] +1j*unc_dict['ximag'], unc_dict['v'], unc_dict['df'], label=unc_dict['label'])

    def ucomplex_to_json(self, unc, **kwargs):
        """
        Turns a GTC uncertain complex into a json string of a dictionary of its parts suitable for json storage.
        Retains nothing of the structure that created the uncertain real.
        A more useful label can be used if, for instance, it is an intermediate result.
        :param unc: a GTC uncertain complex
        :param kwargs: 'new_label' if wanted
        :return: a json string with all the necessary parts of the ureal
        """
        this_label = unc.label
        for arg in kwargs.keys():
            if arg == 'new_label':
                this_label = kwargs[arg]
        chosen_label = this_label
        return dumps({'xreal': unc.x.real, 'ximag': unc.x.imag, 'u': unc.u, 'v': unc.v, 'df': unc.df, 'label': chosen_label})

    def json_to_ucomplex(self, unc_json):
        """
        Takes a json string created by ucomplex_to_json and creates a GTC uncertain complex.
        :param unc_json: json string of a dictionary of parts of a GTC uncertain complex.
        :return: GTC uncertain complex
        """
        unc_dict = loads(unc_json)
        return ucomplex(unc_dict['xreal'] +1j*unc_dict['ximag'], unc_dict['v'], unc_dict['df'], label=unc_dict['label'])


if __name__ == '__main__':
    store = GTCSTORE()
    # first set up a trivial calculation
    x1 = ureal(10 * pi, pi / 3, label='x1')
    x2 = ureal(20, 2.3, label='x2')
    my_result = x1 * x2
    print(my_result)
    print(repr(my_result))
    for l, u in budget(my_result):
        print(l, u)

    print('\n', 'trying out the defs')
    first = store.ureal_to_dict(x1)  # , new_label='keith')
    second = store.ureal_to_dict(my_result)  # , new_label='jones')
    third = store.dict_to_ureal(first)
    fourth = store.dict_to_ureal(second)

    print(first, type(first))
    print(second, type(second))
    print(third, type(third))
    print(fourth, type(fourth))

    # mylist = []
    # mylist.append(x1)
    # mylist.append(x2)
    # store.save_gtc_real(mylist, 'results2.csv')
    # last_results = store.read_gtc_real('results1.csv')
    # print(last_results)
    # print(repr(last_results[1]))

    # Look at uncertain complex
    print('\n', 'Complex games')
    c1 = ucomplex((23.01 + 3.2j), (1.1, 0.22), 22, label='c1')
    c2 = ucomplex((2 * pi + 1j * pi), (1.1, 0.22), 22, label='c1')
    c3 = c1 + c2
    c4 = c1 * c2
    c5 = c3 / c4
    c6 = ucomplex((5 - 1.4j), 0.1, 11, label='c6')
    print(repr(c1))
    print(repr(c2))
    print(repr(c3))
    print(repr(c4))
    print(repr(c5))
    print(repr(c6))
    print(c6.x)
    aaa = store.ucomplex_to_dict(c1)
    print('aaa ', aaa, type(aaa))
    bbb = store.dict_to_ucomplex(aaa)
    print('bbb ', repr(bbb), type(bbb))
    aaa = store.ucomplex_to_dict(c2)
    print('aaa ', aaa, type(aaa))
    bbb = store.dict_to_ucomplex(aaa)
    print('bbb ', repr(bbb), type(bbb))
    aaa = store.ucomplex_to_dict(c3)
    print('aaa ', aaa, type(aaa))
    bbb = store.dict_to_ucomplex(aaa)
    print('bbb ', repr(bbb), type(bbb))
    aaa = store.ucomplex_to_dict(c4)
    print('aaa ', aaa, type(aaa))
    bbb = store.dict_to_ucomplex(aaa)
    print('bbb ', repr(bbb), type(bbb))
    aaa = store.ucomplex_to_dict(c5)
    print('aaa ', aaa, type(aaa))
    # bbb = dict_to_ucomplex(aaa)
    # print('bbb ', repr(bbb), type(bbb))
    print(c5.r)
    s1 = 0.2
    v1 = s1 ** 2
    s2 = 0.1
    v2 = s2 ** 2
    myr = 0.5
    s12 = s1 * s2 * sqrt(myr)  # not correct?
    v12 = s12 ** 2
    c7 = ucomplex((1 - 1j), (v1, v12, v12, v2), label='c6')
    print('c7', repr(c7))
    print(sqrt(0.1))
    print('c7 matrix', c7.v)

    mine = store.ucomplex_to_dict(c7)
    print('mine', mine, type(mine))
    allmine = store.dict_to_ucomplex(mine)
    print('allmine', repr(allmine))
    print(allmine.v)
    print(dumps(allmine.v))
    print(mine)
    print(complex(1,1))
    final = store.ucomplex_to_json(c7)
    print('final', final, type(final))
    final1 = store.json_to_ucomplex(final)
    print('final1', final1, type(final1))
