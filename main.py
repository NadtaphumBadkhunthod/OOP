from __future__ import annotations
from fastmcp import FastMCP
from datetime import datetime

from models.infos import BirthMonth, PaymentOptions, ActivityType, PromotionType
from models.books import BookInfo, TypeBook
from models.customers import Manager
from datebase.init_data import mock_data

bibliohub = mock_data()

mcp = FastMCP()

@mcp.tool
def create_customer(name:str,surname:str,phonenumber:str,email:str):
    """
        สร้างบัญชีสำหรับลูกค้าใหม่
        name : ชื่อจริงลูกค้า
        surname : นามสกุลลูกค้า
        phonenumber : เบอร์โทรศัพท์ 10 ตัว
        email : อีเมลลูกค้า
    """
    return {
        "Result Customer" :  bibliohub.add_customer(name,surname,phonenumber,email)
    }

# @app.get("/create_staff",tags=["Main"])
@mcp.tool
def register(phonenumber:str,birth_month: BirthMonth):
    """
    การ สมัครสมาชิก หรือเป็นสมาชิก เกี่ยวกับ สมาชิก มีสมาชิกเริ่มต้นแบบเดียว
    ให้ข้อมูลเบอร์โทรและวันเกิดเพื่อสมัครสมาชิกเพื่อได้รับแต้ม
    """
    return {
        "Result register" : bibliohub.register(bibliohub.get_user_from_phone_number(phonenumber),birth_month)
    }
@mcp.tool
def create_staff(birth_month:BirthMonth,phonenumber:str,name:str = None,surname:str = None,email:str = None):
    """
        สร้างบัญชีพนักงานใหม่
        name : ชื่อจริงลูกค้า
        surname : นามสกุลลูกค้า
        phonenumber : เบอร์โทรศัพท์ 10 ตัว
        email : อีเมลลูกค้า
        birth_month : BirthMonth เดือนเกิดพนักงาน
    """
    customer = bibliohub.get_user_from_phone_number(phonenumber)
    if customer:
        bibliohub.add_staff(customer,birth_month)
        return "Become a staff"
    else:
        bibliohub.add_staff(bibliohub.add_customer(name,surname,phonenumber,email),birth_month)
        return "Create a customer and become a staff"

# @app.get("/create_promotion",tags=["Main"])
@mcp.tool
def create_promotion(type : PromotionType,promocode : str,discount_rate : float):
    """
        สร้างโปรโมชั่น สำหรับให้พนักงานสร้าง
        type : ประเภทโปรโมชั่น
        promocode : รหัสโปรโมชั่น
        discount_rate : ส่วนลดเป็น % เช่น ใส่ 10 ก็คือจะลด 10 เปอร์เซ็นต์
    """
    return  bibliohub.add_promotion(type,promocode,discount_rate)

# @app.get("/add_or_create_book",tags=["Book"])
@mcp.tool
def create_book(book_name:str,series:str,author:str,category:TypeBook,price:float,activity_type:ActivityType,number_of_copies:int,available_date : str):
    """
        สร้างหนังสือใหม่
        book_name = ชื่อหนังสือ (Naruto ภาค 10)
        series = ซีรีย์ของหนังสือ (Naruto)
        author = ชื่อผู้แต่งหรือ Unknown
        category = ประเภทของหนังสือ
        price = ราคา
        activity_type = ประเภท เช่น ซื้อ หรือ ให้เช่า
        number_of_copies = สร้างจำนวนกี่เล่ม
        available_date = วัน/เดือน/ปี dd/mm/yyyy (เช่น 01/02/2026)
    """
    return bibliohub.add_book(book_name,series,author,category,price,activity_type,number_of_copies,datetime.strptime(available_date, "%d/%m/%Y").date())

# @app.get("/all_area", tags=["Booking Area"])
@mcp.tool
def read_all_areas():
    """
        แสดงผลพื้นที่ทั้งหมด
    """
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

# @app.get("/area/search", tags=["Booking Area"])
@mcp.tool
def search_area(phonenumber: str, area_id : str):

    """
        ค้นหาพื้นที่เพื่อให้ดูว่ามี ช่วงเวลาไหนว่างบ้าง สำหรับแต่ละพื้นที่
    """
    
    customer = bibliohub.get_user_from_phone_number(phonenumber)
    if not customer:
        return {"error": "ไม่พบผู้ใช้ในระบบ"}
        
    try:
        available_slots = bibliohub.search_area(customer, area_id.value)
        return {"area_id": area_id, "available_slots": available_slots}
    except Exception as e:
        return {"error": str(e)}

