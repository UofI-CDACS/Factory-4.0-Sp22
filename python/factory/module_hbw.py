"""Factory Module: High Bay Warehouse """

from factory.register import REGISTER   # Modbus Register
from factory.bit import BIT             # Modbus Bit
from time import sleep

#*****************************
#*           HBW             *
#*****************************
class HBW():
    name = "HBW"
    def __init__(self, modbus):
        self.Task1 =        BIT(1, modbus) # Send
        self.Task2 =        BIT(2, modbus) # Receive
        self.Task3 =        BIT(3, modbus) # Reset
        self.Task4 =        BIT(3, modbus) # Sort
        self.Task5 =        BIT(3, modbus) # Manual Mode
        self.row =       REGISTER(1, modbus) # row
        self.column =       REGISTER(2, modbus) # column
        self.row_new = REGISTER(3, modbus) # row new (sort)
        self.column_new = REGISTER(4, modbus) # column new (sort)
        
        # Outputs from PLC
        self.status_ready = BIT(100, modbus)
        self.status_fault = BIT(101, modbus)
        self.cur_progress = REGISTER(100, modbus)
        self.fault_code   = REGISTER(101, modbus)

    def IsReady(self):
        """ Return True if module is in a ready state """
        print("HBW ready status")
        print(self.status_ready.read())
        return self.status_ready.read()

    def IsFault(self):
        """ Return True if module is in a fault state """
        return self.status_fault.read()

    def CurrentProgress(self):
        """ Return the current task progress
        Returns integer between 0 and 100
        """
        return self.cur_progress.read()

    def StartTask1(self, x, y):
        """ Start Task 1
        Deliver Pallet to conveyor factory side
        """
        self.row.write(x)
        self.column.write(y)
        #Set task one and clear it (simuler to pressing HMI button)
        self.Task1.set()
        print("task 1 running and has row, column", x, y)
        sleep(0.5)
        return 1

    def StartTask2(self, x, y):
        """ Start Task 2
        Retrieve Pallet from conveyor factory side and load on HBW
        """
        self.row.write(x)
        self.column.write(y)
        #Set task two and clear it (simuler to pressing HMI button)
        self.Task2.set()
        sleep(0.25)
        self.Task2.clear()
        return 1
    def StartTask3(self, row_start, column_start, row_finish, column_finish):
        """ Start Task 3
        Task 1 must be called first to clear a HBW slot, then this function could be
        called to relocate pallet for sorting/shuffling operations.
        """
        self.row.write(row_start)
        self.column.write(column_start)
        self.row_relocate.write(row_finish)
        self.column_relocate.write(column_finish)
        #Set task two and clear it (simuler to pressing HMI button)
        self.Task3.set()
        sleep(0.25)
        self.Task3.clear()
        return 1

    def HBW_Status(self):
        """ Show bit & register statuses """
        print("************************")
        print("*      HBW STATUS      *")
        print("************************")
        print("*Task1: "+str(self.Task1.read()))
        print("*Task2: "+str(self.Task2.read()))
        print("*Task3: "+str(self.Task3.read()))
        print("*slot_x: "+str(self.row.read()))
        print("*slot_y: "+str(self.column.read()))
        print("*status_ready: "+str(self.status_ready.read()))
        print("*cur_progress: "+str(self.cur_progress.read()))
        print("*status_fault: "+str(self.status_fault.read()))
        print("*fault_code: "+str(self.fault_code.read()))
        print("************************")
