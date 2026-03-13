# 📚 BiblioHub Management System

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![OOP](https://img.shields.io/badge/Architecture-OOP-success.svg)
![FastAPI](https://img.shields.io/badge/API-FastAPI-009688.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

**BiblioHub Management System** คือระบบจัดการห้องสมุดและพื้นที่ Co-working Space แบบครบวงจร พัฒนาด้วยภาษา Python โดยยึดหลักการออกแบบเชิงวัตถุ (Object-Oriented Programming: OOP) อย่างเคร่งครัด ระบบรองรับการทำธุรกรรมที่หลากหลาย เช่น การเช่า/ซื้อหนังสือ การจองพื้นที่ทำงาน และระบบสมาชิก พร้อมทั้งมี API/Service สำหรับเชื่อมต่อการทำงาน

---

## ✨ Features (ความสามารถหลักของระบบ)

- 👥 **Multi-Role Management**: ระบบจำแนกสิทธิ์ผู้ใช้งาน 4 ระดับ ได้แก่ Customer, Member, Staff และ Manager
- 📖 **Book & Resource Management**: ค้นหา เช่า ซื้อ และจองหนังสือล่วงหน้า พร้อมระบบจัดการคลัง (BookStock) ที่มีประสิทธิภาพ
- 🛋️ **Area & TimeSlot Booking**: ค้นหาและจองพื้นที่นั่งอ่านหนังสือ/ทำงาน พร้อมรองรับฟังก์ชันการอัปเกรดพื้นที่ (Upgrade Area) ระหว่างการใช้งาน
- 💳 **Centralized Checkout**: ระบบตะกร้าสินค้าส่วนกลาง รองรับการชำระเงิน การคำนวณส่วนลด (Promotion) และคิดค่าปรับ (Penalty) อัตโนมัติ
- 🔔 **Smart Notification**: ระบบแจ้งเตือนผู้ใช้งานเมื่อใกล้หมดเวลาจองพื้นที่ หรือใกล้ถึงกำหนดคืนหนังสือ
- 📊 **Business Reports**: ระบบสรุปรายงานสถิติการใช้งานและรายได้ สำหรับผู้จัดการ (Manager)

---

## 🏗️ System Architecture & OOP Principles

โปรเจกต์นี้ถูกออกแบบมาเพื่อแสดงให้เห็นถึงโครงสร้างสถาปัตยกรรมซอฟต์แวร์ที่แข็งแรง:
- **Encapsulation**: ควบคุมการเข้าถึงข้อมูลด้วย Private Attributes และจัดทำ Property/Getter/Setter เท่าที่จำเป็น
- **Inheritance**: มีการสืบทอดคลาสมากกว่า 2 ลำดับชั้น เช่น สายผู้ใช้งาน (`Customer` -> `Member` -> `Staff` -> `Manager`) และสายธุรกรรม (`Purchase` -> `RentBook`, `BookingArea` ฯลฯ)
- **Polymorphism**: รองรับรูปแบบการชำระเงินที่หลากหลายผ่าน Abstract Class `PaymentMethod` (เช่น `QRCode`, `Cash`)
- **Error Handling**: มีระบบตรวจสอบความถูกต้องของข้อมูล (Input Validation) และป้องกันข้อผิดพลาดผ่าน `try-except` ในทุกจุดสำคัญ

---
## 📂 Project Structure (โครงสร้างไฟล์)

```text
📦 BiblioHub-Management-System
 ┣ 📂 models           # เก็บ Class ต่างๆ (Customer, Book, Area, Transaction)
 ┣ 📂 services         # เก็บ MCP Tools และ API Endpoints
 ┣ 📜 system.py        # Controller Class (BiblioHubSystem) ควบคุมลอจิกหลัก
 ┣ 📜 main.py          # ไฟล์หลักสำหรับรันโปรแกรม
 ┣ 📜 requirements.txt # รายชื่อไลบรารีที่ต้องใช้
 ┗ 📜 README.md        # เอกสารแนะนำโปรเจกต์
---

## 🚀 Getting Started (การติดตั้งและใช้งาน)

### Prerequisites (สิ่งที่ต้องมี)
- Python 3.10 ขึ้นไป
- พิมพ์คำสั่งติดตั้งไลบรารีที่จำเป็น (หากมี)
```bash
pip install -r requirements.txt
