
KERNEL_PATH=/usr/local/share/jupyter/kernels
#echo "export PATH=/content/prism/bin:$${PATH}">>/.bashrc
sed -e "s#<path>#${KERNEL_PATH}#g" pyprism_kernel/kernel.tmpl.json > pyprism_kernel/kernel.json


