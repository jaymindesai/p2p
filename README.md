# Peer to peer system with distributed index (P2P-DI)

## Run dev mode

Clone this repo : 

```bash
git clone git@github.ncsu.edu:pmgaikwa/p2p p2p

# switch to directory
cd p2p
```

Install virtualenv on your box :

```bash
pip --user install virtualenv
```

Create virtualenv :

```bash
# create virtualenv
virtualenv --python=<path_to_python_3.7_executable> venv		# starts a virtualenv in "p2p" directory
```

Build in dev mode : 

```bash
# change to deploy directory
cd ./deploy

# build the project
./build.sh
```

Start virtualenv : 

```bash
# change to p2p (project root) directory
cd ../

# start venv
source venv/bin/activate
```

Run tests :

```bash
# switch to tests directory
cd ./tests/

# run RS tests
python rs.py

# run protocol tests
python proto.py
```

#### Run RegistrationServer

```bash
# change to RS directory
cd ./p2p/rs/

# run server
python rs.py
```





