from fastapi import FastAPI, Query
from fastapi.responses import RedirectResponse
from datetime import datetime
import uvicorn
from abc import ABC, abstractmethod
import uuid
app = FastAPI()

class System :
    def __init__(self):
        self.__staff_list : list[Staff] = []
        self.__promotion_list = []
        self.__book_stock = []
        self.__area = []
        self.__customer_list = []
        self.__transaction_list = []
        self.__notification_list = []

    def register(self,name,surname,phonenumber,email,birth_month):
        """
        Registering create member object by using Customer data.
        :param name: name of customer
        :param surname: surname of customer
        :param phonenumber: phonenumber of customer
        :param email: email of customer
        """

        if (not self.validate_input_data(name, surname, phonenumber, email)): 
            raise ValueError()

        if self.check_duplicate_account(phonenumber): 
            raise IndexError("มีบัญชีที่ใช้เบอร์โทรศัพท์นี้แล้ว")
        
        member = Member(name, surname, phonenumber, email, birth_month)
        self.__customer_list.append(member)

        return member
    
    def delete_member(self,member):
        self.__customer_list.remove(member)

    def check_duplicate_account(self,phonenumber):
        """
        Docstring for check_duplicate_account
        
        :param phonenumber: เบอร์โทรศัพทธ์ผู้ใช้สำหรับค้นหาผู้ใช้ว่ามีหรือไม่
        """
        return self.get_user_from_phone_number(phonenumber) in self.__customer_list

    def validate_input_data(self,name,surname,phonenumber,email):
        """
        Validates input data before registering.
        Data that need to validate
        name, surname, phonenumber, email
        Raises ValueError if validation fails.
        """

        if not isinstance(name, str) or not isinstance(surname, str):
            raise ValueError("Name and Surname must be strings.")
        
        if len(name.strip()) < 2:
            raise ValueError("Name is too short.")
        if len(surname.strip()) < 2:
            raise ValueError("Surname is too short.")
        
        for char in name:
            if char.isdigit():
                raise ValueError(f"Name cannot contain numbers: {name}")
        for char in surname:
            if char.isdigit():
                raise ValueError(f"Surname cannot contain numbers: {surname}")
            
        if " " in name:
            raise ValueError(f"Name cannot contain space: {name}")
        if " " in surname:
            raise ValueError(f"Surname cannot contain space: {surname}")
        
        if not isinstance(email,str):
            raise ValueError("Email must be strings.")
        
        if email.count("@") != 1:
            raise ValueError("Email must contain exactly one '@' symbol.")
    
        if " " in email:
            raise ValueError("Email cannot contain spaces.")
        
        local_part, domain_part = email.split("@")

        if len(local_part) == 0:
            raise ValueError("Email is missing the username part (before @).")
        
        if len(domain_part) == 0 or "." not in domain_part:
            raise ValueError("Email domain part is invalid.")

        if domain_part.startswith(".") or domain_part.endswith("."):
            raise ValueError("Email domain cannot start or end with a dot.")
        
        phone_str = str(phonenumber).strip()

        if phone_str.startswith("+"):
            digits_only = phone_str[1:]
        else:
            digits_only = phone_str

        clean_digits = digits_only.replace("-", "").replace(" ", "")

        if not clean_digits.isdigit():
            raise ValueError("Phone number contains invalid characters.")

        if len(clean_digits) != 10:
            raise ValueError("Phone number length is invalid (should be 10 digits).")
        

        return True

    def get_user_from_phone_number(self,phonenumber):
        for member in self.__customer_list:
            if member.phonenumber == phonenumber:
                return member
            
    def search_book(self,customer,bookname,activity_type):
            if not customer.check_eligibility():
                raise PermissionError("Not come in to my place go away don't comeback")
            
            for bookstock in self.__book_stock:
                if bookstock.name == bookname:
                    return bookstock.search_book_avaliable(activity_type)
                
    def search_area(self,customer,area_id):
        if not customer.check_eligibility():
                raise PermissionError("Not come in to my place go away don't comeback")
        
        for area in self.__area:
            if area.area_id == area_id:
                available_slots = area.list_timeslot()
                
                # โชว์ ID พ่วงไปด้วยเลย (เช่น "TS01: 09:00-10:00")
                return [f"{slot.slot_id}: {slot.start_time}-{slot.end_time}" for slot in available_slots]
                
        raise ValueError("ไม่พบพื้นที่ที่ค้นหา")
            
    def checkout(self,customer,staff,selected_list,payment_method):
        list_order = []
        
        for item in selected_list:
            if isinstance(item,Book):
                match item.get_activity_type():
                    case "Rent":
                        list_order.append(RentBook(*item.data))
                    case "Purchase":
                        list_order.append(Purchase())
                    case _: raise ValueError("Error : Activity type not found")
            elif isinstance(item, BookingArea):
                list_order.append(item)

        if not list_order:
            return "ไม่มีสินค้าหรือพื้นที่ในตะกร้า"
        
        payment = Payment(customer,list_order,payment_method)
        net_amount = payment.calculate_net_amount()#need implement : calculate payment ใน payment ไปเลย

        if payment_method == "QRCode":
            pay_method_obj = QRCode(gateway_reference=f"REF-{customer.phonenumber}")
        elif payment_method == "Cash":
            pay_method_obj = Cash()
        else:
            raise ValueError("วิธีชำระเงินไม่ถูกต้อง")
        
        print("\n--- กำลังประมวลผลการชำระเงิน ---")
        is_paid = pay_method_obj.process_payment(net_amount)
        if is_paid:
            payment.update_payment_status("Paid")

        
        transaction = Transaction(customer,staff,datetime.now(),payment)

        transaction.add_audit_log(f"request : {datetime.now()}") #need implement : เพิ่มรูปแบบของ audit log
        print(f"Net Amount: {net_amount}")
        transaction.update_status("Confirm")

        # ส่วนท้ายการทำงาน need implement : ถ้ารายการไหนต้อง update status ของสินค้ามาทำในส่วนนี้
        for item in list_order:
            if isinstance(item,Book):
                match item.get_activity_type():
                    case "Rent":
                        item.change_status("Not Available")
                        print("change status successful") 
            elif isinstance(item, BookingArea):
                for slot in item._BookingArea__reserved_slots:
                    slot.update_slot("Not Available")
                print("Change Area status successful")
                
        total_slots = sum(len(item._BookingArea__reserved_slots) for item in list_order if isinstance(item, BookingArea))
        customer.add_booking_time(total_slots)

        customer.add_transaction(transaction)

        self.notify_user(customer,f"{customer.name}: transaction ... confirm") #need implement : ต้องเปลี่ยนคำ

        if isinstance(customer,Member):
            customer.add_point()
            self.notify_user(customer,f"{customer.name}: add point successful")

        return f"ทำรายการสำเร็จ ชำระเงินรวมทั้งสิ้น {net_amount} บาท"
    
    def verify_permission(self,manager):
        return isinstance(manager,Manager)
    
    def add_book_stock(self,book_stock):
        if isinstance(book_stock,BookStock):
            self.__book_stock.append(book_stock)

    def remove_book_stock(self,book_stock):
        if isinstance(book_stock,BookStock):
            self.__book_stock.remove(book_stock)

    def add_staff(self,staff):
        if isinstance(staff,Staff):
            self.__staff_list.append(staff)

    def remove_staff(self,staff):
        if isinstance(staff,Staff):
            self.__staff_list.remove(staff)

    def add_promotion(self,promotion):
        if isinstance(promotion,Promotion):
            self.__promotion_list.append(promotion)

    def remove_promotion(self,promotion):
        if isinstance(promotion,Promotion):
            self.__promotion_list.remove(promotion)
    
    def add_area(self,area):
        if isinstance(area,Area):
            self.__area.append(area)

    def remove_area(self,area):
        if isinstance(area,Area):
            self.__area.remove(area) 
    
    def add_strike(self,customer):
        if isinstance(customer,Customer):
            customer.add_stike()

    def reduce_strike(self,customer):
        if isinstance(customer,Customer):
            customer.reduce_strike()

    def notify_user(self,customer,message):
        if isinstance(customer,Customer):
            if isinstance(message,str):
                self.__notification_list.append(Notification(customer,message))

    def upgrade_booking_area(self):
        pass

    def generate_utilization_report(self):
        pass  

    @property
    def list_area(self):
        return self.__area      

