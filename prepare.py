import os
import subprocess
import logging
import tarfile
from time import sleep
import urllib.request

# Some basic initializations:
########
local_path = os.path.dirname(os.path.abspath(__file__))
images_url = 'https://s3.eu-central-1.amazonaws.com/devops-exercise/pandapics.tar.gz'
images_tar_file = local_path + '/' + images_url.split('/')[-1]
health_url = 'http://localhost:3000/health'
timeout = 2
time_retries = 3

# Init logger (globally)
log = logging.getLogger('prepare.py')


def config_logger():
    # Create handlers
    c_handler = logging.StreamHandler()
    f_handler = logging.FileHandler('prepare.log')
    c_handler.setLevel(logging.INFO)
    f_handler.setLevel(logging.INFO)  # Should be set higher - set here for verbosity during debugging

    # Create formatter
    c_format = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
    f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    c_handler.setFormatter(c_format)
    f_handler.setFormatter(f_format)

    # Add handlers to the logger
    log.addHandler(c_handler)
    log.addHandler(f_handler)

    # Set general logging level
    log.setLevel(logging.INFO)


def download_image_file(url, file_name):
    # Download the file and save it locally under `file_name`:
    ########
    log.info('Images archive will placed in: ' + file_name)
    with urllib.request.urlopen(url) as response, open(file_name, 'wb') as out_file:
        data = response.read()
        out_file.write(data)


def extract_tar(file_name, destination):
    # Extract downloaded file into images directory:
    ########
    tgzFile = tarfile.open(images_tar_file, 'r:*')
    tgzFile.extractall(destination)
    log.info(file_name + ' contains:')
    for name in tgzFile.getnames():
        log.info(name)
    log.info('extracting to: ' + destination)
    tgzFile.close()


def remove_file(file_name):
    log.info("Deleting file: " + file_name)
    os.remove(file_name)


def up_docker_compose():
    # Launch the docker environment using docker-compose (fail if anything goes wrong):
    # split into two stages for ease of localizing problems
    ########
    subprocess.run(['docker-compose', 'build'], check=True)
    subprocess.run(['docker-compose', 'up', '-d'], check=True)


def health_check():
    # Healthcheck status check:
    ########
    check_result = 0

    for x in range(0, time_retries):
        try:
            healthStatus = urllib.request.urlopen(health_url).getcode()
            if healthStatus != 200:
                log.error('Wooohaaa!! something went wrong...')
            else:
                log.info('Everything seems randy dandy :-)')
                check_result = 1
                break

        except Exception as e:
            if type(e) != ConnectionResetError:  # For more 'exotic' exceptions
                log.exception(e)
            if x != time_retries:
                log.warning('Service might not be ready yet...')
                log.warning('Attempting a timeout wait (retry {} of {}) - sleeping {} seconds.'.format(x + 1, time_retries, timeout))
                sleep(timeout)
                log.warning('Retrying...')
    else:
       log.error('Attempts timed out - connecting with service health check failed.')

    return check_result


def down_docker_compose():
    # Shut down docker environment using docker-compose
    # (assuming deployment flow should finish with shutdown after checking all is ok)
    ########
    log.info('Bringing down docker-compose container environment...')
    subprocess.run(['docker-compose', 'down'], check=True)


def main():
    exit_code = 1
    config_logger()
    log.info('== STARTING deployment flow script ==')

    try:
        download_image_file(images_url, images_tar_file)
        extract_tar(images_tar_file, local_path + '/public/images')
        remove_file(images_tar_file)
        up_docker_compose()
        if health_check():
            log.info('Deployment flow SUCCEEDED')
            exit_code = 0
        else:
            log.error('Deployment flow FAILED.')
            down_docker_compose()
    except Exception as e:
        log.error(e)
        log.error('Deployment flow FAILED.')
        down_docker_compose()

    finally:
        log.info('== FINISHED deployment flow script ==')

    exit(exit_code)


main()