# @app.get("/upgrade_area", tags=["Booking Area"])
@mcp.tool
def upgrade_booking_area(
    phonenumber: str,
    old_area_id: str,
    new_area_id: str,
    slot_ids: list[str]
):
    """
    API สำหรับส่งคำร้องขออัปเกรดที่นั่ง 
    ระบบจะทำการเช็คราคาและโควต้า หากผ่านจะนำใบเสนอราคาส่วนต่างใส่ตะกร้าให้โดยอัตโนมัติ
    จากนั้นให้ลูกค้าไปเรียก API /checkout ต่อไป
    """
    return bibliohub.upgrade_booking_area(phonenumber, old_area_id, new_area_id, slot_ids)

def format_book_info(book : BookInfo):
    is_booking = book.activity_type.value == "Booking"
    available_nums = book.get_nums_incoming() if is_booking and hasattr(book, 'get_nums_incoming') else book.get_nums_available()
    return {
        "Book Name": book.name,
        "Book ID": book.id,
        "Book Copies": book.copies,
        "Book Price" : book.price,
        "Book Available : " : book.get_nums_available(),
        "Book Incoming" : available_nums
    }

# @app.get("/get_all_book_series",tags=["Book"])
@mcp.tool
def get_all_book_series():
    """
        แสดงผลหนังสือทั้งหมด 
        แล้วตรวจสอบข้อมูลตามที่ลูกค้าต้องการ
    """
    respond = []

    for bookstock in bibliohub.get_all_book():
        respond.append({
            "Book Series" : bookstock.name,
            "Book For Sales" : [format_book_info(book_info) for book_info in bookstock.get_book_list(ActivityType.Purchase)],
            "Book For Rent": [format_book_info(book_info) for book_info in bookstock.get_book_list(ActivityType.Rent)],
            "Book For Booking": [format_book_info(book_info) for book_info in bookstock.get_book_list(ActivityType.Booking)] if hasattr(ActivityType, 'Booking') else []
        })
    
    return {
        "All Book Series" : respond
    }

# @app.get("/search_book_by_series",tags=["Book"])
@mcp.tool
def search_book_by_series(series : str):
    """
        หาหนังสือด้วย ซีรีย์ของหนังสือเล่มนั้น (เช่น Naruto มี 10 ภาค ในนี้ก็จะใส่มาเป็น Naruto)
    """
    result : tuple[list[BookInfo],list[BookInfo],list[BookInfo]] = bibliohub.get_book_stock(series).get_book_list(ActivityType.All)
    
    if not result:
        return "Series Not Found"
    
    
    book_for_rent, book_for_sales, book_for_booking = result

    return {
        "Book for rent": [{
            "name : ": book.name,
            "book id : ": book.id,
            "book available : ": book.get_nums_available()
        } for book in book_for_rent],
        
        "Book for sales": [{
            "name : ": book.name,
            "book id : ": book.id,
            "book available : ": book.get_nums_available()
        } for book in book_for_sales],
        
        "Book for booking": [{
            "name : ": book.name,
            "book id : ": book.id,
            # สำหรับ Booking เราจะใช้ get_nums_incoming เพื่อดูจำนวนหนังสือที่กำลังจะเข้า
            "book available : ": book.get_nums_incoming() if hasattr(book, 'get_nums_incoming') else 0
        } for book in book_for_booking]
    }

# @app.get("/select",tags=["Select"])
@mcp.tool
def select(phonenumber:str,item_id:list[str],num_days:int):
    """
        เลือกสินค้า ไม่ว่าจะหนังสือ หรือพื้นที่
        หากต้องการสินค้า 3 ชิ้น 
        ก็จะเป็น
        [A-B-C,A-B-C,A-B-C] รหัสที่ต้องการตามจำนวนชิ้น
    """
    return bibliohub.select(phonenumber,item_id,num_days)

@mcp.tool
def unselect(phonenumber:str,item_id:list[str]):
    """ยกเลิกการเลือกสินค้า"""
    return bibliohub.unselect(phonenumber,item_id)

# @app.get("/get_all_staff",tags=["Checkout"])
@mcp.tool
def get_all_staff():
    """แสดงข้อมูลของ staff ทั้งหมด"""
    return [staff.info() for staff in bibliohub.get_staff_list]

