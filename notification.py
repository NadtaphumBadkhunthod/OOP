from __future__ import annotations
from fastapi import FastAPI, Query, HTTPException, status
from fastapi.responses import RedirectResponse
from datetime import datetime, date, timedelta
from enum import Enum
from abc import ABC, abstractmethod
import uvicorn
import uuid

# Enum Class
class CustomerStatus(str, Enum):
    Expired = "Expired"
    Good = "Good"

class ItemType(str, Enum):
    Book = "Book"
    Area = "Area"

class BookingBookQuota(int, Enum):
    Silver = 6
    Gold = 8
    Platinum = 10

class LevelMember(str, Enum):
    Silver = "Silver"
    Gold = "Gold"
    Platinum = "Platinum"

class BirthMonth(str, Enum):
    Jan = "01"
    Feb = "02"
    Mar = "03"
    Apr = "04"
    May = "05"
    Jun = "06"
    Jul = "07"
    Aug = "08"
    Sep = "09"
    Oct = "10"
    Nov = "11"
    Dec = "12"

class PaymentOptions(str,Enum):
    cash = "cash"
    qrcode = "qrcode"

class ActivityType(str, Enum):
    Rent = "Rent"
    Purchase = "Purchase"
    All = "All"

class TypeBook(str,Enum):
    Manga = "Manga"
    Novel = "Novel"
    Historical = "Historical"
    Education = "Education"
    Self_improvement = "Self Improvement"
    Economic = "Economic"

class ItemStatus(str,Enum):
    Available = "Available"
    NotAvailable = "NotAvailable"
    InProcess = "InProcess"
    Purchased = "Purchased"
    Incoming = "Incoming"
    InUse = "InUse"

class PaymentStatus(str,Enum):
    Unpaid = "Unpaid"
    Paid = "Paid"
    Voied = "Voied"

class TransactionStatus(str,Enum):
    Requested = "Requested"
    Confirm = "Confirm"
    Completed = "Completed"
    Cancelled = "Cancelled"

class AreaType(str,Enum):
    quiet_area = "Quiet_Area"
    private_room = "Private_Room" 
    meeting_room = "Meeting_Room"

class NotificationType(str,Enum):
    AREA_EXPIRING_SOON = "Area_Expiring_Soon"  
    AREA_EXPIRED = "Area_Expired"               
    RENT_DUE_TODAY = "Rent_Due_Today"          
    RENT_OVERDUE = "Rent_Overdue"              
    BOOKING_AVAILABLE = "Booking_Available"   
    PURCHASE_SUCCESS = "Purchase_Success"

# Core Class

class Book:
    def __init__(self,book_info,status):
        """
        class Book คือหนังสือที่แยกตาม UID คือหนังสือแต่ละเล่มแยกกันไป เช่น โดเรม่อน เล่มที่ x อันที่ x 
        
        :param book_info: object ที่มีข้อมูลของหนังสือ
        :type book_info: BookInfo
        :param status: สถานะของหนังสือเล่มนั้น
        :type status: ItemStatus
        """
        self.__book_info = book_info
        self.__book_uid = None
        self.__book_status = status
        self.__start_date = None 
        self.__end_date = None
        self.__actual_return_date = None
    
    @property
    def start_date(self):
        return self.__start_date

    @property
    def end_date(self):
        return self.__end_date    
       
WayLaOpen = [
    ["09:00", "10:00"],
    ["10:00", "11:00"],
    ["11:00", "12:00"],
    ["12:00", "13:00"],
    ["13:00", "14:00"],
    ["14:00", "15:00"],
    ["15:00", "16:00"]
]

class TimeSlot:
    def __init__(self, slot_id, start_time, end_time, area : Area):
        self.__slot_id : str = slot_id  
        self.__start_time : str = start_time
        self.__end_time : str = end_time
        self.__is_available : ItemStatus = ItemStatus.Available
        self.__area = area

    
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

    @property
    def area(self):
        return self.__area
    
    @property
    def list_time_slots(self):
        return self.__list_time_slots
    
    def add_time_slots(self,timeslot : TimeSlot):
        if isinstance(timeslot,TimeSlot):
            self.__list_time_slots.append(timeslot)


class Purchase:
    def __init__(self,order : list[Book | TimeSlot]):
        self._order : list[Book | TimeSlot] = order

    @property
    def get_order(self) -> list[Book | TimeSlot]:
        return self._order

    def calculate_subtotal(self):
        return sum((item.book_info.price if isinstance(item, Book) else item.price) for item in self._order)   
    
    def confirm(self):
        for item in self._order:
            item.change_status(ItemStatus.Purchased)

class RentBook(Purchase):
    def __init__(self,order : list[Book | TimeSlot]):
        super().__init__(order)
        self.__late_penalty_rate = 10

    def get_penalty(self):
        penalty = 0

        for item in self._order:
            penalty += (item.actual_return_date - item.end_date).days * self.__late_penalty_rate
        return penalty
    
    def confirm(self):
        for item in self._order:
            item.change_status(ItemStatus.NotAvailable)
    
class BookingArea(Purchase):
    def __init__(self, order : list[Book | TimeSlot]):
        super().__init__(order)
        self.__area : Area = order[0].area if order else None
    
    @property
    def area(self):
        return self.__area
    
    def add_timeslot(self, list_timeslot : list[TimeSlot]):
        if isinstance(list_timeslot,list[TimeSlot]):
            self._order.extend(list_timeslot)
        
    def calculate_subtotal(self):
        return len(self.get_order) * self.__area.hourly_rate

    def calculate_upgrade_delta(self, new_hourly_rate):
        old_price = self.calculate_subtotal()
        new_price = len(self.__order) * new_hourly_rate
        delta = new_price - old_price
        return delta

    def update_order(self, new_slots, new_area):
        self.__order = new_slots
        self.__area = new_area

    def confirm(self):
        for item in self._order:
            item.change_status(ItemStatus.NotAvailable)

class Transaction:
    def __init__(self,customer:Customer,staff:Staff,payment_method : PaymentOptions,start_date_time : datetime = datetime.now(), end_date_time : datetime = datetime.now()):
        self.__customer = customer
        self.__staff = staff
        self.__start_date_time = start_date_time
        self.__end_date_time = end_date_time
        self.__status = TransactionStatus.Requested.value
        self.__payment = Payment(customer,payment_method)
        self.__audit_logs_list = []

    @property
    def customer(self):
        return self.__customer
    
    @property
    def staff(self):
        return self.__staff
    
    @property
    def start_date_time(self):
        return self.__start_date_time
    
    @property
    def end_date_time(self):
        return self.__end_date_time
    
    @property
    def status(self):
        return self.__status
    
    @property
    def payment(self):
        return self.__payment
    
    @property
    def audit_logs(self):
        return self.__audit_logs_list
    
    @property
    def order(self):
        return self.__payment.order
    

    def notify_user(self,customer,message):
        pass

    
bibliohub = System()


app = FastAPI()

@app.get("/")
def redirect_to_docs():
    return RedirectResponse(url="/docs")

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, log_level="info",reload=True)