from __future__ import annotations
from fastapi import FastAPI, Query, HTTPException, status
from fastapi.responses import RedirectResponse
from datetime import datetime, date, timedelta
from enum import Enum
from abc import ABC, abstractmethod
import uvicorn
from contextlib import asynccontextmanager

app = FastAPI()

# Enum Class

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

class MethodPayment(str,Enum):
    cash = "cash"
    qrcode = "qrcode"

class ActivityType(str, Enum):
    Rent = "Rent"
    Purchase = "Purchase"

class TypeBook(str,Enum):
    Manga = "Manga"
    Novel = "Novel"
    Historical = "Historical"
    Education = "Education"
    Self_improvement = "Self Improvement"
    Economic = "Economic"

class BookStatus(str,Enum):
    Available = "Available"
    UnAvailable = "UnAvailable"
    Selected = "Selected"
    Purchased = "Purchased"
    Incoming = "Incoming"

class PaymentStatus(str,Enum):
    Unpaid = "Unpaid"
    Paid = "Paid"
    Voied = "Voied"

class TransactionStatus(str,Enum):
    Requested = "Requested"
    Confirm = "Confirm"
    In_Use = "In Use"
    Completed = "Completed"
    Cancelled = "Cancelled"

# Core Class

class Area:
    def __init__(self):
        pass

class Book:
    def __init__(self,book_info:BookInfo,status:BookStatus):
        """
        class Book คือหนังสือที่แยกตาม UID คือหนังสือแต่ละเล่มแยกกันไป เช่น โดเรม่อน เล่มที่ x อันที่ x 
        
        :param book_info: object ที่มีข้อมูลของหนังสือ
        :type book_info: BookInfo
        :param status: สถานะของหนังสือเล่มนั้น
        :type status: BookStatus
        """
        self.__book_info = book_info
        self.__book_uid = None
        self.__borrowed_count = 0
        self.__book_status = status
        self.__start_date = None 
        self.__end_date = None
        self.__actual_return_date = None
    
    @property
    def book_info(self):
        return self.__book_info

    @property
    def uid(self):
        return self.__book_uid
    
    @uid.setter
    def uid(self,id):
        self.__book_uid = id

    @property
    def book_status(self) -> BookStatus:
        return self.__book_status

    @property
    def actual_return_date(self):
        return self.__actual_return_date
    
    @actual_return_date.setter
    def actual_return_date(self,date):
        self.__actual_return_date = date
    
    @property
    def start_date(self):
        return self.__start_date
    
    @start_date.setter
    def start_date(self,date : date):
        self.__start_date = date

    @property
    def end_date(self):
        return self.__end_date
    
    def calculate_end_date(self,how_many_days : int):
        self.__end_date = self.__start_date + timedelta(days=how_many_days)

    def check_available(self):
        return self.__book_status == BookStatus.Available.value
    
    def change_status(self,status:BookStatus):
        self.__book_status = status.value
    
    def change_activity_type(self,activity_type:ActivityType):
        self.__activity_type = activity_type

