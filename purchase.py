from fastapi import FastAPI, Query
from fastapi.responses import RedirectResponse
from abc import ABC, abstractmethod
from datetime import datetime, date
from enum import Enum
import uuid
import uvicorn

class ActivityType(str, Enum):
    Rent = "Rent"
    Purchase = "Purchase"

class TypeBook(str, Enum):
    Manga = "Manga"
    Novel = "Novel"
    Historical = "Historical"
    Education = "Education"
    Self_improvement = "Self Improvement"
    Economic = "Economic"

class Status(str, Enum):
    Available = "Available"
    UnAvailable = "UnAvailable"
    Selected = "Selected"
    Purchased = "Purchased"
    Incoming = "Incoming"

class System:
    def __init__(self):
        self.__staff_list = []
        self.__promotion_list = []
        self.__book_stock = []
        self.__area = []
        self.__customer_list = []
        self.__transaction_list = []
        self.__notification_list = []
    
    def register(self, name, surname, phonenumber, email, birth_month = 1):
        if not self.validate_input_data(name, surname, phonenumber, email):
            raise ValueError()
        
        if self.check_duplicate_account(phonenumber):
            raise IndexError("This account already has this phonenumber.")
        
        member = Member(name, surname, phonenumber, email, birth_month)
        self.__customer_list.append(member)
        return member

    def delete_member(self, member):
        self.__customer_list.remove(member)

    def check_duplicate_account(self, phonenumber):
        return self.get_user_from_phone_number(phonenumber)

    def validate_input_data(self, name, surname, phonenumber, email):
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

    def get_user_from_phone_number(self, phonenumber):
        for member in self.__customer_list:
            if member.phonenumber == phonenumber:
                return member

    def search_book(self, customer, book_series, bookname, activity_type):

        customer.check_eligibility()
        
        for stock in self.__book_stock:
            if stock.book_stock_name == book_series:
                found = stock.search_book_available(bookname, activity_type)
                add_result = customer.add_search_result(found)
                return {
                    "Searching Result" : add_result,
                    "All Customer Search Result" : {i: book for i, book in enumerate(customer.get_search_result)}
                }
        return "Not Found"

    def search_area():
        pass

    def checkout(self, customer, staff, selected_list, payment_method):
        list_order = []
        for item in selected_list:
            if isinstance(item, Book):
                match item.get_activity_type:
                    case "Rent":
                        list_order.append(RentBook(*item.data))
                    case "Purchase":
                        list_order.append(Purchase([item]))
                    case _: raise ValueError("Error : Activity type not found")
            elif isinstance(item, BookingArea):
                list_order.append(item)

        if not list_order:
            return "ไม่มีสินค้าหรือพื้นที่ในตะกร้า"
        
        payment = Payment(customer, list_order, payment_method)
        net_amount = payment.calculate_net_amount()

        if payment_method == "QRCode":
            pay_method_obj = QRCode(gateway_reference=f"REF-{customer.phonenumber}")
        elif payment_method == "Cash":
            pay_method_obj = Cash() 
        else:
            raise ValueError("Payment Wrong") 
        
        is_paid = pay_method_obj.process_payment(net_amount)
        if is_paid:
            payment.update_payment_status("Paid")

        transaction = Transaction(customer, staff, datetime.now(), payment)  
        transaction.add_audit_log(f"request : {datetime.now()}") 
        print(f"Net Amount: {net_amount}") 
        transaction.update_status("Confirm")

        # ส่วนท้ายการทำงาน need implement : ถ้ารายการไหนต้อง update status ของสินค้ามาทำในส่วนนี้
        for item in list_order:
            if isinstance(item, Book):
                match item.get_activity_type:
                    case "Rent":
                        item.change_status(Status.UnAvailable)
                        print("Change status successful")
            elif isinstance(item, Purchase):
                for book in item.purchase_items:
                    book.change_status(Status.Purchased)
                print("Change status successful")

        self.__transaction_list.append(transaction)
        customer.add_transaction(transaction) 

        self.notify_user(customer, f"{customer.name}: transaction ... confirm")

        if isinstance(customer, Member):
            customer.add_point() 

        self.notify_user(customer, f"{customer.name}: add point successful")

        return "ทำรายการเสร็จสิ้น"   

    def verify_permission(self, manager):
        return isinstance(manager, Manager)

    def add_book_stock(self, book):
        if isinstance (book, BookStock):
            self.__book_stock.append(book)

    def remove_book_stock(self, book):
        if isinstance(book, BookStock):
            self.__book_stock.remove(book)

    def add_staff(self, staff):
        if isinstance(staff, Staff):
            self.__staff_list.append(staff)

    def remove_staff(self, staff):
        if isinstance(staff, Staff):
            self.__staff_list.remove(staff)

    def add_promotion(self, promotion):
        if isinstance(promotion, Promotion):
            self.__promotion_list.append(promotion)

    def remove_promotion(self, promotion):
        if isinstance(promotion, Promotion):
            self.__promotion_list.remove(promotion)

    def add_area(self, area):
        if isinstance(area, Area):
            self.__area.append(area)

    def remove_area(self, area):
        if isinstance(area, Area):
            self.__area.remove(area)

    def add_strike(self, customer):
        if isinstance(customer, Customer):
            customer.add_strike()

    def reduce_strike(self, customer):
        if isinstance(customer, Customer):
            customer.reduce_strike()

    def notify_user(self, customer, message):
        if isinstance(customer, Customer):
            if isinstance(message, str):
                self.__notification_list.append(Notification(customer, message))

    def upgrade_booking_area():
        pass            

    def generate_utilization_report():
        pass    
    
