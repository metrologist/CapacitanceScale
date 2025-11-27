# see https://stackoverflow.com/questions/49503869/attributeerror-while-trying-to-load-the-pickled-matplotlib-figure
import pickle
# import dill
import matplotlib.pyplot as plt
from matplotlib import _pylab_helpers

# Load the pickled figure
file_name = 'GR and S ball set.pkl'
with open(file_name, 'rb') as f:
    my_fig = pickle.load(f)  # Deserialize the figure
# make sure plt has set a backend and get it
bem = plt._get_backend_mod()
# create a new figure manager for our figure
mgr = bem.new_figure_manager_given_figure(num=my_fig.number, figure=my_fig)
# set the new figure manager as active
_pylab_helpers.Gcf.set_active(mgr)
plt.show(block=True)