class Notification:
    count = 0
    def __init__(self,customer,message):
        self.__customer = customer
        self.__message = message
        self.__uid = f"NT-{customer.name}-{Notification.count}"

class Area:
    def __init__(self, id, type, hourly_rate, feature, capacity):
        self.__area_id = id
        self.__area_type = type #บอกว่าเป็นareaแบบไหนเช่น qiuet area,Private Room,Meeting Room
        self.__hourly_rate = hourly_rate
        self.__feature = feature
        self.__capacity = capacity
        self.__slots= [] 
    def __repr__(self):
        return f"AreaName: {self.__area_id}, Type: {self.__area_type}"
    def add_slot(self, slot):
        self.__slots.append(slot)

    def list_timeslot(self):
        return [slot for slot in self.__slots if slot.is_available == "Available"]

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
    def __init__(self, slot_id, start_time, end_time):
        self.__slot_id = slot_id  
        self.__start_time = start_time
        self.__end_time = end_time
        self.__is_available = "Available"

    def __repr__(self):
        return f"Slot[{self.__slot_id}]: {self.__start_time}-{self.__end_time} | {self.__is_available}"

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

    def update_slot(self, status_change):
        self.__is_available = status_change

class Promotion:
    def __init__(self,promo_code,discount_rate):
        self.__promo_code = promo_code
        self.__discount_rate = discount_rate
        self.__status = False
        self.__used_user = []
        
    def is_eligible(self,customer):
        if isinstance(customer,Customer):
            return customer not in self.__used_user
        
    def apply_discount(self,price,customer):
        if isinstance(customer,Customer):
            if self.is_eligible(customer):
                self.__used_user.append(customer)
                return price - (price * self.__discount_rate)
            
    def payment_unsuccess(self,customer):
        if isinstance(customer,Customer):
            self.__used_user.remove(customer)

