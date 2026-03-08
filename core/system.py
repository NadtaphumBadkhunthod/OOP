from fastapi import HTTPException, status
from datetime import datetime

from models.infos import ItemType, BirthMonth, PaymentOptions, ActivityType, ItemStatus, TransactionStatus, PromotionType
from models.books import Book, BookInfo, BookOrder, BookStock
from models.areas import Area, TimeSlot
from models.customers import Customer, Member, Staff, Manager
from models.transactions import Promotion, Transaction, Notification
from models.orders import Purchase,UpgradeArea

class System:
    def __init__(self):
        self.__staff_list : list[Staff] = []
        self.__promotion_list : list[Promotion] = []
        self.__book_stock : list[BookStock] = []
        self.__area : list[Area] = []
        self.__customer_list : list[Customer] = []
        self.__transaction_list : list[Transaction] = []
        self.__notification_list : list[Notification] = []
        self.__book_returned_list : list[Book] = []

    @property
    def book_returned_list(self):
        return self.__book_returned_list

    @property
    def list_area(self):
        return self.__area

    def register(self,name,surname,phonenumber,email,birth_month=BirthMonth.Jan) -> Member | str:
        """
        Registering create member object by using Customer data.
        :param name: name of customer
        :param surname: surname of customer
        :param phonenumber: phonenumber of customer
        :param email: email of customer
        """

        if (not (self.validate_name_and_surname(name,surname) and self.validate_email(email) and self.validate_phonenumber(phonenumber))):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Validation Fail"
            )
        
        if (self.check_duplicate_account(phonenumber)):
            return HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Account Duplicate"
            )
        
        member = Member(name,surname,phonenumber,email,birth_month)
        self.__customer_list.append(member)

        return member
    
    def add_customer(self,name,surname,phonenumber,email):
        if (not (self.validate_name_and_surname(name,surname) and self.validate_email(email) and self.validate_phonenumber(phonenumber))):
            raise ValueError()
        
        if (self.check_duplicate_account(phonenumber)):
            raise IndexError()
        self.__customer_list.append(Customer(name,surname,phonenumber,email))
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
    
    def get_book_stock(self,series):
        for bookstock in self.__book_stock:
            if bookstock.name == series:
                return bookstock

    def check_type_from_id(self,item_id:str) -> str:
        if item_id.startswith("BK"):
            return ItemType.Book
        elif item_id.startswith("AREA"):
            return ItemType.Area
        else:
            raise ValueError("Invalid ID format")
        
    def get_data_from_id(self,type_of_item:ItemType,item_id:str):
        if type_of_item == ItemType.Book:
            parts = item_id.split("-")
            activity_type = parts[1]
            series = parts[2].replace("_"," ")
            book_name = parts[3].replace("_"," ")
            author = parts[4].replace("_"," ")
            if activity_type == ActivityType.Rent.value:
                activity_type = ActivityType.Rent
            elif activity_type == ActivityType.Purchase.value:
                activity_type = ActivityType.Purchase
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Activity Type Not Found"
                )
            return activity_type,series,book_name,author
        elif type_of_item == ItemType.Area:
            parts = item_id.split("-")
            area_id = "-".join(parts[:3])
            time_slot_id = item_id
            return area_id, time_slot_id
        else:
            raise ValueError("Invalid ID format")
        
    def search_area(self,customer : Customer,area_id):
        if not customer.check_eligibility():
                raise PermissionError("Not come in to my place go away don't comeback")
        
        for area in self.__area:
            if area.area_id == area_id:
                available_slots = area.list_timeslot
                
                # โชว์ ID พ่วงไปด้วยเลย (เช่น "TS01: 09:00-10:00")
                return [f"{slot.slot_id}: {slot.start_time}-{slot.end_time}" for slot in available_slots]
                
        raise ValueError("ไม่พบพื้นที่ที่ค้นหา")

    def select(self,phonenumber : str,item_id : list[str],num_days : int = 1) -> dict | str:
        customer = self.get_user_from_phone_number(phonenumber)
        selectitem_list = []

        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="'User' Not Found"
            )
        for id in item_id:
            type_of_item = self.check_type_from_id(id)

            if type_of_item == ItemType.Book:
                activity_type,series,book_name,author = self.get_data_from_id(type_of_item,id)

                book_info = self.get_book_stock(series).get_book_info_by_name(book_name,author,activity_type)

                if not book_info:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Book Not Found, Maybe checking your book id"
                    )
                
                selectitem_list.append(book_info)
            elif type_of_item == ItemType.Area:
                area_id,time_slot_id = self.get_data_from_id(type_of_item,id)

                target_area = None
                for area in self.list_area:
                    if area.area_id == area_id:
                        target_area = area
                        break

                if not target_area:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="ไม่พบพื้นที่"
                    )
                
                target_time_slot = None
                for timeslot in area.list_timeslot:
                    if timeslot.slot_id == time_slot_id:
                        target_time_slot = timeslot
                        break
                        
                if not target_time_slot or target_time_slot.is_available != ItemStatus.Available:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"สล็อต {time_slot_id} ถูกจองไปแล้ว หรือไม่มีในระบบ (กรุณาทำรายการใหม่)"
                    )
                
                current_time = datetime.now().time()
                #current_time = datetime.strptime("13:00", "%H:%M").time()
                slot_start_time = datetime.strptime(target_time_slot.start_time, "%H:%M").time()
                
                if slot_start_time <= current_time:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"ไม่สามารถจองสล็อตที่เวลาผ่านไปแล้วได้ ({target_time_slot.start_time}-{target_time_slot.end_time})"
                    )
                
                if target_time_slot not in selectitem_list and target_time_slot not in customer.get_selected_list:
                    selectitem_list.append(timeslot)
                else:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"{target_time_slot} - Already Selected"
                    )

        all_book : list[BookInfo] = [book for book in selectitem_list if isinstance(book,BookInfo)] + [book.book_info for book in customer.get_selected_list if isinstance(book,BookOrder)]
        
        book_with_same_name : dict[BookInfo,int] = {}
        
        for book_info in all_book:
            if book_with_same_name.get(book_info):
                book_with_same_name[book_info] += 1
            else:
                book_with_same_name[book_info] = 1

        for book in book_with_same_name:
            if book_with_same_name.get(book) > book.get_nums_available():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"หนังสือ {book.name} มีไม่พอโปรดทำรายการใหม่"
                )
            

        if not customer.check_area_quota(len([request_slot for request_slot in selectitem_list if isinstance(request_slot,TimeSlot)])):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"สล็อตโควต้าเต็ม! คุณจองได้อีก {customer.get_area_quota() - customer.booking_reservation_time} ชม."
            )
        
        if not customer.check_rent_quota(len([rentbook for rentbook in selectitem_list if isinstance(rentbook,BookInfo) and rentbook.activity_type == ActivityType.Rent])):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"เช่าหนังสือโควต้าเต็ม! คุณจองได้อีก {customer.rental_quota - customer.book_rented - len([rentbook for rentbook in customer.get_selected_list if isinstance(rentbook,BookOrder) and rentbook.book_info.activity_type == ActivityType.Rent])} เล่ม"
            )
        
        for item in selectitem_list:
            if isinstance(item,BookInfo):
                customer.select(item,num_days)
            elif isinstance(item,(TimeSlot,Purchase)):
                customer.select(item)
        respond = []

        for selected in customer.get_selected_list:
            if isinstance(selected,BookOrder):
                respond.append({
                    "Book Name" : selected.book_info.name,
                    "Book Series" : selected.book_info.book_stock.name,
                    "Book Author" : selected.book_info.author,
                    "Book Category" : selected.book_info.category.value,
                    "Book Price" : selected.book_info.price,
                    "Book Activity Type" : selected.book_info.activity_type.value,
                    "Book Available Date" : selected.book_info.available_date
                })
            elif isinstance(selected,TimeSlot):
                respond.append(f"{selected}")
        print("Select Successful")
        return {
            "Customer Selected List" : respond
        }
            
    def checkout(self,customer:Customer,staff:Staff,payment_method : PaymentOptions, promocode):
        if not isinstance(customer,Customer):
            return "Not a customer"
        
        if len(customer.get_selected_list) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No Order"
            )

        transaction = Transaction(customer,staff,payment_method,datetime.now(),datetime.now())
        transaction.make_order(customer)

        transaction.add_audit_log(f"Transaction requested : {datetime.now().strftime('%d/%m/%Y, %H:%M:%S')}") #need implement : เพิ่มรูปแบบของ audit log

        for promotion in self.__promotion_list:
            if promotion.is_eligible(customer,promocode):
                transaction.payment.promotion = promotion
                break

        if transaction.payment.promotion:
            transaction.payment.discount_amount = transaction.payment.promotion.apply_discount(transaction.get_sub_total(),customer,promocode)

        result = transaction.payment.payment_method.process_payment(transaction.get_net_amount()) #need implement : calculate payment ใน payment ไปเลย
        print(result)

        transaction.update_status(TransactionStatus.Confirm)
        transaction.add_audit_log(f"transaction completed : {datetime.now().strftime('%d/%m/%Y, %H:%M:%S')}")

        # ส่วนท้ายการทำงาน need implement : ถ้ารายการไหนต้อง update status ของสินค้ามาทำในส่วนนี้
        self.__transaction_list.append(transaction)

        self.notify_user(customer,f"{customer.name}: transaction confirm") #need implement : ต้องเปลี่ยนคำ

        if isinstance(customer,Member):
            customer.add_point()
            self.notify_user(customer,f"{customer.name}: add point successful")

        print("Checkout For Book Successful")
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


        for book_info_obj in stock.get_book_list(activity_type):
            if book_info_obj.name == book_name:
                book_info_obj.add_copies(number_of_copies)
                return "Add Copy Successful"
                    
        book_info_obj = BookInfo(book_stock,book_name,author,category,price,activity_type,available_date)
        book_info_obj.add_copies(number_of_copies)
        book_stock.add_book_info(book_info_obj,activity_type)
        return self.get_all_book

    def add_staff(self,name,surname,phonenumber,email,birth_month):
        if (not (self.validate_name_and_surname(name,surname) and self.validate_email(email) and self.validate_phonenumber(phonenumber))):
            raise ValueError()
        
        if (self.check_duplicate_account(phonenumber)):
            raise IndexError()
        
        if not isinstance(birth_month,BirthMonth):
            raise ValueError()
        
        self.__staff_list.append(Staff(name,surname,phonenumber,email,birth_month))
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

    @property
    def promotion_list(self):
        return self.__promotion_list

    def add_promotion(self,type : PromotionType,promocode,discount_rate):
        if isinstance(type,PromotionType):
            self.__promotion_list.append(Promotion(type,promocode,discount_rate))

        return self.__promotion_list

    def remove_promotion(self,promotion):
        if isinstance(promotion,Promotion):
            self.__promotion_list.remove(promotion)
    
    def add_area(self,type,hourly_rate,feature,capacity):
        area = Area(type,hourly_rate,feature,capacity)
        area.create_time_slot()
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
                notification = Notification(customer,message)
                customer.add_notify(notification)
                self.__notification_list.append(notification)

    def return_book(self,book_id : list[str]):

        result = []
        for id in book_id:
            type_item = self.check_type_from_id(id)
            if not type_item == ItemType.Book:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Need to return a book only"
                )
            
            activity_type,series,book_name,author = self.get_data_from_id(type_item,id)

            book = self.get_book_stock(series).get_book_info_by_name(book_name,author,activity_type).get_book(id)

            if not book:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Book Not Found | id : {id}"
                )
            
            if book.book_status != ItemStatus.InUse and book.book_status != ItemStatus.Confirm:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"This book is not in use"
                )
            
            book.change_status(ItemStatus.NotAvailable)

            result.append(id)
            
            self.__book_returned_list.append(book)

        book.customer.book_rented -= len(result)

        return {
            "Book Returned" : result
        }

    def process_return_book(self,no_staff,book_id : list[str]):
        if not isinstance(self.get_staff_by_no_staff(no_staff),Staff):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Need to be staff for process returned book"
            )
        
        result = []

        for id in book_id:
            type_item = self.check_type_from_id(id)
            if not type_item == ItemType.Book:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Need to return a book only"
                )
            
            activity_type,series,book_name,author = self.get_data_from_id(type_item,id)

            book = self.get_book_stock(series).get_book_info_by_name(book_name,author,activity_type).get_book(id)

            if not book:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Book Not Found | id : {id}"
                )
            
            if book not in self.book_returned_list:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Book not return yet"
                )
            
            result.append(id)
            book.customer = None
            book.change_status(ItemStatus.Available)

        return {
            "Book Process Successful" : result
        }
        
            


    def upgrade_booking_area(self, phonenumber: str, old_area_id: str, new_area_id: str, slot_ids: list[str]):
        
        #หา Customer
        customer = self.get_user_from_phone_number(phonenumber)
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer Not Found"
            )
            
        # หา Transaction ล่าสุดที่ใช้งานอยู่ (Active) เพื่อดึงของเก่า
        active_trans = None
        for trans in reversed(self.__transaction_list):
            # 
            if trans.customer == customer and trans.status == TransactionStatus.Confirm.value:
                active_trans = trans
                break
                
        if not active_trans:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="ไม่พบรายการจองที่กำลังใช้งานอยู่ (No active transaction)"
            )
            
        old_booking_obj = active_trans.get_current_booking_area(old_area_id)
        
        #ดึง Area ใหม่ และสล็อตเวลาใหม่
        target_area = next((a for a in self.__area if a.area_id == new_area_id), None)
        if not target_area:
            raise HTTPException(status_code=404, detail="ไม่พบพื้นที่ใหม่ที่ต้องการอัปเกรด")
            
        new_slots = target_area.get_slots_by_ids(slot_ids)
        if len(new_slots) != len(slot_ids):
            raise HTTPException(status_code=400, detail="สล็อตเวลาบางอันไม่ถูกต้อง")

        current_time = datetime.now().time()
        #current_time = datetime.strptime("13:00", "%H:%M").time()
        for slot in new_slots:
            if slot.is_available != ItemStatus.Available:
                raise HTTPException(status_code=400, detail=f"สล็อต {slot.slot_id} ไม่ว่างแล้ว")
            
            # แปลงสตริง
            slot_start_time = datetime.strptime(slot.start_time, "%H:%M").time()
            if slot_start_time <= current_time:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, 
                    detail=f"ไม่สามารถจองสล็อตที่เวลาผ่านไปแล้วได้ ({slot.start_time}-{slot.end_time})"
                )

        #เช็คโควต้าเฉพาะเวลาที่บวกเพิ่ม
        old_hours = len(old_booking_obj.get_order)
        new_hours = len(new_slots)
        
        if new_hours > old_hours:
            extra_hours = new_hours - old_hours
            if not customer.check_area_quota(extra_hours):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"โควต้าเวลาเต็ม! คุณบวกเวลาเพิ่มได้อีกแค่ {customer.get_area_quota() - customer.booking_reservation_time} ชม."
                )

        #สร้างใบอัปเกรด
        try:
            upgrade_item = UpgradeArea(old_booking_obj, new_slots)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
            
        customer.select(upgrade_item)
        
        print("Upgrade Area Added to Cart")
        return {
            "status": "Success",
            "message": f"นำการอัปเกรดไป {target_area.area_type.value} ใส่ตะกร้าแล้ว",
            "upgrade_fee": upgrade_item.upgrade_delta
        }

    def generate_utilization_report(self):
        pass        