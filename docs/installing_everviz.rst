******************
Installing Everviz
******************
*Everviz* is a plugin of *Everest*, and therefore *Everest* must be installed in the same Python enviroment before you install *Everviz*. 

*Everviz* is based on `Webviz <https://github.com/equinor/webviz-config>`_, which must be installed before installing *Everviz*.

After installing these prerequisites, the easiest way of installing *Everviz* is to run:

.. code-block:: console

    pip install everviz

If you want to download the latest source code and install it manually use the following commands:

.. code-block:: console

    git clone git@github.com:equinor/everviz.git
    cd ./everviz
    pip install .

After installation *Everviz* can be started from the *Everest* tool.