class BirthDate:
    def __init__(self):
        pass

class Transaction:
    def __init__(self, user, staff, start_date_time, payment, end_date_time=None):
        self.__user = user              # Customer object (ผู้ทำรายการ)
        self.__staff = staff            # Staff object
        self.__start_date_time = start_date_time
        self.__end_date_time = end_date_time  # อาจจะใส่ทีหลังตอนจองเสร็จ
        self.__status = "Requested"     # "Requested, Confirmed, In Use, Completed, Cancelled"
        self.__payment = payment        # Payment object ที่รับเข้ามาทั้งก้อน
        self.__audit_logs_list = []     # บันทึกการแก้ไขข้อมูล

    def update_status(self, status: str):
        """อัปเดตสถานะของ Transaction"""
        self.__status = status
        # แถม: ให้มันเขียน Log อัตโนมัติทุกครั้งที่สถานะเปลี่ยน
        self.add_audit_log(f"[{datetime.now()}] Status updated to: {status}")

    def add_audit_log(self, log_message: str):
        """Log of Transaction"""
        self.__audit_logs_list.append(log_message)

    def sync_payment_with_activity(self):
        pass

class PaymentMethod(ABC):
    @abstractmethod
    def process_payment(self, amount: float):
        pass

class QRCode(PaymentMethod):
    def __init__(self, gateway_reference: str):
        self.__gateway_reference = gateway_reference

    def process_payment(self, amount: float):
       
        print(f"กำลังทำรายการจ่ายเงินผ่าน QR Code (Ref: {self.__gateway_reference}) ยอด: {amount} บาท")
        return True
class Cash(PaymentMethod):
    def process_payment(self, amount: float):
        print(f"กำลังทำรายการจ่ายเงินสดหน้าเคาน์เตอร์ ยอด: {amount} บาท")
        return True
    
class Payment:
    def __init__(self, customer, order_list, payment_method_str: str):
        self.__customer = customer
        # จำลองการสร้างเลขสลิป (เลขที่อ้างอิง) อัตโนมัติ
        self.__payment_no = f"PAY-{uuid.uuid4().hex[:8].upper()}" 
        self.__status = "Unpaid" # "Unpaid", "Paid", "Voided"
        self.__order = order_list # เก็บก้อน BookingArea, RentBook ฯลฯ
        self.__timestamp = datetime.now()
        self.__payment_method = payment_method_str # เป็น String ตาม Diagram

        self.__base_fee = 0.0
        self.__upgrade_delta = 0.0
        self.__discount_amount = 0.0
        self.__penalty_fee = 0.0
        self.__net_amount = 0.0

    def calculate_net_amount(self):
        total_base = 0.0
        
        for item in self.__order:
            if hasattr(item, 'calculate_subtotal'):
                total_base += item.calculate_subtotal()
                
        self.__base_fee = total_base

        self.__net_amount = (self.__base_fee + self.__upgrade_delta + self.__penalty_fee) - self.__discount_amount
        
        return self.__net_amount

    def update_payment_status(self, status: str):
        """อัปเดตสถานะ เช่น ตอนจ่ายเงินสำเร็จก็เปลี่ยนเป็น Paid"""
        self.__status = status

    def add_penalty_fee(self, amount: float):
        """บวกค่าปรับเพิ่มเข้าไป (เช่น คืนหนังสือเลท)"""
        self.__penalty_fee += amount
        # พอมีค่าปรับเพิ่ม ก็ควรคำนวณยอดสุทธิใหม่ด้วย
        self.calculate_net_amount()

    @property
    def net_amount(self):
        return self.__net_amount
        
    @property
    def payment_method(self):
        return self.__payment_method
    

