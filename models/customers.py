from __future__ import annotations
from models.transactions import Transaction, Notification
from models.books import Book, BookInfo, BookOrder
from models.areas import TimeSlot
from models.infos import ActivityType, LevelMember, BookingBookQuota, CustomerStatus, BirthMonth
from models.orders import UpgradeArea
class Customer:
    def __init__(self,name:str,surname:str,phonenumber:str,email:str):
        """
        class Customer คือ object ของลูกค้า
        
        :param name: ชื่อผู้ใช้
        :param surname: นามสกุล
        :param phonenumber: เบอร์โทรศัพท์ผู้ใช้
        :param email: อีเมลผู้ใช้
        """
        
        self.__name = name
        self.__surname = surname
        self.__phonenumber = phonenumber
        self.__email = email
        self.__transaction : list[Transaction] = []
        self.__notification_list : list[Notification] = []
        self.__booking_reservation_time = 0
        self.__rental_quota = 4
        self.__book_rented = 0
        self.__strike = 0
        self.__selected_list : list[Book | TimeSlot] = []

    @property
    def get_all_transaction(self) -> list[Transaction]:
        return self.__transaction 
    
    @get_all_transaction.setter
    def all_transaction(self,list_transaction : list[Transaction]):
        self.__transaction = list_transaction

    @property
    def get_selected_list(self):
        return self.__selected_list
    
    @get_selected_list.setter
    def selected_list(self,new_selected_list):
        self.__selected_list = new_selected_list

    @property
    def get_all_notification(self):
        return self.__notification_list
    
    @get_all_notification.setter
    def all_notification(self,list_notification):
        self.__notification_list = list_notification
    
    @property
    def name(self):
        return self.__name
    
    @property
    def surname(self):
        return self.__surname
    
    @property
    def phonenumber(self):
        return self.__phonenumber
    
    @property
    def email(self):
        return self.__email
    
    @property
    def rental_quota(self):
        return self.__rental_quota
    
    @property
    def book_rented(self):
        return self.__book_rented
    
    @book_rented.setter
    def book_rented(self,nums_rent):
        if self.__book_rented < nums_rent:
            self.__book_rented = 0
        else :
            self.__book_rented -= nums_rent 

    def check_eligibility(self):
        return self.__strike < 3
    
    def check_rent_quota(self,request_book_nums): 
        return len([selected for selected in self.__selected_list if isinstance(selected,BookOrder) and selected.book_info.activity_type == ActivityType.Rent]) + request_book_nums + self.__book_rented <= self.__rental_quota

    def select(self, order: BookInfo | TimeSlot | UpgradeArea, num_days: int = 0):
        # เพิ่ม UpgradeArea เข้าไปใน isinstance เพื่อให้ตะกร้ารับใบอัปเกรดได้
        if isinstance(order,(BookInfo,TimeSlot, UpgradeArea)):
            if isinstance(order,BookInfo):
                order = BookOrder(order,num_days)
            self.__selected_list.append(order)

            return order
        return "Not Found"
    
    def unselect(self,order : BookInfo | TimeSlot):
        if order in self.__selected_list:
            self.__selected_list.remove(order)
        else:
            return "Not Found"
        
        return "Remove Successful"

    def update_cart(self, new_items_list):
        """
        เมธอดสำหรับอัปเดตรายการในตะกร้า 
        เช่น ใช้ลบของที่จ่ายเงินเสร็จแล้วออกไป
        """
        if isinstance(new_items_list, list):
            self.__selected_list = new_items_list
            return True
        return False

    def add_notify(self,notification):
        if isinstance(notification,Notification):
            self.__notification_list.append(notification)

    def add_transaction(self,transaction):
        if isinstance(transaction,Transaction):
            self.__transaction.append(transaction)
            self.__selected_list = []

    @property
    def booking_reservation_time(self):
        """คืนค่าจำนวนชั่วโมงที่จองไปแล้ว"""
        return self.__booking_reservation_time
    
    @booking_reservation_time.setter
    def booking_reservation_time(self, amount: int):
        self.__booking_reservation_time = amount

    def get_area_quota(self):
        return 2  

    def check_area_quota(self, requesting_slots_count):
        current_in_cart = len([item for item in self.__selected_list if isinstance(item, dict) and item.get("type") == "temp_area"])

        total_usage = self.booking_reservation_time + current_in_cart + requesting_slots_count
        
        return total_usage <= self.get_area_quota()

class Member(Customer):
    def __init__(self,customer : Customer, birth_month : BirthMonth):
        super().__init__(customer.name, customer.surname, customer.phonenumber, customer.email)

        self.__level_member = LevelMember.Silver
        self.__birth_month = birth_month
        self.__points = 0

        self.all_transaction = customer.get_all_transaction
        self.selected_list = customer.get_selected_list
        self.all_notification = customer.get_all_notification

        self.__booking_book_quota = BookingBookQuota.Silver
        self.__status = CustomerStatus.Good
        self.__book_booked = 0

    @property
    def level_member(self):
        return self.__level_member

    @property
    def birth_month(self):
        return self.__birth_month
    
    def add_point(self):
        self.__points += 1

        if self.__points >= 30:
            self.__level_member = LevelMember.Gold
        elif self.__points >= 100:
            self.__level_member = LevelMember.Platinum

    @property
    def book_booked(self):
        return self.__book_booked
    
    @book_booked.setter
    def book_booked(self, amount):
        self.__book_booked = amount

    def check_booking_quota(self, request_book_nums):
        current_in_cart = len([item for item in self.get_selected_list 
                             if hasattr(item, 'book_info') and item.book_info.activity_type == ActivityType.Booking])
        

        return (self.book_booked + current_in_cart + request_book_nums) <= self.__booking_book_quota.value
class Staff(Member):
    count = 0
    def __init__(self, customer : Customer, birth_month):
        super().__init__(customer, birth_month)
        self.__no_staff = f"STF-{Staff.count}"

    def info(self):
        return {
            "Name" : self.name,
            "Surname" : self.surname,
            "Staff No." : self.__no_staff
        }

    @property
    def no_staff(self):
        return self.__no_staff
    
    def process_return(self,book,customer):
        if not isinstance(book,Book):
            raise ValueError("Not a book")
        
        if not isinstance(customer,Customer):
            raise ValueError("Not a customer")
        
        # Need implement

class Manager(Staff):
    def __init__(self, customer : Customer, birth_month):
        super().__init__(customer, birth_month)
    
    def print_report(self):
        pass
