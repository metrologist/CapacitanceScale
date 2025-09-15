# conditions.py manages the dictionary of temperature and pressure measurements
from GTC import ureal
from archive import GTCSTORE
from json import dumps
class CONDITIONS():
    def __init__(self, expect):
        """

        For carrying the measured conditions through the analysis process.
        :param expect: List of keys identifying which temperature or pressure measurement
        """
        self.expect = expect
        self.cond_dict = {}  # to be created from rows, a dictionary of ureals
        self.gt = GTCSTORE()

    def build_dict_from_row(self, row):
        """

        :param row: a text row read in from the capcal_in csv file
        :return:
        """
        if row[0] in self.expect:
            self.cond_dict[row[0]] = ureal(float(row[1]), float(row[2]))  # csv likely provides strings, no floats
        else:
            print('unexpected key', row[0])

    def build_dict_from_block(self, block):
        """

        for convenience if a block can be extracted
        :param block: a list of lists, each being one row of a csv
        :return:
        """
        for x in block:
            self.build_dict_from_row(x)

    def cond_to_json(self):
        """

        converts the cond_dict to a json string
        :return:
        """
        # first convert dictionary of ureals to a dictionary of dictionary ureals.
        dict_out = {}
        for xx in self.cond_dict:
            dict_out[xx] = self.gt.ureal_to_dict(self.cond_dict[xx])
        json_out = dumps(dict_out)
        return json_out


if __name__ == '__main__':
    expected = ['AH1', 'AH2', 'GRin', 'GRout', 'AB1', 'Sball', 'Perm', 'Barom' ]
    cond = CONDITIONS(expected)  # a single instance for each separate build up
    rw1 = ['AH1', 29.1, 0.029]  # note the temp sd is 0.05/root 3, the digital resolution
    rw2 = ['AH2', 30.0, 0.029]
    rw3 = ['GRin', 24.893, 0.011]
    rw4 = ['GRout', 25.612, 0.021]
    rw5 = ['AB1', 20.05, 0.01]
    rw6 = ['Sball', 23.2, 0.1]
    rw7 = ['Perm', 23.21, 0.05]
    rw8 = ['Barom', 1032.0, 0.01]
    block = [rw1, rw2, rw3, rw4, rw5, rw6, rw7, rw8]
    cond.build_dict_from_block(block)
    print(cond.cond_dict)
    print(cond.cond_to_json())