class Purchase:
    def __init__(self, purchase_items=None):
        self.__purchase_items = purchase_items if purchase_items else []

    def calculate_subtotal(self):
        total = 0.0
        for item in self.__purchase_items:
            total += item.get_rate_info() 
        return total               

class RentBook(Purchase):
    def __init__(self):
        pass

class BookingArea(Purchase):
    def __init__(self, reserved_slots, area):
        super().__init__()
        self.__reserved_slots = reserved_slots
        self.__area = area

    def calculate_total_price(self):
        return len(self.__reserved_slots) * self.__area.hourly_rate

    def calculate_subtotal(self):
        return self.calculate_total_price()

    def request_upgrade(self, system, new_area_id):
        """
        +request_upgrade() "request กลับระบบไป search area"
        รับ object ของ System เข้ามาเพื่อค้นหา Area ใหม่
        """
        available_slots = system.search_area(new_area_id)
        return available_slots

    def calculate_upgrade_delta(self, new_hourly_rate):
        old_price = self.calculate_total_price()
        new_price = len(self.__reserved_slots) * new_hourly_rate
        delta = new_price - old_price
        return delta

    def update_reserved_slots(self, new_slots, new_area):
        self.__reserved_slots = new_slots
        self.__area = new_area
        
    @property
    def reserved_slots(self):
        return self.__reserved_slots
            
class Customer:
    def __init__(self,name:str,surname:str,phonenumber:int,email:str):
        """
        Docstring for __init__
        
        :param name: ชื่อผู้ใช้
        :param surname: นามสกุล
        :param phonenumber: เบอร์โทรศัพท์ผู้ใช้
        :param email: อีเมลผู้ใช้
        """
        
        self.__name = name
        self.__surname = surname
        self.__phonenumber = phonenumber
        self.__email = email
        self.__transaction = []
        self.__notification_list = []
        self.__booking_reservation_time = 0
        self.__rental_quota = 0
        self.__strike = 0
        self.__selected_list = []

    @property
    def name(self):
        return self.__name
    
    @property
    def phonenumber(self):
        return self.__phonenumber
    
    @property
    def selected_list(self):
        return self.__selected_list
    def update_cart(self, new_items_list):
        """
        เมธอดสำหรับอัปเดตรายการในตะกร้า 
        เช่น ใช้ลบของที่จ่ายเงินเสร็จแล้วออกไป
        """
        if isinstance(new_items_list, list):
            self.__selected_list = new_items_list
            return True
        return False
    def check_eligibility(self):
        return self.__strike < 3
    
    def check_quota(self): 
        return len([selected for selected in self.__selected_list if isinstance(selected,Book) and selected.activity_type == "Rent"]) < 4

    def select(self,order):
        self.__selected_list.append(order)

    def unselect(self,order):
        self.__selected_list.remove(order)

    def add_notify(self,notification):
        if isinstance(notification,Notification):
            self.__notification_list.append(notification)

    def add_transaction(self,transaction):
        if isinstance(transaction,Transaction):
            self.__transaction.append(transaction)

    @property
    def booking_reservation_time(self):
        """คืนค่าจำนวนชั่วโมงที่จองไปแล้ว"""
        return self.__booking_reservation_time

    def get_area_quota(self):
        return 2  

    def check_area_quota(self, requesting_slots_count):
        current_in_cart = len([item for item in self.__selected_list if isinstance(item, dict) and item.get("type") == "temp_area"])

        total_usage = self.booking_reservation_time + current_in_cart + requesting_slots_count
        
        return total_usage <= self.get_area_quota()

    def add_booking_time(self, amount: int):
        self.__booking_reservation_time += amount

class Member(Customer):
    def __init__(self, name, surname, phonenumber, email, birth_month):
        super().__init__(name, surname, phonenumber, email)

        self.__level_member = "Silver"
        self.__birth_month = birth_month
        self.__points = 0
        self.__booking_book_quota = 0

    def get_area_quota(self):
        if self.__level_member == "Silver":
            return 3
        elif self.__level_member == "Gold":
            return 4
        elif self.__level_member == "Pathinum":
            return 5
        return 2
    
    def add_point(self):
        self.__points += 10  # สมมติเสยๆน่ะ

