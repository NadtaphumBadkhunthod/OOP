from datetime import datetime,timedelta

from core.system import System
from models.infos import AreaType, BirthMonth, TypeBook, ActivityType,PaymentOptions
from models.customers import Manager # เพิ่ม Manager และ Member

def mock_data():
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
    bibliohub.register(bibliohub.add_customer("ปลื้ม", "เรียนไหม", "0812345678", "pluem@gmail.com"),BirthMonth.May)
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

    # Add Manager
    manager_obj = Manager(bibliohub.add_customer("Sax_Manager", "Pongsathorn", "0999999999", "sax_boss@kmitl.ac.th"), BirthMonth.Jan, "BR-01")
    bibliohub.get_staff_list.append(manager_obj) 

    return bibliohub