from __future__ import annotations
from enum import Enum
from datetime import datetime,timedelta

from core.system import System
from models.infos import AreaType, BirthMonth, TypeBook, ActivityType,PaymentOptions
from models.customers import Staff, Manager, Member # เพิ่ม Manager และ Member

def mock_data():
    Staff.count = 0
    bibliohub = System()
    future_date = datetime.today().date() + timedelta(days=5)

    # 1. เพิ่มหนังสือซีรีส์ใหม่สำหรับจองโดยเฉพาะ
    bibliohub.add_book(
        "Advanced Python Design Patterns", 
        "Python Masterclass", 
        "Guido van Rossum", 
        TypeBook.Education, 
        550.0, 
        ActivityType.Booking, 
        3, 
        future_date
    )

    # 2. เพิ่มหนังสือในซีรีส์เดิม (How to learn OOP) แต่เป็นเวอร์ชันสำหรับจอง
    bibliohub.add_book(
        "How to learn OOP: Special Edition", 
        "How to learn OOP", 
        "Sixsax", 
        TypeBook.Education, 
        250.0, 
        ActivityType.Booking, 
        5, 
        future_date
    )
    bibliohub.add_area(AreaType.meeting_room,150.0,["Projector", "Whiteboard"], 4)
    bibliohub.add_area(AreaType.quiet_area, 50.0, ["Desk Lamp", "Power Outlet"], 1)
    area_names = {area.area_id.replace("-", "_").lower(): area.area_id for area in bibliohub.list_area}
    bibliohub.register("ปลื้ม", "เรียนไหม", "0812345678", "pluem@gmail.com", BirthMonth.Jun)
    bibliohub.add_staff("Pluemepime","PimePluem","0000000000","68010366@kmitl.ac.th",BirthMonth.Jan)
    bibliohub.add_customer("Sixsax","Saxsix","1111111111","68010366@kmitl.ac.th")

    # Create_Book
    bibliohub.add_book("How to learn OOP","How to learn OOP","Sixsax",TypeBook.Education,12,ActivityType.Rent,1,datetime.today().date())
    bibliohub.add_book("How to learn OOP 2","How to learn OOP","Sixsax",TypeBook.Education,12,ActivityType.Rent,2,datetime.today().date())
    bibliohub.add_book("How to learn OOP 2","How to learn OOP","Sixsax",TypeBook.Education,12,ActivityType.Purchase,2,datetime.today().date())
    bibliohub.add_book("IDK","IDK","Sixsax",TypeBook.Historical,10,ActivityType.Rent,1,datetime.today().date())
    bibliohub.add_book("IDK 2","IDK","Sixsax",TypeBook.Historical,10,ActivityType.Rent,5,datetime.today().date())

    # Add Copies
    bibliohub.add_book("IDK 2","IDK","Sixsax",TypeBook.Historical,10,ActivityType.Rent,5,datetime.today().date())
    bibliohub.add_book("IDK 2","IDK","Sixsax",TypeBook.Historical,10,ActivityType.Purchase,10,datetime.today().date())

    Staff.count += 1

    # Add Manager
    manager_obj = Manager("Sax_Manager", "Pongsathorn", "0999999999", "sax_boss@kmitl.ac.th", BirthMonth.Jan, "BR-01")
    bibliohub.get_staff_list.append(manager_obj) 

    cust = bibliohub.get_user_from_phone_number("0812345678")
    stf = bibliohub.get_staff_by_no_staff("STF-0")

    if cust and stf:
        bibliohub.select("0812345678", ["BK-Rent-How_to_learn_OOP-How_to_learn_OOP-Sixsax"])
        bibliohub.checkout(cust, stf, PaymentOptions.cash, "NONE")

        bibliohub.select("0812345678", ["BK-Purchase-How_to_learn_OOP-How_to_learn_OOP_2-Sixsax"])
        bibliohub.checkout(cust, stf, PaymentOptions.qr_code, "NONE")

        # utilization_percent = slot ที่ถูกจอง / slot ที่มีอยู่ * 100
        if bibliohub.list_area:
            first_area = bibliohub.list_area[0]
            if first_area.area__slots:
                bibliohub.select("0812345678", [first_area.area__slots[0].slot_id])
                bibliohub.checkout(cust, stf, PaymentOptions.cash, "NONE")

    gold_member = bibliohub.register("สมชาย", "สายเปย์", "0844444444", "gold@gmail.com", BirthMonth.Aug)
    if isinstance(gold_member, Member):
        for _ in range(35): gold_member.add_point()

    
    AreaOption = Enum('AreaOption', area_names, type=str)

    return bibliohub, AreaOption