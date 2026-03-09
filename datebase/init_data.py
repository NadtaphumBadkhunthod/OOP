from datetime import datetime

from core.system import System
from models.infos import AreaType, BirthMonth, TypeBook, ActivityType

def mock_data():
    bibliohub = System()

    bibliohub.add_area(AreaType.meeting_room,150.0,["Projector", "Whiteboard"], 4)
    bibliohub.add_area(AreaType.quiet_area, 50.0, ["Desk Lamp", "Power Outlet"], 1)
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

    return bibliohub