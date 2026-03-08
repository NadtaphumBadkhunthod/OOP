from __future__ import annotations
from models.infos import ItemStatus, TypeBook, ActivityType
from datetime import date, datetime, timedelta
from fastapi import HTTPException, status

# Core Class

class Book:
    def __init__(self,book_info:BookInfo,status:ItemStatus):
        """
        class Book คือหนังสือที่แยกตาม UID คือหนังสือแต่ละเล่มแยกกันไป เช่น โดเรม่อน เล่มที่ x อันที่ x 
        
        :param book_info: object ที่มีข้อมูลของหนังสือ
        :type book_info: BookInfo
        :param status: สถานะของหนังสือเล่มนั้น
        :type status: ItemStatus
        """
        self.__book_info = book_info
        self.__book_uid = None
        self.__book_status = status
        self.__start_date : datetime = None 
        self.__end_date : datetime = None
        self.__actual_return_date : datetime = None
    
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
    def book_status(self) -> ItemStatus:
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

    @property
    def end_date(self):
        return self.__end_date
    
    def calculate_end_date(self,num_days):
        self.__start_date = datetime.now()
        self.__end_date = self.__start_date + timedelta(days=num_days)
        return self

    def check_available(self):
        return self.__book_status == ItemStatus.Available.value
    
    def change_status(self,status:ItemStatus):
        self.__book_status = status

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
        self.__id = f"BK-{activity_type.value}-{book_stock.name.replace(' ','_')}-{name.replace(' ','_')}-{author}"
    
    @property
    def name(self):
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
    def book_list(self):
        return self.__book
        
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
            status = ItemStatus.Available
        else:
            status = ItemStatus.Incoming
        
        for _ in range(copies):
            book = Book(self,status)
            book.uid = f"{self.__id}-{len(self.__book)}"
            self.__book.append(book)

    def get_nums_available(self):
        count = 0
        for book in self.__book:
            if book.check_available():
                count += 1

        return count

    def search_book_available(self):
        for book in self.__book:
            if book.check_available():
                book.change_status(ItemStatus.InProcess)
                return book
            
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"หนังสือ {self.name} มีจำนวนไม่พอ"
        )
    
class BookOrder:
    def __init__(self,book_info : BookInfo,nums_date):
        self.__book_info : BookInfo = book_info
        self.__nums_date = nums_date

    @property
    def book_info(self):
        return self.__book_info
    
    @property
    def nums_date(self):
        return self.__nums_date

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
        elif activity_type.value == "All":
            return self.__rent_book_list, self.__forsale_book_list
        else:
            raise TypeError("Wrong Activity Type")

    def get_book_info_by_name(self,bookname : str,author : str,activity_type : ActivityType):
        for book_info in self.get_book_list(activity_type):
            if book_info.name == bookname and book_info.author == author:
                return book_info
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book name or Author Not Found"
        )

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
            if book.activity_type == "Rent":
                self.__rent_book_list.remove(book)
            elif book.activity_type == "Purchase":
                self.__forsale_book_list.remove(book)
            else:
                raise TypeError("Activity type error")
        else:
            raise TypeError("Need to be a book")
        
    def get_book_available(self,bookname,activity_type):
        if activity_type == "Rent":
            target_list = self.__rent_book_list
        elif activity_type == "Purchase":
            target_list = self.__forsale_book_list
        else:
            raise TypeError("Activity type error")

        for book_name_object in target_list:
            if book_name_object.name == bookname:
                return book_name_object.search_book_available()
                
        return None
        