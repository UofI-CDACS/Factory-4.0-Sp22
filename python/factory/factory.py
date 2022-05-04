
import time
import logging
import threading

# Import factory modules
from factory.modbus import MODBUS       # Modbus communication client
from factory.module_hbw import HBW      # Mini-Factory module: High Bay Warehouse
from factory.module_vgr import VGR      # Mini-Factory module: Vacume Gripper Robot
from factory.module_mpo import MPO      # Mini-Factory module: mpo??
from factory.module_sld import SLD      # Mini-Factory module: sld
from factory.module_ssc import SSC_LED  # Mini-Factory module: ssc
from factory.module_ssc_webcam import SSC_Webcam      # Mini-Factory module: SSC Webcam



#*****************************
#*         FACTORY           *
#*****************************
class FACTORY():
    def __init__(self, ip, port):
        # Setup Logger
        self.logger = logging.getLogger("Factory")
        self.logger.setLevel(logging.DEBUG) # sets default logging level for module

        self.logger.info("Factory Initializing...")

        # Setup Modules
        self._mb = MODBUS(ip, port)
        self._hbw = HBW(self._mb)
        self._vgr = VGR(self._mb)
        self._mpo = MPO(self._mb)
        self._sld = SLD(self._mb)
        self._ssc = SSC_LED(self._mb)
        self._ssc_webcam = SSC_Webcam(self._mb)

        #check ready status
        self._status_details = None
        self.status()

        # Factory processing variables
        self._factory_state = 'ready'       # Status of the factory
        self._processing_thread = None      # Tread object when active
        self._job_data = None               # Holds job data such as x, y, cook time and slice info

        self.logger.debug("Factory Modbus Initialized")

    def status(self):
        """ Test each module and return a factory status
        Tests each module's fault and ready flags
        Generate a status_detailed dictionary object
        Return factory status string
        """
        factory_status = 'offline'
        modules = [self._hbw, self._vgr, self._mpo, self._sld]

        # Test if online
        self._mb.connection_check()

        # Test each module
        modules_ready_status = []
        modules_faulted_status = []
        modules_statuses = []
        for module in modules:
            module_faulted = module.IsFault()
            module_ready = module.IsReady()

            # Add to lists
            modules_faulted_status.append(module_faulted)
            modules_ready_status.append(module_ready)

            # Module summary (Module name, module faulted, module ready)
            modules_statuses.append((module.name, module_faulted, module_ready))

        # if any module is faulted, Factory is in Fault state
        # if all modules are ready, Factory is in a ready state
        if any(modules_faulted_status):
            factory_status = 'fault'
        elif all(modules_ready_status):
            factory_status = 'ready'
        else:
            factory_status = 'processing'

        # Detailed status report
        self._status_details = {'factory_status': factory_status,          # Factory status
                                'modules_faulted': modules_faulted_status, # List of bools of faulted modules
                                'modules_ready': modules_ready_status,     # List of bools of ready modules
                                'modules_statuses': modules_statuses }     # List: module_name, faulted, ready

        return factory_status

    def status_detailed(self):
        """ Calls Factory.status() and returns detailed information """
        self.status()
        return self._status_details


    def update(self):
        """
        This function should be called periodically every 1-5 seconds
        This checks the factory state and starts jobs as needed
        """
        if self._factory_state == 'ready':
            if self._job_data is not None:
                # Start job
                self.logger.info("Factory starting processing of a job")
                self._factory_state = 'processing'

                # Start thread
                self.logger.info("Starting processing thread")
                if self._job_data.job_type == 1:
                    self._processing_thread = threading.Thread(target=self.process_order)
                    self._processing_thread.start()
                elif self._job_data.job_type == 2:
                    self._processing_thread = threading.Thread(target=self.restock_from_loading_bay)
                    self._processing_thread.start()      
                elif self._job_data.job_type == 3:
                    self._processing_thread = threading.Thread(target=self.load_train)
                    self._processing_thread.start()  
                elif self._job_data.job_type == 4:
                    self._processing_thread = threading.Thread(target=self.restock_from_train)
                    self._processing_thread.start()
                elif self._job_data.job_type == 5:
                    self._processing_thread = threading.Thread(target=self.warehouse_sort)
                    self._processing_thread.start()
                    
        elif self._factory_state == 'processing':
            self.logger.debug("Factory processing an order")
            if not self._processing_thread.is_alive():
                self.logger.info("Job completed")
                self._factory_state = 'ready'

        elif self._factory_state == 'offline':
            self.logger.debug("Factory is offline")

        elif self._factory_state == 'fault':
            self.logger.debug("Factory in fault state")


        else:
            raise Exception("Invalid factory_state set")

        return self._factory_state
        
    def order(self, job_data):
        """ Load processing job order """
        if self._factory_state == 'ready':
            self.logger.info("Factory importing job data")
            self._job_data = job_data
            return 0
        else:
            self.logger.error("Factory not ready. Not accepting job")
            return 1
    def warehouse_sort(self):
        # Parse Job data
        row_index = self._job_data.slot_x
        column_index = self._job_data.slot_y
        row_index_sort = self._job_data.slot_x_sort
        column_index_sort = self._job_data.slot_y_sort
        cook_time = self._job_data.cook_time
        do_slice = self._job_data.sliced
        self.logger.info("Factory process started")
        self.logger.debug("Row: %d, Column: %d", row_index, column_index)
        def stage_1(row_index_sort, column_index_sort, row_index, column_index):
            print("Stage 1 entered")
            hbw_ready_status = self._hbw.IsReady()
            # Run _hbw
            if hbw_ready_status == True:
                print("_hbw Is Ready")
                self._hbw.StartTask1(row_index, column_index) #_hbw STARTS
            else:
                print("_hbw Is Not Ready")
            # Run _vgr and _hbw return
            while True:
                hbw_ready_status = self._hbw.IsReady()
                if hbw_ready_status == True:
                    self._hbw.StartTask4(row_index_sort, column_index_sort, row_index, column_index, ) 
                    break
                time.sleep(0.1)
        def stage_2(row_index_sort, column_index_sort):
            print("Stage 2 entered")
            while True:
                hbw_ready_status = self._hbw.IsReady()
                if hbw_ready_status == True:
                    self._hbw.StartTask2(row_index_sort, column_index_sort) 
                    break
                time.sleep(0.1)
            while True:
                hbw_ready_status = self._hbw.IsReady()
                if hbw_ready_status == True:
                    break
                time.sleep(0.1)
        stage_1(row_index_sort, column_index_sort, row_index, column_index)
        stage_2(row_index_sort, column_index_sort)
        
    def restock_from_train(self):
        # Parse Job data
        row_index = self._job_data.slot_x
        column_index = self._job_data.slot_y
        cook_time = self._job_data.cook_time
        do_slice = self._job_data.sliced
        print("row index is:", row_index)       
        print("column index:", column_index)
        self.logger.info("Factory process started")
        self.logger.debug("Row: %d, Column: %d", row_index, column_index)

        def stage_1(row_index, column_index):
            """
            Stage 1
            _hbw -> _vgr -> _mpo also _hbw return pallet
            """
            print("Stage 1 entered")
            hbw_ready_status = self._hbw.IsReady()
            self._vgr.Reset.set() #home position to reset encoder values
            # Run _hbw
            if hbw_ready_status == True:
                print("_hbw Is Ready")
                self._hbw.StartTask1(row_index, column_index) #_hbw STARTS
            else:
                print("_hbw Is Not Ready")
            # Run _vgr and _hbw return
            while True:
                hbw_ready_status = self._hbw.IsReady()
                vgr_ready_status = self._vgr.IsReady()
                if hbw_ready_status == True and vgr_ready_status == True:
                    self._vgr.StartTask6() 
                    break
                time.sleep(0.1)
        def stage_2(row_index, column_index):
            while True:
                vgr_ready_status = self._vgr.IsReady()
                if vgr_ready_status == True:
                    self._vgr.StartTask9() 
                    break
                time.sleep(0.1)
            while True:
                vgr_ready_status = self._vgr.IsReady()
                if vgr_ready_status == True: 
                    self._hbw.StartTask2(row_index, column_index)#Return Pallet
                    break
                time.sleep(0.1)
        
        stage_1(row_index, column_index)
        stage_2(row_index, column_index)
        time.sleep(1)
        
    def load_train(self):
        # Parse Job data
        self.logger.info("Factory process started")
        
        def stage_1():
            """
            Stage 1
            _hbw -> _vgr -> _mpo also _hbw return pallet
            """
            print("Stage 1 entered")
            vgr_ready_status = self._vgr.IsReady()
            # Run _hbw
            if vgr_ready_status == True:
                print("_vgr Is Ready")
                self._vgr.StartTask5() #_hbw STARTS
                time.sleep(0.5)
            else:
                print("_vgr Is Not Ready")
                
            # Run _vgr and _hbw return
            while True:
                vgr_ready_status = self._vgr.IsReady()
                if vgr_ready_status == True:
                    self._vgr.StartTask10() 
                    time.sleep(0.5)
                    break
                time.sleep(0.1)
                            # Run _vgr and _hbw return
            while True:
                vgr_ready_status = self._vgr.IsReady()
                if vgr_ready_status == True:
                    self._vgr.Reset.set() 
                    time.sleep(0.5)
                    break
                time.sleep(0.1)
        
        stage_1()
                
    def restock_from_loading_bay(self):
        # Parse Job data
        row_index = self._job_data.slot_x
        column_index = self._job_data.slot_y
        cook_time = self._job_data.cook_time
        do_slice = self._job_data.sliced
        print("row index is:", row_index)       
        print("column index:", column_index)
        self.logger.info("Factory process started")
        self.logger.debug("Row: %d, Column: %d", row_index, column_index)
        
        def stage_1(row_index, column_index):
            """
            Stage 1
            _hbw -> _vgr -> _mpo also _hbw return pallet
            """
            print("Stage 1 entered")
            hbw_ready_status = self._hbw.IsReady()
            self._vgr.Reset.set() #home position to reset encoder values
            # Run _hbw
            if hbw_ready_status == True:
                print("_hbw Is Ready")
                self._hbw.StartTask1(row_index, column_index) #_hbw STARTS
                time.sleep(1)
            else:
                print("_hbw Is Not Ready")
            # Run _vgr and _hbw return
            while True:
                hbw_ready_status = self._hbw.IsReady()
                vgr_ready_status = self._vgr.IsReady()
                if hbw_ready_status == True and vgr_ready_status == True:
                    self._vgr.StartTask5() 
                    time.sleep(0.5)
                    break
                time.sleep(0.1)
        def stage_2(row_index, column_index):
            while True:
                vgr_ready_status = self._vgr.IsReady()
                if vgr_ready_status == True:
                    self._vgr.StartTask9() 
                    time.sleep(0.5)
                    break
                time.sleep(0.1)
            while True:
                vgr_ready_status = self._vgr.IsReady()
                if vgr_ready_status == True: 
                    self._hbw.StartTask2(row_index, column_index)#Return Pallet
                    time.sleep(0.5)
                    break
                time.sleep(0.1)
        
        stage_1(row_index, column_index)
        stage_2(row_index, column_index)
        
    def process_order(self):
        """ Main order sequence for factory
        Expects self._job_data to be populated
        """
        # Parse Job data
        row_index = self._job_data.slot_x
        column_index = self._job_data.slot_y
        cook_time = self._job_data.cook_time
        do_slice = self._job_data.sliced
        print("row index is:", row_index)       
        print("column index:", column_index)
        self.logger.info("Factory process started")
        self.logger.debug("Row: %d, Column: %d", row_index, column_index)

        def stage_1(row_index, column_index):
            """
            Stage 1
            _hbw -> _vgr -> _mpo also _hbw return pallet
            """
            print("Stage 1 entered")
            hbw_ready_status = self._hbw.IsReady()
            # Run _hbw
            if hbw_ready_status == True:
                print("_hbw Is Ready")
                self._hbw.StartTask1(row_index, column_index) #_hbw STARTS
                time.sleep(.25)
            else:
                print("_hbw Is Not Ready")

            # Run _vgr and _hbw return
            while True:
                hbw_ready_status = self._hbw.IsReady()
                if hbw_ready_status == True:
                    self._vgr.StartTask1() 
                    time.sleep(1)
                    break
                time.sleep(0.1)
                
            while True:
                vgr_ready_status = self._vgr.IsReady()
                if vgr_ready_status == True: 
                    self._hbw.StartTask2(row_index, column_index)#Return Pallet
                    self._vgr.StartTask7()
                    time.sleep(1)
                    break
                time.sleep(0.1)
            
            while True:
                vgr_ready_status = self._vgr.IsReady()
                # Wait until VGR has dropped puck in MPO
                if vgr_ready_status == True:
                    break
                time.sleep(0.1)

        def stage_2():
            """
            Stage 2
            """
            print("Stage 2 entered")
            mpo_ready_status = self._mpo.IsReady()
            # Run _hbw
            if mpo_ready_status == True:
                print("_mpo Is Ready")

                self._mpo.cook_time.write(cook_time)
                self. _mpo.saw_status.write(do_slice)

                self._mpo.StartTask1() 
                print("mpo task 1 started")
                time.sleep(1)
            else:
                print("_hbw Is Not Ready")
                
            while True:
                # Currently MC450, MPO_Task1, resets after puck put in white red blue slot in SLD and this is used as metric for done
                # This can be further defined later to give factory.py better visibility of where the puck is, etc.
                # This is now tied to MC 820 which will indicate if the SLD is done
                sld_done = self._mpo.Task1.read()
                if self._mpo.sld_done.read() == False:
                    print("Puck ready for pickup")
                    if column_index == 1: #red puck
                        self._vgr.StartTask3()
                    elif column_index == 2: #white puck
                        self._vgr.StartTask2()
                    elif column_index == 3:  #blue puck
                        self._vgr.StartTask4()
                    time.sleep(1)
                    break
                time.sleep(0.1)    

        def stage_3():
            """
            Stage 3
            """
            print("Stage 3 entered")
            while True:
                vgr_ready_status = self._vgr.IsReady()
                if vgr_ready_status == True:
                    self._vgr.StartTask8() # deliver puck to Loading Bay
                    time.sleep(1)
                    break
                time.sleep(0.1)

        stage_1(row_index, column_index)
        stage_2()
        stage_3()
        self._job_data = None # Clear job data that just completed
        return


#*****************************
#*           MAIN            *
#*****************************
if __name__ == '__main__':
    #Main is not used
    print("******************************")
    print("* start factory with         *")
    print("* $python3 pyController.py   *")
    print("*            or              *")
    print("* $python3 test_factory.py   *")
    print("******************************")