class BookInfo:
    def __init__(self,book_stock : BookStock,name,author,category:TypeBook,price,activity_type : ActivityType,available_date=date.today()):
        """
        class BookInfo คือตัวข้อมูลของหนังสือ และจะเป็นตัวเก็บ Book ไว้ เช่น โดเรม่อน เล่มที่ x แล้วข้างในจะเก็บว่ามีโดเรม่อนเล่ม x กี่เล่ม
        
        :param book_stock: object ที่เป็นตัวเก็บ stock หนังสือ
        :type book_stock: BookStock
        :param name: ชื่อของหนังสือเล่มนั้น เช่น โดเรม่อน เล่ม 1
        :param author: ผู้แต่งของหนังสือ
        :param category: ประเภทของหนังสือ
        :type category: TypeBook
        :param price: ราคาในการใช้บริการหนังสือ
        :param activity_type: ประเภทการใช้บริการหนังสือ เช่น ซื้อ หรือ เช่า
        :type activity_type: ActivityType
        :param available_date: วันที่หนังสือเล่มนั้นวางขาย
        """
        self.__name = name
        self.__book_stock = book_stock
        self.__author = author
        self.__category = category
        self.__price = price
        self.__activity_type = activity_type
        self.__book : list[Book] = []
        self.__available_date = available_date
        self.__id = f"BK-{activity_type.value}-{book_stock.name.replace(" ","_")}-{name.replace(" ","_")}-{author}"
    
    @property
    def bookinfo_name(self):
        return self.__name
    
    @property
    def book_stock(self):
        return self.__book_stock
    
    @property
    def author(self):
        return self.__author
    
    @property
    def category(self) -> TypeBook:
        return self.__category
    
    @property
    def price(self):
        return self.__price
    
    @property
    def activity_type(self) -> ActivityType:
        return self.__activity_type
        
    @property
    def available_date(self) -> date:
        return self.__available_date
    
    @property
    def id(self):
        return self.__id
    
    @property
    def copies(self):
        return len(self.__book)
    
    def add_copies(self,copies:int):
        if self.__available_date <= date.today():
            status = BookStatus.Available
        else:
            status = BookStatus.Incoming
        
        for _ in range(copies):
            book = Book(self,status)
            book.uid = f"{self.__id}-{len(self.__book)}"
            self.__book.append(book)

    def search_book_available(self):
        for book in self.__book:
            if book.check_available():
                return book

class BookOrder:
    def __init__(self, book_info, num_days):
        self.__book_info = book_info
        self.__num_days = num_days
        self.__book_info_oder = []

    def add_bookinfo(self, book_info):
        if isinstance(book_info, BookInfo):
            self.__book_info_oder.append(book_info)

    @property
    def book_info(self):
        return self.__book_info
    
    @property
    def num_days(self):
        return self.__num_days

class BookStock:
    def __init__(self,name):
        """
        class BookStock คือ ตัวสต๊อกของหนังสือ จะเป็นตัวที่เก็บ BookInfo ไว้ เช่น โดเรม่อน แล้วข้างในจะเป็น โดเรม่อน เล่มที่ x อีกที

        :param name: ชื่อของ stock เช่น โดเรม่อน
        """
        self.__name = name
        self.__forsale_book_list : list[BookInfo] = []
        self.__rent_book_list : list[BookInfo] = []

    @property
    def name(self):
        return self.__name
    
    def get_book_list(self,activity_type : ActivityType):
        if activity_type.value == "Rent":
            return self.__rent_book_list
        elif activity_type.value == "Purchase":
            return self.__forsale_book_list
        else:
            raise TypeError("Wrong Activity Type")

    def add_book_info(self,book_info:BookInfo,activity_type:ActivityType):
        if not isinstance(book_info,BookInfo):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Not a right book info"
            )
        
        if activity_type.value == "Rent":
            self.__rent_book_list.append(book_info)
        elif activity_type.value == "Purchase":
            self.__forsale_book_list.append(book_info)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Not a right activity type"
            )
                
    def remove_book(self,book):
        if isinstance(book,Book):
            if book.activity_type == ActivityType.Rent:
                self.__rent_book_list.remove(book)
            elif book.activity_type == ActivityType:
                self.__forsale_book_list.remove(book)
            else:
                raise TypeError("Activity type error")
        else:
            raise TypeError("Need to be a book")
        
    def search_book_available(self,bookname,activity_type):
        target_list = self.get_book_list(activity_type)
        for book_name_object in target_list:
            if book_name_object.bookinfo_name == bookname:
                return book_name_object.search_book_available()                
        return None
    
    def search_bookinfo(self, bookinfo_name, activity_type): 
        target_list = self.get_book_list(activity_type)      
        for bookinfo in target_list:
            if bookinfo.bookinfo_name == bookinfo_name:
                return bookinfo
        return None            
        
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
        self.__booking_reservation_time = None
        self.__rental_quota = 0
        self.__strike = 0
        self.__selected_list : list[Book,Area] = []

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

    def check_eligibility(self):
        return self.__strike < 3
    
    def check_quota(self): 
        return len([selected for selected in self.__selected_list if isinstance(selected,Book) and selected.book_info.activity_type.value == "Rent"]) < (4 - self.__rental_quota)

    def select(self,order : BookInfo | Area, num_days=0) -> str | BookInfo | Area: #num_days ไม่รู้ว่าต้องกำหนดยังไงเป็นหน้าทีของrentมั้ยนะ
        if isinstance(order, (BookInfo, Area)):
            if isinstance(order, BookInfo):
                bookorder = BookOrder(order, num_days)
                self.__selected_list.append(bookorder)
                return bookorder
            elif isinstance(order, Area):
                self.__selected_list.append(order)
        # Need implement Area
        """
        if isinstance(order,Area):
            return order.something(Status.Selected)
        """

    def add_notify(self,notification):
        if isinstance(notification,Notification):
            self.__notification_list.append(notification)

    def add_transaction(self,transaction):
        if isinstance(transaction,Transaction):
            self.__transaction.append(transaction)

