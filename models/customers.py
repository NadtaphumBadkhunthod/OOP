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

    @property
    def get_selected_list(self):
        return self.__selected_list
    
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
        self.__book_rented = nums_rent

    def check_eligibility(self):
        return self.__strike < 3
    
    def check_rent_quota(self,request_book_nums): 
        return len([selected for selected in self.__selected_list if isinstance(selected,BookOrder) and selected.book_info.activity_type == ActivityType.Rent]) + request_book_nums <= (self.__rental_quota - self.__book_rented)

    def select(self, order: BookInfo | TimeSlot | UpgradeArea, num_days: int = 0):
        # เพิ่ม UpgradeArea เข้าไปใน isinstance เพื่อให้ตะกร้ารับใบอัปเกรดได้
        if isinstance(order, (BookInfo, TimeSlot, UpgradeArea)):
            if isinstance(order, BookInfo):
                order = BookOrder(order, num_days)
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
    def __init__(self, name, surname, phonenumber, email, birth_month : BirthMonth):
        super().__init__(name, surname, phonenumber, email)

        self.__level_member = LevelMember.Silver
        self.__birth_month = birth_month
        self.__points = 0
        self.__booking_book_quota = BookingBookQuota.Silver
        self.__status = CustomerStatus.Good

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

class Staff(Member):
    count = 0
    def __init__(self, name, surname, phonenumber, email, birth_month):
        super().__init__(name, surname, phonenumber, email, birth_month)
        self.__no_staff = f"STF-{Staff.count}"

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
    def __init__(self, name, surname, phonenumber, email, birth_month, no_branch):
        super().__init__(name, surname, phonenumber, email, birth_month, no_branch)
    
    def print_report(self):
        pass
