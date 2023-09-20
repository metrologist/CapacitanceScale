"""
dial_read.py is for manual entry of IVD dials that include a sign dial and digit settings from -1 to X.
The dial readings are then interpreted as a value with a nominal full scale value of 1. This can be used with the
10:1 capacitance bridge and the Universal Impedance Bridge.
"""


class READOUT(object):
    def __init__(self, pattern):
        """
        READOUT enables processing of the dial settings of inductive voltage dividers that can have overlapping dials
        with the settings of -1 and X as well as 0...9. It is more reliable to record the dials exactly as set rather
        than to risk an error when translating the dial settings to a number. This will facilitate a GUI interface
        for the direct entry of dial settings which will remove the need to transpose hand-written entries from a lab
        book.

        :param pattern: a dictionary {'number': n, 'input_style': 'xxxx_step', 'sign': boolean}
        """
        self.dial_patterns = {'sign': {'+': 1.0, '-': -1.0},
                              'ten_step': {'0': 0, '1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6,
                                           '7': 7, '8': 8, '9': 9},
                              'eleven_step': {'0': 0, '1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6,
                                              '7': 7, '8': 8, '9': 9, 'x': 10, 'X': 10},
                              'twelve_step': {'-1': -1, '0': 0, '1': 1, '2': 2,
                                              '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, 'x': 10, 'X': 10}}
        self.number_of_dials = pattern['number']  # includes the sign dial if there is one
        self.pattern = pattern
        if self.pattern['sign']:
            self.input_style = [self.dial_patterns['sign']]  # first dial is the sign
            self.start = 1  # iterate number dials over n-1
        else:
            self.input_style = []
            self.start = 0  # iterate number dials over n
        for i in range(self.number_of_dials - self.start):  # the rest are all, say, twelve_step
            self.input_style.append(self.dial_patterns[self.pattern['input_style']])  # an inefficient construction?

    def convert_input(self, dial_in):
        """
        An input method is required to generate the dial_in list.

        :param dial_in: a list of each individual dial setting entered as string
        :return: a floating point, depending of the dial pattern from 0.0 to +/- 1.111111
        """
        assert len(dial_in) == self.number_of_dials, 'wrong number of dials'
        dial_sign = False  # default to no sign dial
        if self.input_style[0] == self.dial_patterns['sign']:  # check if first dial is a sign dial
            factor = int(self.input_style[0][dial_in[0]])  # picks up the multiplying factor from the dictionary
            dial_sign = True  # have the factor to impose the sign
        dial_value = 0  # default start value that will be added to dial by dial to generate the final number
        for i in range(self.start, self.number_of_dials):
            assert dial_in[i] in self.input_style[i], 'dial setting does not match pattern'
            dial_value = dial_value + 10 ** -(i + (1 - self.start)) * self.input_style[i][dial_in[i]]
        if dial_sign:
            dial_value = dial_value * factor  # factor will already be defined if dial_sign is True
        return dial_value

    def terminal_input_by_dial(self):
        """
        Simple dial by dial entry from keyboard for testing

        """
        dial_in = []
        counter = 0
        for i in range(self.pattern['number']):
            prompt = 'enter dial #' + str(i) + ':  '
            dial_setting = input(prompt)
            while dial_setting not in self.input_style[counter]:
                prompt = 'try again dial #' + str(i) + ':  '
                dial_setting = input(prompt)
            dial_in.append(dial_setting)
            counter = counter + 1
        return self.convert_input(dial_in)

    def terminal_input_by_string(self):
        """
        Simple single string entry from keyboard for testing

        """
        prompt = ' enter all dials as string:  '
        dial_reading = input(prompt)
        return self.input_by_string(dial_reading)

    def input_by_string(self, some_input):
        """
        Checks that the input string can be sliced into valid dial settings consistent with the pattern. A boolean is
        returned so that a 'try again' dialogue can be managed. A successful list of the dial settings can be processed
        by the convert_input() method into a floating point dial value.

        :param some_input: a string representation of the dial setting
        :return: (list of dial setting strings (one for each dial), boolean True if parsing successful)
        """
        # need to check that final parsed string reassembles into the same length as the original!
        # check = False  # will be set to True if parsing is successful
        output = []  # a list of strings that each represent a single dial setting
        dial_reading = some_input
        pointer = 0
        if self.pattern['sign']:  # first character must be a sign
            if dial_reading[pointer] not in self.dial_patterns['sign']:  # first character must be "+" or "-"
                # check = False  # first character is not a sign
                return output, False
            output.append(dial_reading[pointer])
            pointer = pointer + 1  # points to next character to read
        while len(output) < self.number_of_dials:  # carry on until all the dial settings are found
            if self.pattern['input_style'] == 'twelve_step':  # now dealing with a non-signed dial
                # in a twelve_step a -1 setting is possible,but not,say, '-3' or - not followed
                x = slice(pointer, pointer + 2)
                if len(dial_reading[x]) == 2:  # i.e. not at the end of the string
                    if dial_reading[x][0] + dial_reading[x][1] == '-1':
                        output.append(dial_reading[x][0] + dial_reading[x][1])
                        pointer = pointer + 2
                    else:
                        x = slice(pointer, pointer + 1, 1)
                        output.append(dial_reading[x])
                        pointer = pointer + 1
            else:
                x = slice(pointer, pointer + 1, 1)
                output.append(dial_reading[x])
                pointer = pointer + 1
        # final check
        # check = False
        start = 0
        if self.pattern['sign']:
            start = 1  # first character already checked to be a sign
        for i in range(start, len(output)):
            if output[i] not in self.input_style[i]:
                check = False
                return output, False
        # check = True
        length_test=[]
        for x in output:
            for y in x:  # extracting characters
                length_test.append(y)
        if len(length_test) != len(some_input):  # checking all characters in the string are entered
            return output, False
        return output, True


if __name__ == '__main__':
    pattern_ivd_a = {'number': 7, 'input_style': 'twelve_step', 'sign': True}
    dial = ['-', '1', 'x', '-1', '5', 'X', '9']
    ivd_a = READOUT(pattern_ivd_a)
    print(ivd_a.convert_input(dial))
    pattern_ivd_b = {'number': 6, 'input_style': 'twelve_step', 'sign': False}
    ivd_b = READOUT(pattern_ivd_b)
    dial2 = ['1', 'x', '-1', '5', 'X', '9']
    print(ivd_b.convert_input(dial2))
    pattern_ivd_c = {'number': 6, 'input_style': 'eleven_step', 'sign': False}
    ivd_c = READOUT(pattern_ivd_c)
    dial3 = ['1', 'x', '2', '5', 'X', '9']
    print(ivd_c.convert_input(dial3))
    pattern_ivd_d = {'number': 7, 'input_style': 'eleven_step', 'sign': True}
    ivd_d = READOUT(pattern_ivd_d)
    dial4 = ['-', '1', 'x', '2', '5', 'X', '9']
    print(ivd_d.convert_input(dial4))
    # print(ivd_d.terminal_input_by_dial())
    # print(ivd_b.terminal_input_by_string())
    a_reading = ivd_b.input_by_string('-1X3x-16')
    print(a_reading, ivd_b.convert_input(a_reading[0]))