class Member(Customer):
    def __init__(self, name, surname, phonenumber, email, birth_month : BirthMonth):
        super().__init__(name, surname, phonenumber, email)

        self.__level_member = LevelMember.Silver
        self.__birth_month = birth_month
        self.__points = 0
        self.__booking_book_quota = BookingBookQuota.Silver
        try:
            self.__expiration_date = date.today().replace(year=date.today().year + 1)
        except:
            self.__expiration_date = date.today().replace(year=date.today().year + 1,month=3, day=1)
    
    def add_point(self):
        self.__points += 1

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

class Purchase:
    def __init__(self,order : list[Book,Area]):
        self._order : list[Book,Area] = order

    @property
    def get_order(self):
        return self._order

    def calculate_subtotal(self):
        total = 0.0
        for item in self._order:
            if isinstance(item, Book):
                total += item.book_info.price
        return total 
    
    def confirm(self):
        for item in self._order:
            if isinstance(item, Book):
                item.change_status(BookStatus.Purchased)

class RentBook(Purchase):
    def __init__(self,order : list[Book,Area]):
        super().__init__(order)
        self.__late_penalty_rate = 10

    def get_penalty(self):
        penalty = 0

        for item in self._order:
            penalty += (item.actual_return_date - item.end_date).days * self.__late_penalty_rate
        return penalty
    
    def confirm(self):
        for item in self._order:
            if isinstance(item, Book):
                item.change_status(BookStatus.UnAvailable)
    
class Order:
    def __init__(self):
        self.__rent_book : RentBook = None
        self.__purchase_book : Purchase = None

    @property
    def info(self):
        def format_book(book : Book):
            return {
                "Book Name" : book.book_info.name,
                "Book Series" : book.book_info.book_stock.name,
                "Book Author" : book.book_info.author,
                "Book Category" : book.book_info.category.value,
                "Book Price" : book.book_info.price,
                "Book Activity Type" : book.book_info.activity_type.value,
                "Book Available Date" : book.book_info.available_date,
                "Book Status" : book.book_status,
                "Book UID" : book.uid
            }
        res = {}
        if self.__rent_book:
            res["Rent Book"] = [format_book(e) for e in self.__rent_book.get_order if isinstance(e, Book)]
        if self.__purchase_book:
            res["Purchase Book"] = [format_book(e) for e in self.__purchase_book.get_order if isinstance(e, Book)]
        return res

    @property
    def rent_book(self):
        return self.__rent_book
    
    @rent_book.setter
    def rent_book(self,rent_book : RentBook):
        self.__rent_book = rent_book

    @property
    def purchase_book(self):
        return self.__purchase_book
    
    @purchase_book.setter
    def purchase_book(self,purchase_book):
        self.__purchase_book = purchase_book

    def calculate_subtotal(self):
        purchase = self.__purchase_book.calculate_subtotal() if self.__purchase_book else 0.0
        rent = self.__rent_book.calculate_subtotal() if self.__rent_book else 0.0
        return purchase + rent
    
    def confirm(self):
        self.__purchase_book.confirm()
        self.__rent_book.confirm()

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

