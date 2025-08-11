# tc-interview-problem-python-deps

Your primary task will be to implement some Python dependency management features to this codebase. This code
repository has the following structure:

```
tc-interview-problem-python-deps
├── .git
├── .gitignore
├── Dockerfile
├── Makefile
├── README.md
├── apps
│   ├── job-a
│   │   ├── Dockerfile
│   │   └── app.py
│   ├── job-b
│   │   ├── Dockerfile
│   │   └── app.py
│   ├── job-c
│   │   ├── Dockerfile
│   │   └── app.py
│   ├── server-one
│   │   ├── Dockerfile
│   │   └── app.py
│   └── server-two
│       ├── Dockerfile
│       └── app.py
├── lib
│   └── verse
│       └── common.py
├── pyproject.toml
├── scripts
│   └── main.py
├── static_data
│   ├── enron_emails_1702.csv
│   └── LD2011_2014.csv
└── tests
    ├── test_runtime.py
    └── verse
        └── test_common.py
```

To start things off, please complete the following setup steps:


## Python Environment


(verse-dev-3.11.9) (base) luisgonzalez@Luiss-MacBook-Air pydeps-takehome-aiota % pyenv versions
  system
  3.11.9
  3.11.9/envs/verse-dev-3.11.9
* verse-dev-3.11.9 --> /Users/luisgonzalez/.pyenv/versions/3.11.9/envs/verse-dev-3.11.9 (set by PYENV_VERSION environment variable)


### Pre-setup

TODO: paste the result of the following command immediately below for your active Python runtime
```
python --version
which python
```

### Python Versions

TODO: please paste all the versions of Python you have installed, e.g. if you have `pyenv` installed you can obtain
this with `pyenv versions`


## Coding Assignment

Files added:
  
  - requirements.txt
  - /job-a/requirements.txt
  - /job-b/requirements.txt
  - /job-c/requirements.txt
  - /server-one/requirements.txt
  - /server-two/requirements.txt
  - /scripts/AlignDependencies.py
  - /scripts/DownloadFile.py
  - /server-three/app.py, Dockerfile, requirements.txt, service.proto


## Running this assignment

1. Download data
  - Run python scripts/main.py

  Downloads the static_data
  Upgrades the base dependencies if alignment is possible.


  Reasoning on dependencies manager class:
    The purpose of the DependenciesManager is to manage and validate dependency upgrades across multiple applications within a monorepo.
    
    Since the base dependencies are already defined in pyproject.toml, we can use this as the foundation.
    
    When evaluating an upgrade—for example, updating numpy from version 2.1.1 to 2.3.0—we simulate the change by modifying only the target package version while keeping the rest of the dependencies intact.
    
    The updated environment is then validated by:
	  	Building a Docker image for each app with the new dependency version.
	  	Running the container to ensure the app starts and functions without error.
	  
    If the build and runtime succeed without exceptions, we consider the new dependency version valid for that app.
    
    Alignment is achieved when all apps within the monorepo (i.e., len(apps)) successfully build and run with the proposed dependency version. At that point, the new version can be recorded or promoted to pyproject.toml.
    

2. Bulding the python-base
  * Since the align_python_deps() function updates the base after alignment is complete, this step is not needed*
  - make build-base

3. Build jobs, servers...
  - make build job-a
  - make build all

# Note: tags are python-{$apps-dir-name}
4. Running the jobs, servers...
  - docker run -p 8000:8000 python-{job-a}
  - docker run -p 8000:8000 python-{server-one} 



# Testing
  * Test the base tests path
  - make test-base
  * Test the jobs and servers
  - make test job-a .. 
  * Test all jobs
  - make test all

  

# gRPC server-three
  grpcurl required to test out this endpoint.  Install direclty using Go, apt(ubuntu), homebrew(mac).. 
  To run:
  - docker run -p 8080:5000 ptyhon-server-three
  To test endpoint
  - grpcurl -plaintext -d '{"msg": "Hello world"}' localhost:8080 demo.v1.VerseService/Echo
  - grpcurl -plaintext -d '{}' localhost:8080 demo.v1.VerseService/GetMemory