# @app.get("/checkout",tags=["Checkout"])
@mcp.tool
def checkout(phonenumber:str,no_staff:str,payment_method:PaymentOptions,promocode:str):
    """
        จ่ายเงิน หลังจากทำรายการอื่นๆ มาแล้ว
    """
    transaction = bibliohub.checkout(bibliohub.get_user_from_phone_number(phonenumber),bibliohub.get_staff_by_no_staff(no_staff),payment_method,promocode)

    if isinstance(transaction,list):
        return transaction

    return {
        "Transaction" : {
            "customer name" : transaction.customer.name,
            "staff name" : transaction.staff.name,
            "start date" : transaction.start_date_time,
            "end date" : transaction.end_date_time,
            "status" : transaction.status,
            "payment no" : transaction.payment.payment_no,
            "audit log" : transaction.audit_logs
        },
        "Payment" : {
            "payment no" : transaction.payment.payment_no,
            "status" : transaction.payment.status,
            "order" : transaction.payment.order.info,
            "timestamp" : transaction.payment.timestamp, 
            "payment method" : transaction.payment.payment_method.name, 
            "base fee" : transaction.payment.base_fee, 
            "upgrade delta" : transaction.payment.upgrade_delta,
            "discount amount" : transaction.payment.discount_amount,
            "penalty fee" : transaction.payment.penalty_fee,
            "net amount" : transaction.payment.net_amount
        }
    }

# @app.get("/get_transaction",tags=["Main"])
@mcp.tool
def get_transaction(phonenumber:str):
    """
        แสดงผลการทำรายการทั้งหมดของแต่ละคน
    """
    customer = bibliohub.get_user_from_phone_number(phonenumber)

    return [{
        "Transaction" : {
            "customer name" : transaction.customer.name,
            "staff name" : transaction.staff.name,
            "start date" : transaction.start_date_time,
            "end date" : transaction.end_date_time,
            "status" : transaction.status,
            "payment no" : transaction.payment.payment_no,
            "audit log" : transaction.audit_logs
        },
        "Payment" : {
            "payment no" : transaction.payment.payment_no,
            "status" : transaction.payment.status,
            "order" : transaction.payment.order.info,
            "timestamp" : transaction.payment.timestamp, 
            "payment method" : transaction.payment.payment_method.name, 
            "base fee" : transaction.payment.base_fee, 
            "upgrade delta" : transaction.payment.upgrade_delta,
            "discount amount" : transaction.payment.discount_amount,
            "penalty fee" : transaction.payment.penalty_fee,
            "net amount" : transaction.payment.net_amount
        }
    } for transaction in customer.get_all_transaction]

@mcp.tool
def get_manager_report(no_staff: str):
    """
    API สำหรับผู้จัดการ (Manager) เพื่อดึงรายงานสรุปผลการดำเนินงานของระบบ
    ระบบจะทำการตรวจสอบสิทธิ์ว่าพนักงานคนดังกล่าวเป็น Manager หรือไม่ก่อนแสดงผล
    """
    employee = bibliohub.get_staff_by_no_staff(no_staff)

    if not isinstance(employee, Manager):
        raise ValueError("สิทธิ์ไม่เพียงพอ: เฉพาะพนักงานระดับ Manager เท่านั้นที่สามารถเข้าถึงรายงานนี้ได้")
    
    report_data = employee.print_report(bibliohub)
    
    return {
        "status": "Success",
        "manager_info": {
            "name": f"{employee.name} {employee.surname}",
            "no_staff": employee.no_staff
        },
        "report": report_data
    }

@mcp.tool
def return_book(book_id:list[str]):
    """
        สำหรับให้ลูกค้าคืนหนังสือ
    """
    return bibliohub.return_book(book_id)

# @app.get("/process_book_return",tags=["For Staff"])
@mcp.tool
def process_return_book(no_staff : str,book_id : list[str]):
    """
        สำหรับให้ staff ตรวจสอบหนังสือ
    """
    return bibliohub.process_return_book(no_staff,book_id)

# @app.get("/system/check_upcoming_deadlines", tags=["Notification Scheduler"])
@mcp.tool
def check_upcoming_deadlines(
    current_datetime: str):

    """
        แสดงผลการแจ้งเตือนทั้งหมด ตามเวลาที่กำหนด  (รูปแบบ: dd/mm/yyyy HH:MM เช่น 10/03/2026 14:56)
    """

    try:
        dt_obj = datetime.strptime(current_datetime, "%d/%m/%Y %H:%M") if current_datetime else datetime.now()    
        sent_log = bibliohub.process_notifications(dt_obj)

        if not sent_log:
            return {
                "status": "success",
                "checked_at": dt_obj.strftime("%d/%m/%Y %H:%M"),
                "message": "ตอนนี้ไม่มีแจ้งเตือนสำหรับลูกค้า",
                "notifications_sent": []
            }
        return {
            "status": "success",
            "checked_at": dt_obj.strftime("%d/%m/%Y %H:%M"),
            "notifications_sent": sent_log
        }
    except ValueError:
        return {
            "status": "error",
            "message": "Format วันที่ผิด! กรุณาใช้ dd/mm/yyyy HH:MM"

        }

if __name__ == "__main__":
    # uvicorn.run("main:app", host="127.0.0.1", port=8000, log_level="info",reload=True)
    mcp.run()