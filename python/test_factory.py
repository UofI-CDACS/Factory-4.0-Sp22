
"""This module tests the runability of factory.py"""

import logging
from time import sleep

import utilities
from job_data import JobData
from factory.factory import FACTORY

logger = logging.getLogger()
logger.setLevel(logging.DEBUG) # sets default logging level for this module

# Create formatter
#formatter = logging.Formatter('[%(asctime)s] [%(levelname)-5s] [%(name)s] [%(threadName)s] - %(message)s')
formatter = logging.Formatter('[%(asctime)s] [%(levelname)-5s] [%(name)s] - %(message)s')

# Logger: create console handle
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)     # set logging level for console
ch.setFormatter(formatter)
logger.addHandler(ch)


logging.getLogger("pymodbus").setLevel(logging.INFO)

def main():
    logger.info("Starting test factory")
    config = utilities.load_env()
    f = FACTORY(config['FACTORY_IP'], config['FACTORY_PORT'])
    logger.info("Initialized")
    

    f_status = f.status()

    
    logger.info("Factorystatus %s", f_status)
    
# 1.)  Process order.  Original job_type processing a puck through the factory from the HBW and delivering to the loading bay.
    job_data = JobData(job_id=254, order_id=100, color='blue', cook_time=5, sliced=False, job_type = 1)
    job_data.add_slot((1,3,0,0))

# 2.) Restock from loading bay test, blue pallet on row 1 column 3 should be empty before starting and should be a puck in the loading bay.  
# This could for example be run after running the standard job_type = 1 example above
#    job_data = JobData(job_id=254, order_id=100, color='blue', cook_time=12, sliced=True, job_type = 2)
#    job_data.add_slot((1,3,0,0))

# 3.) Load train test, just need a puck in the loading bay and the black flat cargo car on the train should be roughly in line with 
#  the loading bay with the track about a 0.25" from the base of the mini-factory. 
#    job_data = JobData(job_id=254, order_id=100, color='blue', cook_time=12, sliced=True, job_type = 3)
#    job_data.add_slot((1,3,0,0))

# 4.) Restock from train test, blue pallet on row 1 column 3 should be empty before starting and best to run load train first so puck is 
# in approximately the right location
#    job_data = JobData(job_id=254, order_id=100, color='blue', cook_time=12, sliced=True, job_type = 4)
#    job_data.add_slot((1,3,0,0))

# 5.) Sort puck test
#    job_data = JobData(job_id=254, order_id=100, color='blue', cook_time=12, sliced=True, job_type = 5)
#    job_data.add_slot((2,3,2,2))
    
    if f_status == 'ready':
        f.order(job_data)
        f.update()
        sleep(2)
    else:
        logger.error("Factory not ready")
        return 1
    
    status = ""
    while status != 'ready':
        status = f.status()
        logger.info("Factory Status: %s", status)
        f.update()
        sleep(1)
        


if __name__ == "__main__":
    main()
