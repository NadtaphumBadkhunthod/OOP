from enum import Enum

# Enum Class
class CustomerStatus(str, Enum):
    Expired = "Expired"
    Good = "Good"

class ItemType(str, Enum):
    Book = "Book"
    Area = "Area"

class BookingBookQuota(int, Enum):
    Silver = 6
    Gold = 8
    Platinum = 10

class LevelMember(str, Enum):
    Silver = "Silver"
    Gold = "Gold"
    Platinum = "Platinum"

class BirthMonth(str, Enum):
    Jan = "01"
    Feb = "02"
    Mar = "03"
    Apr = "04"
    May = "05"
    Jun = "06"
    Jul = "07"
    Aug = "08"
    Sep = "09"
    Oct = "10"
    Nov = "11"
    Dec = "12"

class PaymentOptions(str,Enum):
    cash = "cash"
    qr_code = "qrcode"

class ActivityType(str, Enum):
    Rent = "Rent"
    Purchase = "Purchase"
    All = "All"

class TypeBook(str,Enum):
    Manga = "Manga"
    Novel = "Novel"
    Historical = "Historical"
    Education = "Education"
    Self_improvement = "Self Improvement"
    Economic = "Economic"

class ItemStatus(str,Enum):
    Available = "Available"
    NotAvailable = "NotAvailable"
    InProcess = "InProcess"
    Purchased = "Purchased"
    Incoming = "Incoming"
    InUse = "InUse"

class PaymentStatus(str,Enum):
    Unpaid = "Unpaid"
    Paid = "Paid"
    Voied = "Voied"

class TransactionStatus(str,Enum):
    Requested = "Requested"
    Confirm = "Confirm"
    Completed = "Completed"
    Cancelled = "Cancelled"

class AreaType(str,Enum):
    quiet_area = "Quiet_Area"
    private_room = "Private_Room" 
    meeting_room = "Meeting_Room"

class PromotionType(str ,Enum):
    DoubleDate = "DoubleDate"
    BirthMonth = "BirthMonth"