# PyPRISM: PRISM Python interface


## Installation of PyPRISM
 
The PRISM included in this repository is from Ubuntu's recommended environment,
please overwrite `pyprism/bin` if you want to use the one in your own environment.
Note that the PRISM binary in this repository have been compiled and may not work well in other environments.


After that, please execute the following commands in this directory:
```
pip install .
```

## Installation of Jupyte notebook kernel for PRISM

```
mkdir -p  ~/.ipython/kernels/prism/
cp pyprism_kernel/kernel.py  ~/.ipython/kernels/prism/
```

For checking
```
sed -e "s#<path>#$(dirname ~/.ipython/kernels/prism/kernel.py)#g" pyprism_kernel/kernel.tmpl.json
```

To save the kernel.json
```
sed -e "s#<path>#$(dirname ~/.ipython/kernels/prism/kernel.py)#g" pyprism_kernel/kernel.tmpl.json >  ~/.ipython/kernels/prism/kernel.json
```


Set the environment variable PATH so that you can use the prism command.
If you already have the prism command available, you don't need to run this command.
```
export PATH=$PATH:$(pwd)/pyprism/bin/prism

```

Finally, please launch the jupyter notebook:
```
jupyter notebook
```

## Build

"""
python setup.py bdist_wheel
"""

