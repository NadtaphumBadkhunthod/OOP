from __future__ import annotations
from fastapi import FastAPI, Query
from fastapi.responses import RedirectResponse
from datetime import datetime, date
import uvicorn

from models.infos import BirthMonth, PaymentOptions, ActivityType, PromotionType
from models.books import BookInfo, TypeBook
from datebase.init_data import mock_data

bibliohub, AreaOption = mock_data()

app = FastAPI()

@app.get("/")
def redirect_to_docs():
    return RedirectResponse(url="/docs")

@app.get("/create_customer",tags=["Main"])
def create_customer(name:str = Query(description="ชื่อจริงลูกค้า"),surname:str = Query(description="นามสกุลลูกค้า"),phonenumber:str = Query(description="เบอร์โทรศัพทธ์ลูกค้า"),email:str = Query(description="อีเมลลูกค้า")):
    return {
        "Result Customer" :  bibliohub.add_customer(name,surname,phonenumber,email)
    }

@app.get("/create_staff",tags=["Main"])
def create_staff(name:str = Query(description="ชื่อจริงพนักงาน"),surname:str = Query(description="นามสกุลพนักงาน"),phonenumber:str = Query(description="เบอร์โทรศัพทธ์พนักงาน"),email:str = Query(description="อีเมลพนักงาน"),birth_month:BirthMonth = Query(description="เดือนเกิดพนักงาน")):
    return {
        "Result Staff" : bibliohub.add_staff(name,surname,phonenumber,email,birth_month)
    }

@app.get("/create_promotion",tags=["Main"])
def create_promotion(type : PromotionType,promocode : str,discount_rate : float):
    return  bibliohub.add_promotion(type,promocode,discount_rate)

@app.get("/add_or_create_book",tags=["Book"])
def create_book(book_name:str,series:str,author:str,category:TypeBook,price:float,activity_type:ActivityType,number_of_copies:int,available_date = Query(default=date.today().strftime("%d/%m/%Y"),description="วัน/เดือน/ปี (เช่น 01/02/2026)")):
    return bibliohub.add_book(book_name,series,author,category,price,activity_type,number_of_copies,datetime.strptime(available_date, "%d/%m/%Y").date())

@app.get("/all_area", tags=["Booking Area"])
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

def format_book_info(book : BookInfo):
    return {
        "Book Name": book.name,
        "Book ID": book.id,
        "Book Copies": book.copies,
        "book available : " : book.get_nums_available()
    }

@app.get("/get_all_book_series",tags=["Book"])
def get_all_book_series():
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

@app.get("/search_book_by_series",tags=["Book"])
def search_book_by_series(series : str):
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

@app.get("/select",tags=["Select"])
def select(phonenumber:str,item_id:list[str] = Query(default=["XX-XX-XX"],description="id ของสินค้าที่ต้องการเลือก ขั้นด้วย , เช่น BK-xx-xx, BK-yy-yy, BK-zz-zz หรือทำทีละ id"),num_days:int = Query(default=1,description="จำนวนวันที่ต้องการ")):
    return bibliohub.select(phonenumber,item_id,num_days)

@app.get("/get_all_staff",tags=["Checkout"])
def get_all_staff():
    return bibliohub.get_staff_list

@app.get("/checkout",tags=["Checkout"])
def checkout(phonenumber:str,no_staff:str = Query(description="รหัสพนักงาน"),payment_method:PaymentOptions = Query(description="วิธีการชำระเงิน"),promocode:str = Query(default="xxxxxx",description="รหัสโปรโมชั่น")):
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

@app.get("/get_transaction",tags=["Main"])
def get_transaction(phonenumber:str):
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

@app.get("/return_book",tags=["Book"])
def return_book(phonenumber:str,book_id:list[str] = Query(default=["XX-XX-XX"],description="id ของสินค้าที่ต้องการเลือก ขั้นด้วย , เช่น BK-xx-xx, BK-yy-yy, BK-zz-zz หรือทำทีละ id")):
    return bibliohub.return_book(phonenumber,book_id)

@app.get("/process_book_return",tags=["For Staff"])
def process_return_book(no_staff : str,book_id : list[str]):
    return bibliohub.process_return_book(no_staff,book_id)

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, log_level="info",reload=True)