from __future__ import annotations
import uuid
from datetime import datetime
from abc import ABC, abstractmethod

from models.orders import Order, RentBook, UpgradeArea, BookingArea
from models.infos import PromotionType, ItemStatus, PaymentOptions, TransactionStatus, PaymentStatus, ActivityType, AreaType
from models.books import BookOrder
from models.areas import TimeSlot
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.customers import Customer, Member, Staff

class Promotion:
    def __init__(self,type : PromotionType,promo_code,discount_rate):
        self.__type = type
        self.__promo_code = promo_code
        self.__discount_rate = discount_rate
        self.__status = ItemStatus.Available
        self.__used_user = []

    @property
    def type(self):
        return self.__type
        
    def is_eligible(self,customer,promocode):
        from models.customers import Customer
        if isinstance(customer,Customer):
            if self.type == PromotionType.BirthMonth:
                from models.customers import Member
                if not isinstance(customer,Member):
                    raise ValueError("This Promotion Need to be used by Member only")
            
            return (customer not in self.__used_user and promocode == self.__promo_code)
        
    def apply_discount(self,price,customer,promocode):
        if self.__status == ItemStatus.Available:
            if promocode == self.__promo_code:
                from models.customers import Customer
                if isinstance(customer,Customer):
                    if self.is_eligible(customer,promocode):
                        self.__used_user.append(customer)
                        return self.calculate_discount(price)
        raise ValueError("Promotion is not Available")

    def change_stauts(self,status : ItemStatus):
        self.__status = status
    
    def calculate_discount(self,price):
        return (price * self.__discount_rate / 100)
    
    def payment_unsuccess(self,customer):
        from models.customers import Customer
        if isinstance(customer,Customer):
            self.__used_user.remove(customer)

class Payment:
    def __init__(self,customer : "Customer",payment_method : PaymentOptions):
        self.__customer = customer
        self.__payment_no = f"PAY-{uuid.uuid4().hex[:8].upper()}"
        self.__status = PaymentStatus.Unpaid
        self.__order : Order = Order()
        self.__timestamp = datetime.now()
        self.__promotion : Promotion = None
    

        if payment_method == PaymentOptions.cash:
            self.__payment_method = Cash()
        elif payment_method == PaymentOptions.qr_code:
            self.__payment_method = QRCode(self.__customer.phonenumber)
        else:
            raise ValueError(f"Payment Options Not Found : {payment_method} {type(payment_method)}")
        
        self.__base_fee = 10 # เท่าไหร่อ่ะ need implement
        self.__upgrade_delta = 0
        self.__discount_amount = 0
        self.__penalty_fee = 0
        self.__net_amount = 0

    @property
    def payment_no(self):
        return self.__payment_no
    
    @property
    def status(self):
        return self.__status
    
    @property
    def order(self):
        return self.__order
    
    @property
    def timestamp(self):
        return self.__timestamp

    @property
    def promotion(self):
        return self.__promotion
    
    @promotion.setter
    def promotion(self,promotion : Promotion):
        self.__promotion = promotion

    @property
    def payment_method(self) -> PaymentMethod:
        return self.__payment_method
    
    @property
    def base_fee(self):
        return self.__base_fee
    
    @property
    def upgrade_delta(self):
        return self.__upgrade_delta
    
    @upgrade_delta.setter
    def upgrade_delta(self, amount):
        """รับยอดส่วนต่างจากการอัปเกรดเข้ามาเก็บไว้ เพื่อไปบวกใน calculate_net_amount()"""
        self.__upgrade_delta = amount
    
    @property
    def discount_amount(self):
        return self.__discount_amount
    
    @discount_amount.setter
    def discount_amount(self,amount):
        self.__discount_amount = amount
    
    @property
    def penalty_fee(self):
        return self.__penalty_fee
    
    @property
    def net_amount(self):
        return self.__net_amount
    
    def calculate_subtotal(self):
        subtotal = 0
        if self.__order.rent_book:
            subtotal += self.__order.rent_book.calculate_subtotal()
        if self.__order.purchase_book:
            subtotal += self.__order.purchase_book.calculate_subtotal()
        if len(self.__order.booking_area) > 0:
            subtotal += sum([bookingarea.calculate_subtotal() for bookingarea in self.__order.booking_area])

        return subtotal

    def calculate_net_amount(self):
        self.__net_amount = 0
        self.__net_amount += self.calculate_subtotal()
        self.__net_amount += self.__upgrade_delta - abs(self.__discount_amount) + self.__base_fee + self.__penalty_fee
        return self.__net_amount
    
    def update_payment_status(self,status:PaymentStatus):
        self.__status = status.value

        if status == PaymentStatus.Paid:
            self.__order.confirm()

    def add_penalty_fee(self,penalty_fee):
        self.__penalty_fee += penalty_fee

