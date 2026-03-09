from __future__ import annotations
from datetime import datetime

from fastmcp import FastMCP

from models.infos import BirthMonth, PaymentOptions, ActivityType, PromotionType
from models.books import BookInfo, TypeBook
from datebase.init_data import mock_data

bibliohub = mock_data()
mcp = FastMCP("Demo")

@mcp.tool
def create_customer(name:str ,surname:str ,phonenumber:str,email:str):
    """สร้าง object ของลูกค้าขึ้นมา"""
    return {
        "Result Customer" :  bibliohub.add_customer(name,surname,phonenumber,email)
    }

@mcp.tool
def create_staff(name:str,surname:str,phonenumber:str,email:str,birth_month:BirthMonth):
    """สร้าง object ของ staff ขึ้นมา"""
    return {
        "Result Staff" : bibliohub.add_staff(name,surname,phonenumber,email,birth_month)
    }

@mcp.tool
def create_promotion(type : PromotionType,promocode : str,discount_rate : float):
    """สร้าง promotion ขึ้นมา"""
    return  bibliohub.add_promotion(type,promocode,discount_rate)

@mcp.tool
def create_book(book_name:str,series:str,author:str,category:TypeBook,price:float,activity_type:ActivityType,number_of_copies:int,available_date):
    """สร้างหนังสือ (รูปแบบของวันที่ใส่เป็น dd/mm/yyyy เช่น 01/02/2026)"""
    return bibliohub.add_book(book_name,series,author,category,price,activity_type,number_of_copies,datetime.strptime(available_date, "%d/%m/%Y").date())

@mcp.tool
def read_all_areas():
    """แสดงข้อมูลพื้นที่ทั้งหมด"""
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

@mcp.tool
def search_area(phonenumber: str, area_id : str):
    """ค้นหาพื้นที่ในการเช่า ว่ามีช่วงเวลาไหนว่างบ้าง"""
    
    customer = bibliohub.get_user_from_phone_number(phonenumber)
    if not customer:
        return {"error": "ไม่พบผู้ใช้ในระบบ"}
        
    try:
        available_slots = bibliohub.search_area(customer, area_id)
        return {"area_id": area_id, "available_slots": available_slots}
    except Exception as e:
        return {"error": str(e)}

@app.get("/upgrade_area", tags=["Booking Area"])
def upgrade_booking_area(
    phonenumber: str = Query(..., description="เบอร์โทรศัพท์ลูกค้า"),
    old_area_id: str = Query(..., description="ID ของพื้นที่เดิมที่กำลังนั่งอยู่ (เช่น AREA-QUIET-1)"),
    new_area_id: str = Query(..., description="ID ของพื้นที่ใหม่ที่ต้องการย้ายไป (เช่น AREA-PRIVATE-2)"),
    slot_ids: list[str] = Query(default=["XX-XX-XX"], description="ID ของสล็อตเวลาใหม่ที่ต้องการ ขั้นด้วย , (เช่น AREA-PRIVATE-2-1)")
):
    """
    API สำหรับส่งคำร้องขออัปเกรดที่นั่ง 
    ระบบจะทำการเช็คราคาและโควต้า หากผ่านจะนำใบเสนอราคาส่วนต่างใส่ตะกร้าให้โดยอัตโนมัติ
    จากนั้นให้ลูกค้าไปเรียก API /checkout ต่อไป
    """
    return bibliohub.upgrade_booking_area(phonenumber, old_area_id, new_area_id, slot_ids)

def format_book_info(book : BookInfo):
    return {
        "Book Name": book.name,
        "Book ID": book.id,
        "Book Copies": book.copies,
        "book available : " : book.get_nums_available()
    }

@mcp.tool
def get_all_book_series():
    """แสดงหนังสือทั้งหมด"""
    respond = []

    for bookstock in bibliohub.get_all_book():
        respond.append({
            "Book Series" : bookstock.name,
            "Book For Sales" : [format_book_info(book_info) for book_info in bookstock.get_book_list(ActivityType.Purchase)],
            "Book For Rent": [format_book_info(book_info) for book_info in bookstock.get_book_list(ActivityType.Rent)]
        })
    
    return {
        "All Book Series" : respond
    }

@mcp.tool
def search_book_by_series(series : str):
    """หาหนังสือด้วย ซีรีย์ของหนังสือเล่มนั้น (เช่น Naruto มี 10 ภาค ในนี้ก็จะใส่มาเป็น Naruto)"""
    result : tuple[list[BookInfo],list[BookInfo]] = bibliohub.get_book_stock(series).get_book_list(ActivityType.All)
    
    if not result:
        return "Series Not Found"
    
    book_for_rent, book_for_sales = result

    return {
        "Book for rent" : [{
            "name : " : book.name,
            "book id : " : book.id,
            "book available : " : book.get_nums_available()
        } for book in book_for_rent],
        "Book for sales" : [{
            "name : " : book.name,
            "book id : " : book.id,
            "book available : " : book.get_nums_available()
        } for book in book_for_sales]
    }

@mcp.tool
def select(phonenumber:str,item_id:list[str],num_days:int = 0):
    """เลือกหนังสือหรือพื้นที่ไปเก็บไว้ใน object ของลูกค้า เพื่อนำไปจ่ายเงินต่อไป"""
    return bibliohub.select(phonenumber,item_id,num_days)

@mcp.tool
def get_all_staff():
    """แสดงข้อมูล staff ทั้งหมด แสดงเฉพาะ staff_id และข้อมูลที่ไม่ใช่ private"""
    return [staff.info() for staff in bibliohub.get_staff_list]

@mcp.tool
def checkout(phonenumber:str,no_staff:str,payment_method:PaymentOptions,promocode:str = "xxxxxx"):
    """จ่ายเงิน"""
    transaction = bibliohub.checkout(bibliohub.get_user_from_phone_number(phonenumber),bibliohub.get_staff_by_no_staff(no_staff),payment_method,promocode)

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

@mcp.tool
def get_transaction(phonenumber:str):
    """แสดงผล การทำรายการทั้งหมดของลูกค้าคนใดคนหนึ่ง"""
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
def return_book(book_id:list[str]):
    """การคืนหนังสือที่เช่ามา"""
    return bibliohub.return_book(book_id)

@mcp.tool
def process_return_book(no_staff : str,book_id : list[str]):
    """การยืนยันหนังสือที่ลูกค้าคืนโดย staff หากหนังสือที่ลูกค้าคืนมาปกติดีจะทำให้หนังสือนั้นกลับไปเช่าได้ปกติ"""
    return bibliohub.process_return_book(no_staff,book_id)

if __name__ == "__main__":
    mcp.run()