class PaymentMethod(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def process_payment(self):
        pass

class Cash(PaymentMethod):
    def __init__(self):
        self.__name = "Cash"

    @property
    def name(self):
        return self.__name

    def process_payment(self,Amount):
        return f"Process with Cash : {Amount}"

class QRCode(PaymentMethod):
    def __init__(self,phonenumber):
        self.__name = "QR Code"
        self.__phonenumber = phonenumber

    @property
    def name(self):
        return self.__name

    def process_payment(self,Amount):
        return f"Process with QRCode : {Amount} code QR-{self.__phonenumber}"

class Payment:
    count = 0
    def __init__(self,customer : Customer,order : Order,payment_method : PaymentMethod):
        self.__customer = customer
        self.__payment_no = f"PYM-{Payment.count}"
        self.__status = PaymentStatus.Unpaid.value
        self.__order : Order = order
        self.__timestamp = datetime.now()
        self.__payment_method = payment_method
        self.__base_fee = 10 # เท่าไหร่อ่ะ need implement
        self.__upgrade_delta = 0
        self.__discount_amount = 0
        self.__penalty_fee = 0
        self.__net_amount = 0

        Payment.count += 1

    @property
    def payment_no(self):
        return self.__payment_no
    
    @property
    def status(self):
        return self.__status
    
    @property
    def order(self):
        return self.__order
    
    @property
    def timestamp(self):
        return self.__timestamp

    @property
    def payment_method(self) -> PaymentMethod:
        return self.__payment_method
    
    @property
    def base_fee(self):
        return self.__base_fee
    
    @property
    def upgrade_delta(self):
        return self.__upgrade_delta
    
    @property
    def discount_amount(self):
        return self.__discount_amount
    
    @property
    def penalty_fee(self):
        return self.__penalty_fee
    
    @property
    def net_amount(self):
        return self.__net_amount

    def calculate_net_amount(self):
        subtotal = self.__order.calculate_subtotal()
        self.__net_amount = subtotal + self.__upgrade_delta - self.__discount_amount + self.__base_fee + self.__penalty_fee
        return self.__net_amount
    
    def update_payment_status(self,status:PaymentStatus):
        self.__status = status.value

    def add_penalty_fee(self,penalty_fee):
        self.__penalty_fee += penalty_fee

class Transaction:
    def __init__(self,customer:Customer,staff:Staff,payment : Payment,start_date_time : datetime = datetime.now(), end_date_time : datetime = datetime.now()):
        self.__customer = customer
        self.__staff = staff
        self.__start_date_time = start_date_time
        self.__end_date_time = end_date_time
        self.__status = TransactionStatus.Requested.value
        self.__payment = payment
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

    def update_status(self,status:TransactionStatus):
        self.__status = status.value

    def add_audit_log(self,log):
        self.__audit_logs_list.append(log)

    def sync_payment_with_activity(self,rentbook : RentBook):
        return True
    
class Notification:
    count = 0
    def __init__(self,customer,message):
        self.__customer = customer
        self.__message = message
        self.__uid = f"NT-{customer.name}-{Notification.count}"

# Contoller Class

class System:
    def __init__(self):
        self.__staff_list : list[Staff] = []
        self.__promotion_list : list[Promotion] = []
        self.__book_stock : list[BookStock] = []
        self.__area : list[Area] = []
        self.__customer_list : list[Customer] = []
        self.__transaction_list : list[Transaction] = []
        self.__notification_list : list[Notification] = []

    def register(self,name,surname,phonenumber,email) -> Member | str:
        """
        Registering create member object by using Customer data.
        :param name: name of customer
        :param surname: surname of customer
        :param phonenumber: phonenumber of customer
        :param email: email of customer
        """

        if (not (self.validate_name_and_surname(name,surname) and self.validate_email(email) and self.validate_phonenumber(phonenumber))):
            return "Input not in a right form"
        
        if (self.check_duplicate_account(phonenumber)):
            return "Account duplicated"
        
        member = Member(name,surname,phonenumber,email)
        self.__customer_list.append(member)

        return member
    
    def add_customer(self,customer):
        if isinstance(customer,Customer):
            if (not (self.validate_name_and_surname(customer.name,customer.surname) and self.validate_email(customer.email) and self.validate_phonenumber(customer.phonenumber))):
                raise ValueError()
            
            if (self.check_duplicate_account(customer.phonenumber)):
                raise IndexError()
            self.__customer_list.append(customer)
            return "Add customer successful"

    def delete_customer(self,customer):
        if isinstance(customer,Customer):
            self.__customer_list.remove(customer)
            return "Remove customer successful"
        return "Not Found"

    def get_customer_list(self) -> list:
        """
        return customer list in list
        """
        return self.__customer_list

    def check_duplicate_account(self,phonenumber) -> bool:
        """
        checking for duplicated account return in bool
        true if found duplicated
        false if not found duplicated
        
        :param phonenumber: เบอร์โทรศัพทธ์ผู้ใช้สำหรับค้นหาผู้ใช้ว่ามีหรือไม่
        """
        return self.get_user_from_phone_number(phonenumber) in self.__customer_list

    def validate_name_and_surname(self,name,surname) -> bool:
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

        return True

    def validate_phonenumber(self,phonenumber) -> bool:
        phone_str = str(phonenumber).strip()

        if phone_str.startswith("+"):
            digits_only = phone_str[1:]
        else:
            digits_only = phone_str

        clean_digits = digits_only.replace("-", "").replace(" ", "")

        if not clean_digits.isdigit():
            raise ValueError("Phone number contains invalid characters.")

        if len(clean_digits) != 10:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Phone number length is invalid (should be 10 digits). {len(clean_digits)}"
            )
        
        return True

    def validate_email(self,email) -> bool:
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
        
        return True

    def get_user_from_phone_number(self,phonenumber) -> Customer | None:
        if self.validate_phonenumber(phonenumber):
            for member in self.__customer_list:
                if member.phonenumber == phonenumber:
                    return member
        return None
    
    def get_all_book(self):
        return self.__book_stock
    
    def search_book(self,book_series) -> dict | str:
            for bookstock in self.__book_stock:
                if bookstock.name == book_series:
                    return bookstock
            return "Not Found"
            
    def get_book(self,book_series,bookname,activity_type) -> Book | None:
            for bookstock in self.__book_stock:
                if bookstock.name == book_series:
                    return bookstock.search_book_available(bookname,activity_type) 
            return None
                
    def search_area(self,customer,area_id) -> Area | None:
        if not customer.check_eligibility():
                raise PermissionError("Not come in to my place go away don't comeback")
        
        for area in self.__area:
            if area.id == area_id:
                return area.list_timeslot()
            
    def checkout(self,customer:Customer,staff:Staff,payment_method : MethodPayment):
        order = Order()
        rent_list = []
        purchase_list = []

        if not isinstance(customer,Customer):
            return "Not a customer"
        
        selected_list = customer.get_selected_list

        rent_list = [selected for selected in selected_list if isinstance(selected, Book) and selected.book_info.activity_type.value == "Rent"]
        purchase_list = [selected for selected in selected_list if isinstance(selected, Book) and selected.book_info.activity_type.value == "Purchase"]

        order.rent_book = RentBook(rent_list)
        order.purchase_book = Purchase(purchase_list)

        if payment_method == MethodPayment.cash:
            payment_method = Cash()
        elif payment_method == MethodPayment.qrcode:
            payment_method = QRCode(customer.phonenumber)
        else:
            raise TypeError("Method Payment error")
        payment = Payment(customer,order,payment_method)
        transaction = Transaction(customer,staff,payment,datetime.now(),datetime.now())

        transaction.add_audit_log(f"Transaction requested : {datetime.now().strftime("%d/%m/%Y, %H:%M:%S")}") #need implement : เพิ่มรูปแบบของ audit log
        net_amount = payment.payment_method.process_payment(payment.calculate_net_amount()) #need implement : calculate payment ใน payment ไปเลย
        print(net_amount)

        payment.update_payment_status(PaymentStatus.Paid)
        transaction.update_status(TransactionStatus.Confirm)
        transaction.add_audit_log(f"transaction completed : {datetime.now().strftime("%d/%m/%Y, %H:%M:%S")}")

        # ส่วนท้ายการทำงาน need implement : ถ้ารายการไหนต้อง update status ของสินค้ามาทำในส่วนนี้
        order.confirm()

        self.__transaction_list.append(transaction)
        customer.add_transaction(transaction)

        self.notify_user(customer,f"{customer.name}: transaction ... confirm") #need implement : ต้องเปลี่ยนคำ

        if isinstance(customer,Member):
            customer.add_point()

        self.notify_user(customer,f"{customer.name}: add point successful")
        print("Checkout Successful")
        return transaction
    
    def verify_permission(self,manager) -> bool:
        return isinstance(manager,Manager)
    
    def add_book(self,book_name,series,author,category,price,activity_type,number_of_copies,available_date) -> str:
        inputs_to_validate = [book_name, series, author]
    
        for input in inputs_to_validate:
            if isinstance(input, str):
                if "_" in input or "-" in input:
                    raise ValueError(f"ไม่อนุญาตให้ใส่ '_' หรือ '-' ในข้อมูล: '{input}'")
        
        if price <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="ราคาต้องมากกว่า 0"
            )
        
        if number_of_copies <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="จำนวนเล่มต้องมากกว่า 0"
            )
        
        book_stock = None
        
        for stock in self.__book_stock:
            if stock.name == series:
                book_stock = stock
                break

        if not book_stock:
            book_stock = BookStock(series)
            book_info_obj = BookInfo(book_stock,book_name,author,category,price,activity_type,available_date)
            book_info_obj.add_copies(number_of_copies)
            book_stock.add_book_info(book_info_obj,activity_type)
            self.__book_stock.append(book_stock)
            return "Create BookStock,BookInfo and Add Copy Successful"


        for book_info_obj in book_stock.get_book_list(activity_type):
            if book_info_obj.name == book_name:
                book_info_obj.add_copies(number_of_copies)
                return "Add Copy Successful"
                    
        book_info_obj = BookInfo(book_stock,book_name,author,category,price,activity_type,available_date)
        book_info_obj.add_copies(number_of_copies)
        book_stock.add_book_info(book_info_obj,activity_type)
        return "Create BookInfo and Add Copy Successful"

    def add_staff(self,staff):
        if isinstance(staff,Staff):
            self.__staff_list.append(staff)
            return "Add Staff Successful"

    @property
    def get_staff_list(self):
        return self.__staff_list
    
    def get_staff_by_no_staff(self,no_staff):
        for staff in self.__staff_list:
            if staff.no_staff == no_staff:
                return staff
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Staff Not Found"
        )

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
            customer.add_strike()

    def reduce_strike(self,customer):
        if isinstance(customer,Customer):
            customer.reduce_strike()

    def notify_user(self,customer,message):
        if isinstance(customer,Customer):
            if isinstance(message,str):
                notification = Notification(customer,message)
                customer.add_notify(notification)
                self.__notification_list.append(notification)

    def upgrade_booking_area(self):
        pass

    def generate_utilization_report(self):
        pass        
    
