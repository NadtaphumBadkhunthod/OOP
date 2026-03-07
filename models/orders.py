from models.books import Book
from models.areas import Area, TimeSlot
from models.infos import ActivityType, AreaType, ItemStatus

class Order:
    def __init__(self):
        self.__rent_book : RentBook = None
        self.__purchase_book : Purchase = None
        self.__booking_area : list[BookingArea] = []

    @property
    def info(self):
        def format_book(book : Book):
            result = {
                "Book Name" : book.book_info.name,
                "Book Series" : book.book_info.book_stock.name,
                "Book Author" : book.book_info.author,
                "Book Category" : book.book_info.category.value,
                "Book Price" : book.book_info.price,
                "Book Activity Type" : book.book_info.activity_type.value,
                "Book Available Date" : book.book_info.available_date,
                "Book Status" : book.book_status,
                "Book UID" : book.uid
            }

            if book.book_info.activity_type == ActivityType.Rent:
                result["Start Date"] = book.start_date
                result["End Date"] = book.end_date
            return result
        order_info = []
        if self.__rent_book:
            order_info.extend([format_book(rent_book) for rent_book in self.__rent_book.get_order])
        if self.__purchase_book:
            order_info.extend([format_book(purchase_book) for purchase_book in self.__purchase_book.get_order])
        if self.__booking_area:
            order_info.extend([{
                "Area" : f"{booking_area.area}",
                "Area Order" : [f"{order}" for order in booking_area.get_order]
            } for booking_area in self.__booking_area])
        return {"Order Info" : order_info}

    @property
    def rent_book(self):
        return self.__rent_book
    
    @rent_book.setter
    def rent_book(self,book_list : list[Book]):
        self.__rent_book = RentBook(book_list)

    @property
    def purchase_book(self):
        return self.__purchase_book
    
    @purchase_book.setter
    def purchase_book(self,book_list : list[Book]):
        self.__purchase_book = Purchase(book_list)

    @property
    def booking_area(self):
        return self.__booking_area
    
    @booking_area.setter
    def booking_area(self,timeslot_list : dict[AreaType, list[TimeSlot]]):
        for bookingarea in self.__booking_area:
            if timeslot_list.get(bookingarea.area.area_type):
                bookingarea.add_timeslot(timeslot_list[bookingarea.area.area_type])
                return
        for areatype in AreaType:
            if timeslot_list.get(areatype):
                self.__booking_area.append(BookingArea(timeslot_list[areatype]))


    def calculate_subtotal(self):
        return self.__purchase_book.calculate_subtotal() + self.__rent_book.calculate_subtotal()
    
    def confirm(self):
        if self.__purchase_book:
            self.__purchase_book.confirm()
        if self.__rent_book:
            self.__rent_book.confirm()
        if len(self.__booking_area) > 0:
            for bookingarea in self.__booking_area:
                bookingarea.confirm()

class Purchase:
    def __init__(self,order : list[Book | TimeSlot]):
        self._order : list[Book | TimeSlot] = order

    @property
    def get_order(self) -> list[Book | TimeSlot]:
        return self._order

    def calculate_subtotal(self):
        return sum((item.book_info.price if isinstance(item, Book) else item.price) for item in self._order)   
    
    def confirm(self):
        for item in self._order:
            item.change_status(ItemStatus.Purchased)

class RentBook(Purchase):
    def __init__(self,order : list[Book | TimeSlot]):
        super().__init__(order)
        self.__late_penalty_rate = 10

    def get_penalty(self):
        penalty = 0

        for item in self._order:
            penalty += (item.actual_return_date - item.end_date).days * self.__late_penalty_rate
        return penalty
    
    def confirm(self):
        for item in self._order:
            item.change_status(ItemStatus.Confirm)
    
class BookingArea(Purchase):
    def __init__(self, order : list[Book | TimeSlot]):
        super().__init__(order)
        self.__area : Area = order[0].area if order else None
    
    @property
    def area(self):
        return self.__area
    
    def add_timeslot(self, list_timeslot : list[TimeSlot]):
        if isinstance(list_timeslot,list[TimeSlot]):
            self._order.extend(list_timeslot)
        
    def calculate_subtotal(self):
        return len(self.get_order) * self.__area.hourly_rate

    def calculate_upgrade_delta(self, new_hourly_rate):
        old_price = self.calculate_subtotal()
        new_price = len(self.__order) * new_hourly_rate
        delta = new_price - old_price
        return delta

    def update_order(self, new_slots, new_area):
        self.__order = new_slots
        self.__area = new_area

    def confirm(self):
        for item in self._order:
            item.change_status(ItemStatus.NotAvailable)