class Customer(ABC):
    def __init__(self, name, surname, phonenumber, email):
        self.__name = name
        self.__surname = surname
        self.__phonenumber = phonenumber
        self.__email = email
        self.__retal_quota = 0
        self.__strike = 0
        self.__transaction = []
        self.__notification_list = []
        self.__booking_reservation_time = None
        self.__selected_list = []
        self.__search_result = []

    @property
    def name(self):
        return self.__name

    @property
    def get_search_result(self):
        return self.__search_result
    
    @property
    def phonenumber(self):
        return self.__phonenumber
    
    def check_eligibility(self):
        if self.__strike >= 3:
            raise ValueError("You can't buy or rent na ja")
        
    def add_search_result(self, newsearch_result):
        for result in self.__search_result:
            if result == newsearch_result:
                return "Already search"
        self.__search_result.append(newsearch_result)
        return newsearch_result

    def check_quota(self):
        pass

    def select(self, order):
        if isinstance(order, (Book, Area)):
            self.__selected_list.append(order)
            if isinstance(order, Book):
                order.change_status(Status.Selected)
                self.__search_result.remove(order)        
    
    def unselect(self, order):
        self.__selected_list.remove(order)
        if isinstance(order, Book):
            order.change_status(Status.Available)

    def add_notify(self, notification):
        if isinstance(notification, Notification):
            self.__notification_list.append(notification)

    def add_transaction(self, transaction):
        if isinstance(transaction, Transaction):
            self.__transaction.append(transaction)   

    # def add_strike(self):
    #     pass

    # def reduce_strike(self):
    #     pass

class Member(Customer):
    def __init__(self, name, surname, phonenumber, email, birth_month):
        super().__init__(name, surname, phonenumber, email)
        self.__level_member = "Silver"
        self.__birth_month = birth_month
        self.__points = 0
        self.__booking_book_quota = 6 # silver 6 gold 8 platinum 10
        try:
            self.__expiration_date = date.today().replace(year = date.today().year + 1)
        except:
            self.__expiration_date = date.today().replace(year = date.today().year + 1, month = 3, day = 1)

    def add_point(self, point =  1000000):
        self.__points += point

class Staff(Member):
    def __init__(self, name, surname, phonenumber, email, birth_month):
        super().__init__(name, surname, phonenumber, email, birth_month)

class Manager(Staff):
    def __init__(self, name, surname, phonenumber, email, birth_month):
        super().__init__(name, surname, phonenumber, email, birth_month)

class Book:
    count = 0

    def __init__(self, book_name, book_series, book_uid, author, category, price, activity_type, total_borrowed_count, book_status, available_date):
        self.__book_name = book_name
        self.__book_series = book_series
        self.__book_uid = f"BK-{activity_type}-{book_series}-{book_name.replace(" ","_")}-{author}-{Book.count}"
        self.__author = author
        self.__category = category
        self.__price = price
        self.__activity_type = activity_type #เช่า / ขาย
        self.__total_borrowed_count =  0
        self.__book_status = book_status #Selected, Available, Incoming, Not Available
        if available_date <= date.today():
            self.__book_status = Status.Available
        else:
            self.__book_status = Status.Incoming
        self.__available_date = available_date
        Book.count += 1
    
    @property
    def book_name(self):
        return self.__book_name 
    
    @property 
    def book_series(self):
        return self.__book_series
       
    @property
    def get_activity_type(self):
        return self.__activity_type

    def check_availability(self):
        return self.__book_status == "Available"

    def change_status(self, status):
        if isinstance(status, Status):
            self.__book_status = status.value
        
    def get_rate_info(self):
        return self.__price

    def change_activity_type(self, activity_type):
        if isinstance(activity_type, ActivityType):
            self.__activity_type = activity_type.value

