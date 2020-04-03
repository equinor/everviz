***************
Running Everviz
***************

*Everviz* is a plugin of *Everest* and is run using the `results` sub-command of *Everest*:

.. code-block:: console

    everest results config_file.yaml

where ``config_file.yaml`` must be the configuration file that was used to run the optimization.

The *Everviz* web interface will open in a browser, allowing you to select several pages as described in the following sections.

Controls
========
In this section two plots are shown. The first allows you to plot the control values as a function of the batch number, to see how they evolve during the optimization. The second plot plots all control values for two batches: the first batch, and the batch that corresponds to the best objective function value.

Objectives
==========
This section shows a plot of the objective function values as a function of the batch number. The simulations generally exist of a large set of realizations at each batch. By default, the mean over the realizations is plotted with the range between the P10 and P90 percentile values plotted as a shaded area. Alternatively, you can plot all individual realizations as separate points. Choose between these options by using the ``Statistics`` and ``Data`` radio buttons.

Summary Values
==============
Summary values are different from control and objective function values, since they consists of time series. At these page two plots are shown: the first plots the summary values as a function of time, where you must select on or more summary keys and batch numbers to plot. The second plots summary values as a function of the batch number, where you choose one or more summary keys and dates to plot. As with the objective values, summary keys are the results of many realizations, and therefore you can again choose between plotting the mean with an P10-P90 interval, or plotting all realizations as individual points.

Cross plots
===========
Cross plots allow you to plot any arbitrary value in the optimization resuls against any arbitrary other value.

Everviz configuration
=====================
This page shows the configuration file that is used to generate all the plots.