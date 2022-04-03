# PyPRISM: PRISM Python interface


## Installation of PyPRISM
 
The PRISM included in this repository is from Ubuntu's recommended environment,
please overwrite `pyprism/bin` if you want to use the one in your own environment.
The PRISM source code and binary can be downloaded from https://github.com/prismplp/prism .
Note that the default PRISM binary in this repository have been compiled for the Google Colaboratory and may not work well in other environments.


After that, please execute the following commands in this directory:
```
pip install -U git+https://github.com/kojima-r/pyprism.git
```

You can see examples of installation and usage of PyPRISM using Google Colaboratory from the link below:
https://drive.google.com/drive/folders/13wYs_eKxjNg2bmcagYkMNtX9t86Ddlcc?usp=sharing

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