class Staff:
    def __init__(self):
        pass

class Manager:
    def __init__(self):
        pass

class BookStock:
    def __init__(self,name):
        self.__name = name
        self.__forsale_book_list = []
        self.__rent_book_list = []

    def add_book(self,book):
        if isinstance(book,Book):
            if book.activity_type == "Rent":
                self.__rent_book_list.append(book)
            elif book.activity_type == "Purchase":
                self.__forsale_book_list.append(book)
            else:
                raise TypeError("Activity type error")
        else:
            raise TypeError("Need to be a book")
        
        
    def remove_book(self,book):
        if isinstance(book,Book):
            if book.activity_type == "Rent":
                self.__rent_book_list.remove(book)
            elif book.activity_type == "Purchase":
                self.__forsale_book_list.remove(book)
            else:
                raise TypeError("Activity type error")
        else:
            raise TypeError("Need to be a book")
        
    def search_book_available(self,BookName,activity_type):
        if activity_type == "Rent":
            for book in self.__rent_book_list:
                if book.book_name == BookName:
                    if book.checkavailability():
                        return book
        elif activity_type == "Purchase":
            for book in self.__forsale_book_list:
                if book.book_name == BookName:
                    if book.checkavailability():
                        return book
        else:
            raise TypeError("Activity type error")
    
class Book:
    count = 0

    def __init__(self,name,series,author,category,price,activity_type,available_date=datetime.now()):
        self.__book_name = name
        self.__book_series = series
        self.__book_uid = f"BK-{activity_type}-{series}-{name}-{author}-{Book.count}"
        self.__author = author
        self.__category = category
        self.__price = price
        self.__activity_type = activity_type
        self.__borrowed_count = 0
        if available_date == datetime.now():
            self.__book_status = "Available"
        else:
            self.__book_status = "Incoming"
        self.__available_date = available_date
        Book.count += 1

    def check_available(self):
        return self.__book_status == "Available"
    
    def change_status(self,status):
        self.__book_status = status

    def get_rate_info(self):
        return self.__price
    
    def change_activity_type(self,activity_type):
        self.__activity_type = activity_type

    def get_activity_type(self):
        return self.__activity_type

from pydantic import BaseModel
from typing import List
from enum import Enum

"""
class AreaOption(str, Enum):
    meeting_room = "MeetingRoom-01"
    quiet_area = "Quiet-A"

    """

bibliohub = System()



bibliohub.register("ปลื้ม", "เรียนไหม", "0812345678", "pluem@gmail.com", 5)

dummy_area = Area("MeetingRoom-01", "Meeting Room", 150.0, ["Projector", "Whiteboard"], 4)
dummy_area.add_slot(TimeSlot("MR01", "09:00", "10:00"))
dummy_area.add_slot(TimeSlot("MR02", "10:00", "11:00"))
dummy_area.add_slot(TimeSlot("MR03", "11:00", "12:00"))
dummy_area.add_slot(TimeSlot("MR04", "12:00", "13:00"))
dummy_area.add_slot(TimeSlot("MR05", "13:00", "14:00"))
dummy_area.add_slot(TimeSlot("MR06", "14:00", "15:00"))
dummy_area.add_slot(TimeSlot("MR07", "15:00", "16:00"))
bibliohub.add_area(dummy_area)

quiet_area = Area("Quiet-A", "Quiet Area", 50.0, ["Desk Lamp", "Power Outlet"], 1)
quiet_area.add_slot(TimeSlot("QA01", "09:00", "10:00"))
quiet_area.add_slot(TimeSlot("QA02", "10:00", "11:00"))
quiet_area.add_slot(TimeSlot("QA03", "11:00", "12:00"))
quiet_area.add_slot(TimeSlot("QA04", "12:00", "13:00"))
quiet_area.add_slot(TimeSlot("QA05", "13:00", "14:00"))
quiet_area.add_slot(TimeSlot("QA06", "14:00", "15:00"))
quiet_area.add_slot(TimeSlot("QA07", "15:00", "16:00"))
bibliohub.add_area(quiet_area)

area_names = {area.area_id.replace("-", "_").lower(): area.area_id for area in bibliohub.list_area}

AreaOption = Enum('AreaOption', area_names, type=str)
class PaymentOption(str, Enum):
    qr_code = "QRCode"
    cash = "Cash"