class Transaction:
    def __init__(self,customer: "Customer",staff: "Staff",payment_method : PaymentOptions,start_date_time : datetime = datetime.now(), end_date_time : datetime = datetime.now()):
        self.__customer = customer
        self.__staff = staff
        self.__start_date_time = start_date_time
        self.__end_date_time = end_date_time
        self.__status = TransactionStatus.Requested.value
        self.__payment = Payment(customer,payment_method)
        self.__audit_logs_list = []

    @property
    def customer(self):
        return self.__customer
    
    @property
    def staff(self):
        return self.__staff
    
    @property
    def start_date_time(self):
        return self.__start_date_time
    
    @property
    def end_date_time(self):
        return self.__end_date_time
    
    @property
    def status(self):
        return self.__status
    
    @property
    def payment(self):
        return self.__payment
    
    @property
    def audit_logs(self):
        return self.__audit_logs_list
    
    @property
    def order(self):
        return self.__payment.order
    
    def make_order(self,customer : "Customer"):
        selected_list : list[BookOrder, TimeSlot] = customer.get_selected_list
        rent_list = [order.book_info.search_book_available(customer).calculate_end_date(order.nums_date) for order in selected_list if isinstance(order,BookOrder) and order.book_info.activity_type == ActivityType.Rent]
        purchase_list = [order.book_info.search_book_available(customer) for order in selected_list if isinstance(order,BookOrder) and order.book_info.activity_type == ActivityType.Purchase]
        area_list = {}
        upgrade_list = [item for item in selected_list if isinstance(item, UpgradeArea)]
        booking_list = [order.book_info.search_book_incoming() for order in selected_list if isinstance(order, BookOrder) and order.book_info.activity_type == ActivityType.Booking]
        
        if len(booking_list) > 0:
            if hasattr(customer, 'book_booked'):
                customer.book_booked += len(booking_list)
            self.__payment.order.booking_book = booking_list

        current_time = datetime.now().time()
        # current_time = datetime.strptime("08:00", "%H:%M").time()
        
        for areatype in AreaType:
            area_in_type_list = []
            for item in selected_list:
                if isinstance(item,TimeSlot):
                    # แปลงเวลามาเช็ค
                    slot_start_time = datetime.strptime(item.start_time, "%H:%M").time()
                    if slot_start_time <= current_time:
                        raise ValueError(f"สล็อตเวลา {item.start_time}-{item.end_time} ผ่านไปแล้ว ไม่สามารถชำระเงินได้")
                        
                    if item.area.area_type == areatype:
                        area_in_type_list.append(item)
            
            if len(area_in_type_list) > 0:
                area_list[areatype] = area_in_type_list
        if len(rent_list) > 0:
            self.__customer.book_rented += len(rent_list) 
            self.__payment.order.rent_book = rent_list
        if len(purchase_list) > 0:
            self.__payment.order.purchase_book = purchase_list
        if len(area_list) > 0:
            self.__customer.booking_reservation_time += len([timeslot for timeslot in selected_list if isinstance(timeslot,TimeSlot)])
            self.__payment.order.booking_area = area_list

        if len(upgrade_list) > 0:
            for upg in upgrade_list:
                self.add_upgrade_order(upg)
        
        if not (len(rent_list) > 0 or len(purchase_list) > 0 or len(area_list) > 0 or len(upgrade_list) > 0 or len(booking_list) > 0):
            raise ValueError("activity type not found")
        
    
    def get_current_booking_area(self, old_area_id: str) -> BookingArea:
        for booking_area in self.__payment.order.booking_area:
            if booking_area.area.area_id == old_area_id:
                return booking_area
        raise ValueError(f"ไม่พบพื้นที่การจองเดิมรหัส {old_area_id} ใน Transaction นี้")
    
    def add_upgrade_order(self, upgrade_item: UpgradeArea):
        # ยัดใส่ตะกร้า
        self.__payment.order.add_upgrade_area(upgrade_item)
        
        #ส่งยอดส่วนต่างไปให้ Paymentเพื่อให้ calculate_net_amount()
        self.__payment.upgrade_delta = upgrade_item.upgrade_delta
    
    def get_sub_total(self):
        return self.__payment.calculate_subtotal()
        
    def get_net_amount(self):
        return self.__payment.calculate_net_amount()

    def update_status(self,status:TransactionStatus):
        self.__status = status

        if status == TransactionStatus.Confirm:
            self.__customer.add_transaction(self)
            self.__payment.update_payment_status(PaymentStatus.Paid)


    def add_audit_log(self,log):
        self.__audit_logs_list.append(log)

    def sync_payment_with_activity(self,rentbook : RentBook):
        return True
    
class Notification:
    count = 0
    def __init__(self,customer,message):
        self.__customer = customer
        self.__message = message
        self.__uid = f"NT-{customer.name}-{Notification.count}"

class PaymentMethod(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def process_payment(self):
        pass

class Cash(PaymentMethod):
    def __init__(self):
        self.__name = "Cash"

    @property
    def name(self):
        return self.__name

    def process_payment(self,Amount):
        return f"Process with Cash : {Amount}"

class QRCode(PaymentMethod):
    def __init__(self,phonenumber):
        self.__name = "QR Code"
        self.__phonenumber = phonenumber

    @property
    def name(self):
        return self.__name

    def process_payment(self,Amount):
        return f"Process with QRCode : {Amount} code QR-{self.__phonenumber}"