Bibliohub = System()

@app.get("/")
def redirect_to_docs():
    return RedirectResponse(url="/docs")

@app.get("/search_book")
def search_book(phonenumber: str, series_name: str):
    customer = Bibliohub.get_user_from_phone_number(phonenumber)
    if not customer:
        raise HTTPException(status_code=404, detail="ไม่พบเบอร์นี้ในระบบ")
        
    if not customer.check_eligibility():
        raise HTTPException(status_code=403, detail="คุณโดนแบน (Strike >= 3)")

    result = Bibliohub.search_book(series_name)
    if result == "Not Found":
        return {"message": "ไม่พบหนังสือที่หา"}
    
    return {"series": result.name, "detail": "พบหนังสือที่คุณต้องการ"}


@app.get("/")
def redirect_to_docs():
    return RedirectResponse(url="/docs")

@app.get("/search_book")
def search_book(phonenumber: str, series_name: str):
    customer = Bibliohub.get_user_from_phone_number(phonenumber)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found. Please register first.")
    
    if not customer.check_eligibility():
        raise HTTPException(status_code=403, detail="Access denied. Strike limit reached.")

    result = Bibliohub.search_book(series_name)
    if result == "Not Found":
        raise HTTPException(status_code=404, detail="Book series not found.")
    
    return {
        "series": result.name,
        "available_for_rent": [b.name for b in result.get_book_list(ActivityType.Rent)],
        "available_for_purchase": [b.name for b in result.get_book_list(ActivityType.Purchase)]
    }

