

from factory.register import REGISTER   # Modbus Register
from factory.bit import BIT             # Modbus Bit
from time import sleep

#*****************************
#*            VGR            *
#*****************************
class VGR():
    name = "VGR"
    def __init__(self, modbus):
        self.Reset =        BIT(200, modbus) # Reset
        self.Task1 =        BIT(201, modbus) # Pickup disk HBW
        self.Task2 =        BIT(202, modbus) # Pickup disk SLD white
        self.Task3 =        BIT(203, modbus) # Pickup disk SLD red
        self.Task4 =        BIT(204, modbus) # Pickup disk SLD blue
        self.Task5 =        BIT(205, modbus) # Pickup disk Loading Bay
        self.Task6 =        BIT(206, modbus) # Pickup disk Train
        self.Task7 =        BIT(207, modbus) # Deliver disk MPO
        self.Task8 =        BIT(208, modbus) # Deliver disk Loading Bay
        self.Task9 =        BIT(209, modbus) # Deliver disk HBW
        self.Task10 =       BIT(210, modbus) # Deliver disk Train
        self.Manual_control  = BIT(220, modbus)
        # Output from the factory
        self.status_ready = BIT(300, modbus)
        self.status_fault = BIT(301, modbus)
        self.cur_progress = REGISTER(300, modbus)
        self.fault_code   = REGISTER(301, modbus)

    def IsReady(self):
        """ Return True if module is in a ready state """
        return self.status_ready.read()

    def IsFault(self):
        """ Return True if module is in a fault state """
        value = self.fault_code.read()
        if value > 0: 
            return True
        else:
            return False

    def StartTask1(self):
        self.Task1.set()
        sleep(.25)
        return 1

    def StartTask2(self):
        self.Task2.set()
        sleep(.25)
        return 1
    def StartTask3(self):
        self.Task3.set()
        sleep(.25)
        return 1
    def StartTask4(self):
        self.Task4.set()
        sleep(.25)
        return 1
    def StartTask5(self):
        self.Task5.set()
        sleep(.25)
        return 1
    def StartTask6(self):
        self.Task6.set()
        sleep(.25)
        return 1
    def StartTask7(self):
        self.Task7.set()
        sleep(.25)
        return 1
    def StartTask8(self):
        self.Task8.set()
        sleep(.25)
        return 1
    def StartTask9(self):
        self.Task9.set()
        sleep(.25)
        return 1
    def StartTask10(self):
        self.Task10.set()
        sleep(.25)
        return 1
    
    def VGR_Status(self):
        """ Show bit & register statuses """
        print("************************")
        print("*      VGR STATUS      *")
        print("************************")
        print("Reset: "+str(self.Reset.read()))
        print("Task1: "+str(self.Task1.read()))
        print("Task2: "+str(self.Task2.read()))
        print("Task3: "+str(self.Task3.read()))
        print("Task4: "+str(self.Task4.read()))
        print("man_control: "+str(self.man_control.read()))
        print("mc301: "+str(self.mc301.read()))
        print("mc302: "+str(self.mc302.read()))
        print("mc303: "+str(self.mc303.read()))
        print("mc304: "+str(self.mc304.read()))
        print("mc305: "+str(self.mc305.read()))
        print("mc306: "+str(self.mc306.read()))
        print("mc307: "+str(self.mc307.read()))
        print("mc350: "+str(self.mc350.read()))
        print("status_ready: "+str(self.status_ready.read()))
        print("vgr_b5: "+str(self.vgr_b5.read()))
        print("fault_code: "+str(self.fault_code.read()))
        print("************************")
