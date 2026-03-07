from __future__ import annotations
from models.infos import AreaType, ItemStatus

WayLaOpen = [
    ["09:00", "10:00"],
    ["10:00", "11:00"],
    ["11:00", "12:00"],
    ["12:00", "13:00"],
    ["13:00", "14:00"],
    ["14:00", "15:00"],
    ["15:00", "16:00"]
]

class Area:
    count = 1
    def __init__(self,type : AreaType, hourly_rate, feature, capacity):
        self.__area_id : str = f"AREA-{type.value.upper()}-{self.count}"
        self.count += 1

        self.__area_type : AreaType = type #บอกว่าเป็นareaแบบไหนเช่น qiuet area,Private Room,Meeting Room
        self.__hourly_rate : float = hourly_rate
        self.__feature : list[str] = feature
        self.__capacity : int = capacity
        self.__slots : list[TimeSlot] = [] 
    def __repr__(self):
        return f"AreaName: {self.__area_id}, Type: {self.__area_type.value}"

    @property
    def list_timeslot(self) -> list[TimeSlot]:
        return [slot for slot in self.__slots if slot.is_available == "Available"]

    def create_time_slot(self):
        for time in WayLaOpen:
            start_time,end_time = time
            self.__slots.append(TimeSlot(f"{self.__area_id}-{len(self.__slots) + 1}",start_time,end_time,self))

    @property
    def area_id(self):
        return self.__area_id
    
    @property
    def area_type(self):
        return self.__area_type
    
    @property
    def area_feature(self):
        return self.__feature
    
    @property
    def area_capacity(self):
        return self.__capacity
    
    @property
    def area__slots(self):
        return self.__slots

    @property
    def hourly_rate(self):
        return self.__hourly_rate
    
class TimeSlot:
    def __init__(self, slot_id, start_time, end_time, area : Area):
        self.__slot_id : str = slot_id  
        self.__start_time : str = start_time
        self.__end_time : str = end_time
        self.__is_available : ItemStatus = ItemStatus.Available
        self.__area : Area = area

    def __repr__(self):
        return f"Slot[{self.__slot_id}]: {self.__start_time}-{self.__end_time} | {self.__is_available} | {self.__area.hourly_rate}"
    
    @property
    def slot_id(self):
        return self.__slot_id
        
    @property
    def start_time(self):
        return self.__start_time
        
    @property
    def end_time(self):
        return self.__end_time

    @property
    def is_available(self):
        return self.__is_available
    
    @property
    def area(self):
        return self.__area

    def change_status(self, status_change : ItemStatus):
        self.__is_available = status_change

    @property
    def area(self):
        return self.__area
    
    @property
    def list_time_slots(self):
        return self.__list_time_slots
    
    def add_time_slots(self,timeslot : TimeSlot):
        if isinstance(timeslot,TimeSlot):
            self.__list_time_slots.append(timeslot)
