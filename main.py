from fastapi import FastAPI, Query
from fastapi.responses import RedirectResponse
import uvicorn

app = FastAPI()

class System :
    def __init__(self):
        self.__staff_list = []
        self.__promotion_list = []
        self.__book_stock = []
        self.__area = []
        self.__customer_list = []
        self.__transaction_list = []
        self.__notification_list = []

    def register(self,name,surname,phonenumber,email):
        """
        Registering create member object by using nonmember data.
        :param name: name of customer
        :param surname: surname of customer
        :param phonenumber: phonenumber of customer
        :param email: email of customer
        """

        if (not self.validate_input_data()):
            raise ValueError()
        
        if (self.check_duplicate_account):
            raise IndexError()
        
        member = Member(name,surname,phonenumber,email)
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

        if len(clean_digits) == 10:
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

        net_amount = payment.process_payment() #need implement : calculate payment ใน payment ไปเลย
        transaction.add_audit_log() #need implement : เพิ่มรูปแบบของ audit log
        transaction.update_status("Confirm")

        # ส่วนท้ายการทำงาน need implement : ถ้ารายการไหนต้อง update status ของสินค้ามาทำในส่วนนี้
    
        customer.add_transaction()

        self.notify_user(customer,"transaction ... confirm") #need implement : ต้องเปลี่ยนคำ

        return "ทำรายการเสร็จสิ้น"

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

class Book:
    def __init__(self):
        pass

class Member:
    def __init__(self):
        pass

class RentBook:
    def __init__(self):
        pass
            
class NonMember:
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
        self.__booking_reservation_time = None
        self.__rental_quota = 0
        self.__strike = 0
        self.__selected_list = []


@app.get("/")
def redirect_to_docs():
    return RedirectResponse(url="/docs")

@app.get("/get_customer_information")
def get_customer_information(name:str = Query(description="ชื่อจริงลูกค้า"),surname:str = Query(description="นามสกุลลูกค้า"),phonenumber:int = Query(description="เบอร์โทรศัพทธ์ลูกค้า"),email:str = Query(description="อีเมลลูกค้า")):
    Customer = NonMember(name,surname,phonenumber,email)
    return Customer

# @app.get("/test")
# def read_root(request:str, reply:str):
#     return {"Request":request, "Reply": reply}

# @app.get("/items/{item_id}/{q}")
# def read_item(item_id: int, q: str | None = None):
#     return {"item_id": item_id, "q": q}

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, log_level="info",reload=True)