class BookStock:
    def __init__(self, name):
        self.__name = name
        self.__forsale_book_list = []
        self.__rent_book_list = []

    @property
    def book_stock_name(self):
        return self.__name
    
    def add_book(self, book_object):
        if isinstance(book_object, Book):
            if book_object.get_activity_type == "Rent":
                for rent in self.__rent_book_list:
                    if rent.name_book == book_object.book_name:
                        rent.add_book(book_object)
                        return "Rent book add successful"
                bookname = BookName(book_object.book_name)
                bookname.add_book(book_object)
                self.__rent_book_list.append(bookname)
            elif book_object.get_activity_type == "Purchase":
                for forsale in self.__forsale_book_list:
                    if forsale.name_book == book_object.book_name:
                        forsale.add_book(book_object)
                        return "Purchase book add successful"
                bookname = BookName(book_object.book_name)
                bookname.add_book(book_object)
                self.__forsale_book_list.append(bookname)
            else:
                raise TypeError("Activity type error")
        else:
            raise TypeError("Need to be a book")

    def remove_book(self, book_object):
        if isinstance(book_object, Book):    
            if book_object.get_activity_type == "Purchase":
                self.__forsale_book_list.remove(book_object)
            elif book_object.get_activity_type == "Rent":
                self.__rent_book_list.remove(book_object)

    def search_book_available(self, bookname, activity_type):
        if activity_type == "Rent":
            for book_name in self.__rent_book_list:
                if book_name.name_book == bookname:
                    return book_name.search_book_available()
        elif activity_type == "Purchase":
            for book_name in self.__forsale_book_list:
                if book_name.name_book == bookname:
                    return book_name.search_book_available()
        else:                
            raise TypeError("Activity type error")
        
class BookName:
    def __init__(self, name):
        self.__name = name
        self.__book = []

    @property
    def name_book(self):
        return self.__name

    def add_book(self, book):
        if isinstance(book, Book):
            self.__book.append(book)

    def search_book_available(self):
        for book in self.__book:
            if book.check_availability():
                return book
            
class Area:
    def __init__(self):
        pass

class TimeSlot:
    def __init__(self):
        pass

class Purchase:
    def __init__(self, purchase_items):
        self.__purchase_items = purchase_items if purchase_items else []

    def calculate_subtotal(self):
        total = 0.0
        for item in self.__purchase_items:
            total += item.get_rate_info()
        return total
    
    @property
    def purchase_items(self):
        return self.__purchase_items

class RentBook(Purchase):
    def __init__(self, purchase_items):
        super().__init__(purchase_items)

class BookingBook(Purchase):
    def __init__(self, purchase_items):
        super().__init__(purchase_items)

class BookingArea(Purchase):
    def __init__(self, purchase_items):
        super().__init__(purchase_items)

class PaymentMethod(ABC):
    @abstractmethod
    def process_payment(self, amount):
        pass

class QRCode(PaymentMethod):
    def __init__(self, gateway_reference):
        self.__gateway_reference = gateway_reference #รหัสอ้างอิง คล้ายพวกเลขสลีป

    def process_payment(self, amount):
        print(f"กำลังทำรายการจ่ายเงินผ่าน QR Code (Ref: {self.__gateway_reference}) ยอด: {amount} บาท")
        return True 

class Cash(PaymentMethod):
    def process_payment(self, amount):
        print(f"กำลังทำรายการจ่ายเงินสดหน้าเคาน์เตอร์ ยอด: {amount} บาท")              
        return True

class Payment:
    def __init__(self, customer, order_list, payment_method_str):
        self.__customer = customer
        self.__payment_no = f"PAY-{uuid.uuid4().hex[:8].upper()}" 
        self.__status = "Unpaid" # "Unpaid", "Paid", "Voided"
        self.__order = order_list
        self.__timestamp = datetime.now()
        self.__payment_method = payment_method_str

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

    def update_payment_status(self, status):
        self.__status = status
 
    def add_penalty_fee(self, amount):
        self.__penalty_fee += amount
        self.calculate_net_amount()


class Transaction:
    def __init__(self, user, staff, status, payment):
        self.__user = user
        self.__staff = staff
        self.__status = "Requested" # "Requested, Confirmed, In Use, Completed, Cancelled"
        self.__payment = payment
        self.__start_date_time = datetime.now()
        self.__end_date_time = datetime.now()
        self.__audit_logs_list = []

    def update_status(self, status):
        self.__status = status

    def add_audit_log(self, log_message):
        self.__audit_logs_list.append(log_message)
    
    def sync_payment_with_activity():
        pass
        
class Notification:
    count = 0
    def __init__(self, customer, message):
        self.__customer = customer
        self.__message = message
        self.__uid = f"NT-{customer.name}-{Notification.count}"

class Promotion(ABC):
    def __init__(self,promo_code,discount_rate):
        self.__promo_code = promo_code
        self.__discount_rate = discount_rate
        self.__status = False
        self.__used_user = []

    @abstractmethod
    def is_eligible(self):
        pass

    def apply_discount(self):
        pass

class DoubleDate:
    def is_eligible(self):
        pass

class BirthDate:
    def is_eligible(self):
        pass

bibliohub = System()



app = FastAPI()
@app.get("/")
def redirect_to_docs():
    return RedirectResponse(url="/docs")