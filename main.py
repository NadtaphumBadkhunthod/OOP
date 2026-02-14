from fastapi import FastAPI, Query
from fastapi.responses import RedirectResponse
from datetime import datetime, date
from enum import Enum
import uvicorn

app = FastAPI()

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

class Status(str,Enum):
    Available = "Available"
    UnAvailable = "UnAvailable"
    Selected = "Selected"
    Purchased = "Purchased"
    Incoming = "Incoming"

class Notification:
    count = 0
    def __init__(self,customer,message):
        self.__customer = customer
        self.__message = message
        self.__uid = f"NT-{customer.name}-{Notification.count}"

class Area:
    def __init__(self):
        pass

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
    def __init__(self):
        pass

class Payment:
    def __init__(self):
        pass

class Purchase:
    def __init__(self):
        pass                    

class RentBook:
    def __init__(self):
        pass
            
class BookStock:
    def __init__(self,name):
        self.__name = name
        self.__forsale_book_list = []
        self.__rent_book_list = []

    @property
    def name(self):
        return self.__name

    def add_book(self,book):
        if isinstance(book,Book):
            if book.get_activity_type == "Rent":
                for rent_book in self.__rent_book_list:
                    if rent_book.name == book.name:
                        rent_book.add_book(book)
                        return "Rent book add successful"
                bookname = BookName(book.name)
                bookname.add_book(book)
                self.__rent_book_list.append(bookname)
            elif book.get_activity_type == "Purchase":
                for forsale_book in self.__forsale_book_list:
                    if forsale_book.name == book.name:
                        forsale_book.add_book(book)
                        return "Rent book add successful"
                bookname = BookName(book.name)
                bookname.add_book(book)
                self.__forsale_book_list.append(bookname)
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
        
    def search_book_available(self,bookname,activity_type):
        if activity_type == "Rent":
            for book_name_object in self.__rent_book_list:
                if book_name_object.name == bookname:
                    return book_name_object.search_book_available()
        elif activity_type == "Purchase":
            for book_name_object in self.__forsale_book_list:
                if book_name_object.name == bookname:
                    return book_name_object.search_book_available()
        else:
            raise TypeError("Activity type error")

class BookName:
    def __init__(self,name):
        self.__name = name
        self.__book = []
    
    @property
    def name(self):
        return self.__name
    
    def add_book(self,book):
        if isinstance(book,Book):
            self.__book.append(book)

    def search_book_available(self):
        for book in self.__book:
            if book.check_available():
                return book

class Book:
    count = 0

    def __init__(self,name,series,author,category,price,activity_type,available_date=date.today()):
        self.__book_name = name
        self.__book_series = series
        self.__book_uid = f"BK-{activity_type}-{series}-{name.replace(" ","_")}-{author}-{Book.count}"
        self.__author = author
        self.__category = category
        self.__price = price
        self.__activity_type = activity_type
        self.__borrowed_count = 0
        if available_date <= date.today():
            self.__book_status = "Available"
        else:
            self.__book_status = "Incoming"
        self.__available_date = available_date
        Book.count += 1

    @property
    def name(self):
        return self.__book_name

    @property
    def series(self):
        return self.__book_series

    def check_available(self):
        return self.__book_status == "Available"
    
    def change_status(self,status:Status):
        self.__book_status = status.value

    def get_rate_info(self):
        return self.__price
    
    def change_activity_type(self,activity_type:ActivityType):
        self.__activity_type = activity_type

    @property
    def get_activity_type(self):
        return self.__activity_type

class Customer:
    def __init__(self,name:str,surname:str,phonenumber:str,email:str):
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
        self.__booking_reservation_time = None
        self.__rental_quota = 0
        self.__strike = 0
        self.__selected_list = []
        self.__search_result = []

    @property
    def get_selected_list(self):
        return self.__selected_list

    @property
    def get_search_result(self):
        return self.__search_result

    def add_search_result(self,newsearch_result):
        if isinstance(newsearch_result,(Book,Area)):
            for result in self.__search_result:
                if result == newsearch_result:
                    print("Already search")
                    return "Already search"    
            self.__search_result.append(newsearch_result)
            return newsearch_result

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
        return len([selected for selected in self.__selected_list if isinstance(selected,Book) and selected.activity_type == "Rent"]) < 4

    def select(self,order) -> str | Book | Area:
        if isinstance(order,(Book,Area)):
            self.__selected_list.append(order)
            if isinstance(order,Book):
                order.change_status(Status.Selected)
                self.__search_result.remove(order)
            
            # Need implement Area
            """
            if isinstance(order,Area):
                return order.something(Status.Selected)
            """

            return order
        return "Not Found"

    def unselect(self,order):
        if isinstance(order,(Book,Area)):
            self.__selected_list.remove(order)

    def add_notify(self,notification):
        if isinstance(notification,Notification):
            self.__notification_list.append(notification)

    def add_transaction(self,transaction):
        if isinstance(transaction,Transaction):
            self.__transaction.append(transaction)

class Member(Customer):
    def __init__(self, name, surname, phonenumber, email, birth_month):
        super().__init__(name, surname, phonenumber, email)

        self.__level_member = "Silver"
        self.__birth_month = birth_month
        self.__points = 0
        self.__booking_book_quota = 6 # silver 6 gold 8 platinum 10
        try:
            self.__expiration_date = date.today().replace(year=date.today().year + 1)
        except:
            self.__expiration_date = date.today().replace(year=date.today().year + 1,month=3, day=1)
    
    def add_point(self):
        self.__points += 1

