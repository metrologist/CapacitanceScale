A testing framework is required. To date code following if __name__ == '__main__': has been relied on to confirm
performance, but this is not sufficiently robust for future development.

The components module (CAPACITOR and LEAD classes) can be improved with the addition of

•	temperature, pressure and humidity (in the case of high frequency air capacitors) coefficients,
•	specific uncertainties for each of the admittances and impedances that comprise the full model (not just 'relu'),
•	possible frequency dependent behaviour for some components (beyond assuming constant C and G over a narrow frequency range),
•	time dependence of capacitance values at a level suitable for predicting values between calibrations.

Once this capacitance scale process has been exercised a few more times it might be beneficial to set up a GUI for both
analysis and direct gathering of the data (remembering to ensure that the GUI is always an optional way of running the
process, leaving the basic data structure unchanged).