@app.get("/", tags=["Booking Area"])
def read_all_areas():
    all_areas = []
    for area in bibliohub.list_area:
        slots_list = []
        for slot in area.area__slots:
            slots_list.append({
                "slot_id": slot.slot_id,
                "time_range": f"{slot.start_time} - {slot.end_time}",
                "status": slot.is_available
            })
        all_areas.append({
            "area_id": area.area_id,          
            "area_type": area.area_type,       
            "hourly_rate": area.hourly_rate,  
            "features": area.area_feature,   
            "capacity": area.area_capacity,   
            "time_slots": slots_list          
        })
        
    return {
        "message": "Welcome to BiblioHub Booking System",
        "total_areas": len(all_areas),
        "areas_catalog": all_areas
    }

@app.get("/area/search", tags=["Booking Area"])
def search_area(phonenumber: str = Query(description="เบอร์โทรศัพท์ลูกค้า (เช่น 812345678)"), 
                    area_id: AreaOption = Query(..., description="เลือกพื้นที่ที่ต้องการจอง")):
    
    customer = bibliohub.get_user_from_phone_number(phonenumber)
    if not customer:
        return {"error": "ไม่พบผู้ใช้ในระบบ"}
        
    try:
        available_slots = bibliohub.search_area(customer, area_id.value)
        return {"area_id": area_id, "available_slots": available_slots}
    except Exception as e:
        return {"error": str(e)}

@app.post("/area/select", tags=["Booking Area"])
def select_area(
    phonenumber: str = Query(..., description="เบอร์โทรศัพท์ลูกค้า"),
    area_id: AreaOption = Query(..., description="เลือกพื้นที่ที่ต้องการจอง"),
    slot_ids: List[str] = Query(..., description="ID สล็อตที่ต้องการ (กด Add Item เพื่อเพิ่มหลายอัน)")
):
    customer = bibliohub.get_user_from_phone_number(phonenumber)
    if not customer:
        return {"error": "ไม่พบผู้ใช้ในระบบ"}

    target_area = None

    for a in bibliohub.list_area:
        if a.area_id == area_id.value:
            target_area = a
            break   
    if not target_area:
        return {"error": "ไม่พบพื้นที่"}

    selected_slots = []
    
    for req_slot_id in slot_ids: #เช็คว่ามันว่างจริงไหม
        found_slot = None
        for slot in target_area.area__slots:
            if slot.slot_id == req_slot_id:
                found_slot = slot
                break
                
        if not found_slot or found_slot.is_available != "Available":
            return {"error": f"สล็อต {req_slot_id} ถูกจองไปแล้ว หรือไม่มีในระบบ (กรุณาทำรายการใหม่)"}
            
        selected_slots.append(found_slot)

    requesting_count = len(slot_ids)
    if not customer.check_area_quota(requesting_count):
        return {"error": f"โควต้าเต็ม! คุณจองได้อีก {customer.get_area_quota() - customer.booking_reservation_time} ชม."}
    
    for slot in selected_slots:
        temp_booking = {"type": "temp_area", "area": target_area, "slot": slot}
        customer.select(temp_booking)

    slot_names = ", ".join(slot_ids)
    return {"status": "Success", "message": f"นำสล็อต {slot_names} ของ {area_id.value} ใส่ตะกร้าแล้ว"}

@app.post("/area/checkout")
def checkout_area(
    phonenumber: str = Query(..., description="เบอร์โทรศัพท์ลูกค้า"),
    payment_method: PaymentOption = Query(..., description="เลือกช่องทางการชำระเงิน")
):  
    customer = bibliohub.get_user_from_phone_number(phonenumber)
    
    temp_items = []
    other_items = []
    
    for item in customer.selected_list:
        if isinstance(item, dict) and item.get("type") == "temp_area":
            temp_items.append(item)
        else:
            other_items.append(item)

    if not temp_items:
        return {"error": "ไม่มีรายการจองที่นั่ง"}

    all_slots = []
    for item in temp_items:
        all_slots.append(item["slot"])
    
    the_room = temp_items[0]["area"] 
    booking_order = BookingArea(all_slots, the_room)

    try:
        msg = bibliohub.checkout(customer, Staff(), [booking_order], payment_method)
        
        customer.update_cart(other_items)
        
        return {"status": "Success", "message": msg}
        
    except Exception as e:
        return {"error": str(e)}
if __name__ == "__main__":
    uvicorn.run("booking_area:app", host="127.0.0.1", port=8000, log_level="info",reload=True)