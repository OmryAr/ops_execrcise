# Welcome to ops_exercise!
…where a solved exercise for a certain grand-bear-bearing corporation resides :-)

# Things to know:
- Contains the following files (and associated requirements):
   * prepare.py  -- deployment flow script, tested with Python 3.5
   * docker-compose.yml  -- docker-compose configuration file, tested with docker-compose v1.23.2

- Designed to be placed in the exercise application's root directory and executed using 'python3 prepare.py'.
 
- Assumes a successful deployment leaves the containers running, while an unsuccessful one brings everything down.

- A log file (prepare.log) is created with all script messages. For convenience logging is also streamed to STDOUT.

- Script exit codes:
  * 1 - deployment flow failed (see logfile for details)
  * 0 - deployment flow succeeded

- As part of the healthcheck stage of the script, several polling attempts might take place, in order to allow the application reasonable time to start up. Adjust parameters (timeout, time_retrys) in the initialization section of the script as needed.

- TODOs: more generalized functions (for future reuse in other case scenarios), more elegant error handling, better log formatting, etc.


