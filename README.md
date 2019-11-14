# get_rax_name
Python script that gets a server name from a UUID in the Rackspace cloud

*Currently the script may not work correctly with UK accounts*


##Setting up 


I highly recommend setting up a [python virtual environment](https://docs.python.org/3/library/venv.html) before installing the 
python dependcies for this script. You can easily do this with the following:

#Create virtual environment
```
python3 -m venv <path-to-environemnt>

ex:

python3 -m venv ~/.rax

```
#Activate the environment
```
source <path-to-environemnt>/bin/activate

ex:

source ~/.rax/bin/activate 
```

Once your enviornment is setup you can install the requirements for this script using
the requirements file:

```
pip install -r requirments.txt
```


##How to use

The first time you run the script you will be prompted to enter your Rackspace cloud username and [API key](https://support.rackspace.com/how-to/view-and-reset-your-api-key). 
After this the script will automatically run. By default, the script will grab all servers in all regions, but you can specify a specific region or even a specific server UUID.
Please note that if you specify a UUID, you should also specify the region if you know it. The reason for this is that without a region the script will search all regions and 
that will take significantly longer considering it is single threaded. 

```
$ ./get_rax_name.py -h
usage: get_rax_name.py [-h] [-u UUID] [-c] [-r REGION]

Get a Rackspace server name with UUID

optional arguments:
  -h, --help            show this help message and exit
  -u UUID, --uuid UUID  Rackspace server UUID
  -c, --configure       Configure the Rackspace username and api key
  -r REGION, --region REGION
                        Select specific region e.g. dfw, ord, iad

```