class Staff(Member):
    count = 0
    def __init__(self, name, surname, phonenumber, email, birth_month,no_branch):
        super().__init__(name, surname, phonenumber, email, birth_month)
        self.__no_staff = f"STF-{Staff.count}"
        self.__no_branch = no_branch
    
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

class System:
    def __init__(self):
        self.__staff_list = []
        self.__promotion_list = []
        self.__book_stock = []
        self.__area = []
        self.__customer_list = []
        self.__transaction_list = []
        self.__notification_list = []

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
            raise ValueError(f"Phone number length is invalid (should be 10 digits). {len(clean_digits)}")
        
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
            
    def search_book(self,customer,book_series,bookname,activity_type) -> dict | str:
            if not isinstance(customer,Customer):
                return "Not a Customer"
            
            if not customer.check_eligibility():
                raise PermissionError("Not come in to my place go away don't comeback")
            
            for bookstock in self.__book_stock:
                if bookstock.name == book_series:
                    result = bookstock.search_book_available(bookname,activity_type)
                    add_result = customer.add_search_result(result)
                    return {
                        "Searching Result" : add_result,
                        "All Customer Search Result" : {i: book for i, book in enumerate(customer.get_search_result)}
                    }
            return "Not Found"
                
    def search_area(self,customer,area_id) -> Area | None:
        if not customer.check_eligibility():
                raise PermissionError("Not come in to my place go away don't comeback")
        
        for area in self.__area:
            if area.id == area_id:
                return area.list_timeslot()
            
    def checkout(self,customer,staff,selected_list,payment_method):
        list_order = []
        
        for item in selected_list:
            if isinstance(item,Book):
                match item.get_activity_type():
                    case "Rent":
                        list_order.append(RentBook(*item.data))
                        return
                    case "Purchase":
                        list_order.append(Purchase())
                        return
                    case _: raise ValueError("Error : Activity type not found")
        
        payment = Payment(customer,list_order,payment_method)
        transaction = Transaction(customer,staff,"datetime.now",payment)

        transaction.add_audit_log("request : datetime.now") #need implement : เพิ่มรูปแบบของ audit log
        net_amount = payment.process_payment() #need implement : calculate payment ใน payment ไปเลย
        print(net_amount)
        transaction.update_status("Confirm")

        # ส่วนท้ายการทำงาน need implement : ถ้ารายการไหนต้อง update status ของสินค้ามาทำในส่วนนี้
        for item in list_order:
            if isinstance(item,Book):
                match item.get_activity_type():
                    case "Rent":
                        item.change_status("Not Available")
                        print("change status successful") 
                        return

        self.__transaction_list.append(transaction)
        customer.add_transaction(transaction)

        self.notify_user(customer,f"{customer.name}: transaction ... confirm") #need implement : ต้องเปลี่ยนคำ

        if isinstance(customer,Member):
            customer.add_point()

        self.notify_user(customer,f"{customer.name}: add point successful")

        return "ทำรายการเสร็จสิ้น"
    
    def verify_permission(self,manager) -> bool:
        return isinstance(manager,Manager)
    
    def add_book(self,book) -> str:
        if isinstance(book,Book):
            for book_stock in self.__book_stock:
                if book_stock.name == book.series:
                    book_stock.add_book(book)
                    return "Add Book Successful"
        
        book_stock = BookStock(book.series)
        book_stock.add_book(book)
        self.__book_stock.append(book_stock)
        return "Create BookStock Successful"

    def remove_book(self,book_stock):
        if isinstance(book_stock,BookStock):
            self.__book_stock.remove(book_stock)

    def get_all_book(self) -> list:
        return self.__book_stock

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

Bibliohub = System()

@app.get("/")
def redirect_to_docs():
    return RedirectResponse(url="/docs")

@app.get("/create_customer")
def create_customer(name:str = Query(description="ชื่อจริงลูกค้า"),surname:str = Query(description="นามสกุลลูกค้า"),phonenumber:str = Query(description="เบอร์โทรศัพทธ์ลูกค้า"),email:str = Query(description="อีเมลลูกค้า")):
    customer = Customer(name,surname,phonenumber,email)
    Bibliohub.add_customer(customer)
    return customer

@app.get("/add_or_create_book")
def create_book(book_name:str,series:str,author:str,category:TypeBook,price:float,activity_type:ActivityType,available_date:date = Query(default=date.today(),description="ปี/เดือน/วัน")):
    print(Bibliohub.add_book(Book(book_name,series,author,category.value,price,activity_type.value,available_date)))
    return Bibliohub.get_all_book()

@app.get("/search_book")
def search_book(phonenumber:str,book_series:str , book_name:str,activity_type:ActivityType):
    return Bibliohub.search_book(Bibliohub.get_user_from_phone_number(phonenumber),book_series,book_name,activity_type.value)

@app.get("/select")
def select(phonenumber:str,order:int):
    customer = Bibliohub.get_user_from_phone_number(phonenumber)
    if order + 1 < len(customer.get_search_result):
        return "Order not in range"
    result = customer.select(customer.get_search_result[order])
    return {
        "Result" : result,
        "Customer Searching List" : customer.get_search_result,
        "Customer Selected List" : customer.get_selected_list
    }

create_customer("Sixsax","Saxsix","0956645474","68010366@kmitl.ac.th")
create_book("How to learn OOP","How to learn OOP","Sixsax",TypeBook.Education,12,ActivityType.Rent,date.today())

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, log_level="info",reload=True)