@app.post("/add_book")
def add_book(
    book_name: str, 
    series: str, 
    author: str, 
    category: TypeBook, 
    price: float, 
    activity_type: ActivityType, 
    copies: int,
    available_date: date = date.today()
):
    msg = Bibliohub.add_book(book_name, series, author, category, price, activity_type, copies, available_date)
    return {"status": "Success", "detail": msg}

@app.post("/add_customer")
def add_customer(name: str, surname: str, phonenumber: str, email: str):
    new_customer = Customer(name, surname, phonenumber, email)
    msg = Bibliohub.add_customer(new_customer)
    return {"status": "Success", "detail": msg}

@app.post("/select")
def select_item(phonenumber: str, series: str, book_name: str, activity_type: ActivityType):
    customer = Bibliohub.get_user_from_phone_number(phonenumber)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found.")

    book = Bibliohub.get_book(series, book_name, activity_type)
    if not book:
        raise HTTPException(status_code=400, detail="Book not available for the requested activity type.")

    if activity_type == ActivityType.Rent:
        if not customer.check_quota():
            raise HTTPException(status_code=400, detail="Rental quota exceeded.")

    selected_node = customer.select(book)
    return {
        "status": "Item selected",
        "book_uid": book.uid,
        "activity": activity_type.value
    }

@app.get("/cart")
def view_cart(phonenumber: str):
    customer = Bibliohub.get_user_from_phone_number(phonenumber)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found.")
    
    cart_content = []
    for item in customer.get_selected_list:
        if isinstance(item, Book):
            cart_content.append({
                "uid": item.uid,
                "name": item.book_info.name,
                "activity": item.book_info.activity_type.value,
                "price": item.book_info.price
            })
    return {
        "customer": f"{customer.name} {customer.surname}",
        "cart": cart_content
    }

@app.delete("/del_cart")
def delete_from_cart(phonenumber: str, book_uid: str):
    customer = Bibliohub.get_user_from_phone_number(phonenumber)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found.")

    for item in customer.get_selected_list:
        if isinstance(item, Book) and item.uid == book_uid:
            item.change_status(BookStatus.Available)
            customer.get_selected_list.remove(item)
            return {"status": "Success", "message": f"Removed {book_uid} from cart."}
            
    raise HTTPException(status_code=404, detail="Item not found in cart.")

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, log_level="info",reload=True)