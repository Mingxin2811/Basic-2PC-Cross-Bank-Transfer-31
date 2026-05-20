# Distributed Database Project - Basic 2PC Cross-Bank Transfer

## 1. Project Information

**Project ID:** #31  
**Category:** Category 4 - Reliability and Commit Protocols  
**Project Title:** Basic 2-Phase Commit (2PC) - Cross-Bank Transfer  
**Team Name:** Mingxin  
**Team Member:** Nguyễn Minh Tâm  

---

## 2. Project Description

Project này mô phỏng một giao dịch chuyển khoản liên ngân hàng sử dụng giao thức **Two-Phase Commit (2PC)** trong hệ cơ sở dữ liệu phân tán.

Hệ thống gồm 3 node chính:

- **Coordinator**
- **Bank A Service**
- **Bank B Service**

Mục tiêu chính của project là chứng minh cách giao thức **2PC** đảm bảo tính nhất quán dữ liệu trong distributed transaction, đặc biệt trong trường hợp **Coordinator bị crash sau PREPARE phase nhưng trước COMMIT phase**.

Project tập trung vào các nội dung chính:

- Mô phỏng distributed transaction giữa 2 ngân hàng.
- Triển khai giao thức **Two-Phase Commit**.
- Ghi lại trạng thái transaction bằng **transaction log**.
- Mô phỏng lỗi **Coordinator crash**.
- Thực hiện **recovery** sau khi Coordinator reboot.

---

## 3. System Architecture

```text
Client
  |
  v
Coordinator Service - Port 5000
  |
  |---- PREPARE / COMMIT ----> Bank A Service - Port 5001
  |
  |---- PREPARE / COMMIT ----> Bank B Service - Port 5002
```

### Vai trò của từng node

| Node | Vai trò |
|---|---|
| Coordinator | Điều phối transaction, gửi PREPARE/COMMIT, ghi log và thực hiện recovery |
| Bank A Service | Participant node đại diện ngân hàng gửi tiền |
| Bank B Service | Participant node đại diện ngân hàng nhận tiền |

Trong project này, **Coordinator không truy cập trực tiếp database của Bank A hoặc Bank B**.  
Coordinator chỉ giao tiếp với các bank thông qua **REST API**, đúng với ý tưởng của hệ thống phân tán.

---

## 4. Technologies Used

Project sử dụng các công nghệ sau:

| Technology | Purpose |
|---|---|
| Python | Ngôn ngữ lập trình chính |
| Flask | Xây dựng REST API cho các node |
| SQLite | Lưu trữ dữ liệu tài khoản ngân hàng |
| Requests | Gửi HTTP request giữa Coordinator và các Bank Services |
| JSON | Lưu pending transaction phục vụ recovery |
| Transaction Log | Ghi lại trạng thái transaction |

---

## 5. Project Structure

```text
Distributed-2PC-Project/
│
├── coordinator/
│   └── app.py
│
├── bank_a/
│   └── app.py
│
├── bank_b/
│   └── app.py
│
├── databases/
│   ├── bank_a.db
│   └── bank_b.db
│
├── logs/
│   ├── coordinator.log
│   └── pending_transactions.json
│
├── setup_database.py
├── requirements.txt
└── README.md
```

### Ý nghĩa các thư mục chính

| Thành phần | Mô tả |
|---|---|
| `coordinator/` | Chứa code của Coordinator Service |
| `bank_a/` | Chứa code của Bank A Service |
| `bank_b/` | Chứa code của Bank B Service |
| `databases/` | Chứa SQLite database của từng ngân hàng |
| `logs/` | Chứa transaction log và pending transaction |
| `setup_database.py` | File khởi tạo database và dữ liệu mẫu |
| `requirements.txt` | Danh sách thư viện cần cài đặt |
| `README.md` | Hướng dẫn setup, chạy và test project |

---

## 6. Dataset

Dataset được tự tạo để phục vụ mô phỏng giao dịch chuyển khoản.

Project không sử dụng dataset từ Kaggle hoặc nguồn bên ngoài vì mục tiêu chính không phải phân tích dữ liệu, mà là mô phỏng cơ chế **commit protocol** trong distributed database.

### Bank A Accounts

| Account ID | Owner Name | Balance |
|---|---|---|
| A001 | Alice | 5000 |
| A002 | David | 3000 |

### Bank B Accounts

| Account ID | Owner Name | Balance |
|---|---|---|
| B001 | Bob | 2000 |
| B002 | Tom | 4000 |

---

## 7. Setup Instructions

### Step 1: Tạo virtual environment

Mở terminal tại thư mục gốc project và chạy:

```bash
python -m venv venv
```

---

### Step 2: Activate virtual environment

Nếu dùng Windows PowerShell:

```bash
.\venv\Scripts\Activate.ps1
```

Nếu dùng Windows CMD:

```bash
venv\Scripts\activate
```

Sau khi activate thành công, terminal sẽ hiển thị:

```text
(venv)
```

---

### Step 3: Cài đặt dependencies

```bash
pip install -r requirements.txt
```

Nếu chưa có file `requirements.txt`, có thể cài trực tiếp:

```bash
pip install flask requests
```

Sau đó tạo lại file:

```bash
pip freeze > requirements.txt
```

---

### Step 4: Khởi tạo database

```bash
python setup_database.py
```

Sau khi chạy thành công, project sẽ tạo:

```text
databases/bank_a.db
databases/bank_b.db
```

---

## 8. How to Run the System

Cần mở **3 terminal riêng biệt** để chạy 3 node.

---

### Terminal 1 - Run Coordinator

```bash
cd coordinator
python app.py
```

Coordinator chạy tại:

```text
http://127.0.0.1:5000
```

---

### Terminal 2 - Run Bank A

```bash
cd bank_a
python app.py
```

Bank A chạy tại:

```text
http://127.0.0.1:5001
```

---

### Terminal 3 - Run Bank B

```bash
cd bank_b
python app.py
```

Bank B chạy tại:

```text
http://127.0.0.1:5002
```

---

## 9. API Testing Tools

Có thể test API bằng:

- Postman
- Thunder Client trong VSCode
- Browser đối với các API `GET`

Các API dạng `POST` nên test bằng Postman hoặc Thunder Client.

---

## 10. Check All Nodes

API này dùng để kiểm tra Coordinator có kết nối được với Bank A và Bank B hay không.

### Method

```text
GET
```

### URL

```text
http://127.0.0.1:5000/check_nodes
```

### Expected Result

```json
{
  "Bank_A": "ONLINE",
  "Bank_B": "ONLINE"
}
```

Nếu một node bị tắt, kết quả có thể là:

```json
{
  "Bank_A": "ONLINE",
  "Bank_B": "OFFLINE"
}
```

---

## 11. View All Accounts

API này dùng để xem dữ liệu tài khoản hiện tại ở Bank A và Bank B.

### Method

```text
GET
```

### URL

```text
http://127.0.0.1:5000/all_accounts
```

### Expected Result

```json
{
  "Bank_A": [
    {
      "account_id": "A001",
      "balance": 5000.0,
      "owner_name": "Alice"
    },
    {
      "account_id": "A002",
      "balance": 3000.0,
      "owner_name": "David"
    }
  ],
  "Bank_B": [
    {
      "account_id": "B001",
      "balance": 2000.0,
      "owner_name": "Bob"
    },
    {
      "account_id": "B002",
      "balance": 4000.0,
      "owner_name": "Tom"
    }
  ]
}
```

---

## 12. Normal 2PC Transaction

API này mô phỏng giao dịch chuyển khoản bình thường theo giao thức **Two-Phase Commit**.

### Method

```text
POST
```

### URL

```text
http://127.0.0.1:5000/transfer
```

### Body

```json
{
  "transaction_id": "TXN001",
  "from_account": "A001",
  "to_account": "B001",
  "amount": 1000
}
```

### Quy trình xử lý

```text
INITIAL
↓
PREPARE
↓
READY
↓
COMMIT
```

### Expected Result

Transaction được commit thành công.

Trước khi transfer:

```text
A001 = 5000
B001 = 2000
```

Sau khi transfer:

```text
A001 = 4000
B001 = 3000
```

### Ý nghĩa

Ở normal transaction, Coordinator thực hiện đầy đủ 2 phase:

**Phase 1 - PREPARE**

Coordinator gửi yêu cầu `PREPARE` đến Bank A và Bank B.

- Bank A kiểm tra tài khoản gửi có đủ tiền không.
- Bank B kiểm tra tài khoản nhận có tồn tại không.

Nếu cả hai trả về `READY`, transaction được phép chuyển sang phase tiếp theo.

**Phase 2 - COMMIT**

Coordinator gửi `COMMIT` đến Bank A và Bank B.

- Bank A trừ tiền tài khoản gửi.
- Bank B cộng tiền tài khoản nhận.

---

## 13. Prepare Phase Test

API này chỉ dùng để test phase đầu tiên của 2PC, chưa làm thay đổi số dư.

### Method

```text
POST
```

### URL

```text
http://127.0.0.1:5000/prepare_transfer
```

### Body

```json
{
  "from_account": "A001",
  "to_account": "B001",
  "amount": 1000
}
```

### Expected Result

```json
{
  "coordinator_decision": "READY_TO_COMMIT"
}
```

Nếu tài khoản gửi không đủ tiền hoặc tài khoản nhận không tồn tại, Coordinator sẽ trả về:

```json
{
  "coordinator_decision": "ABORT"
}
```

---

## 14. Coordinator Crash Simulation

API này mô phỏng lỗi chính của project: **Coordinator crash sau PREPARE phase nhưng trước COMMIT phase**.

### Method

```text
POST
```

### URL

```text
http://127.0.0.1:5000/transfer_crash
```

### Body

```json
{
  "transaction_id": "TXN003",
  "from_account": "A001",
  "to_account": "B001",
  "amount": 1000
}
```

### Quy trình xử lý

```text
INITIAL
↓
PREPARE
↓
READY
↓
CRASH
```

### Expected Result

Coordinator nhận được `READY` từ Bank A và Bank B, sau đó giả lập crash trước khi gửi `COMMIT`.

Kết quả mong muốn:

```json
{
  "status": "COORDINATOR_CRASHED",
  "message": "Simulated crash after READY and before COMMIT. No COMMIT was sent."
}
```

Lúc này balance chưa thay đổi:

```text
A001 = 5000
B001 = 2000
```

### Ý nghĩa

Trạng thái này cho thấy transaction đã được các participant đồng ý, nhưng Coordinator chưa gửi quyết định cuối cùng.  
Đây là tình huống cần recovery sau khi Coordinator reboot.

---

## 15. Recovery After Coordinator Reboot

Sau khi mô phỏng crash, restart lại Coordinator để tượng trưng cho việc Coordinator reboot.

Sau đó gọi API recovery.

### Method

```text
POST
```

### URL

```text
http://127.0.0.1:5000/recover
```

### Body

Không cần body.

### Quy trình xử lý

```text
RECOVERY
↓
COMMIT
```

### Expected Result

```json
{
  "status": "RECOVERY_COMPLETED",
  "results": {
    "TXN003": {
      "status": "RECOVERED_AND_COMMITTED"
    }
  }
}
```

Sau khi recovery:

```text
A001 = 4000
B001 = 3000
```

### Ý nghĩa

Khi Coordinator reboot, hệ thống đọc lại file `pending_transactions.json` để tìm transaction chưa hoàn tất.  
Sau đó Coordinator gửi tiếp `COMMIT` đến Bank A và Bank B để hoàn thành transaction.

---

## 16. Transaction Log

Coordinator ghi lại trạng thái transaction vào file:

```text
logs/coordinator.log
```

Ví dụ log của normal transaction:

```text
TXN001 | INITIAL
TXN001 | PREPARE
TXN001 | READY
TXN001 | COMMIT
```

Ví dụ log của crash/recovery transaction:

```text
TXN003 | INITIAL
TXN003 | PREPARE
TXN003 | READY
TXN003 | CRASH
TXN003 | RECOVERY
TXN003 | COMMIT
```

Transaction log là phần quan trọng để chứng minh hệ thống có khả năng recovery sau failure.

---

## 17. Pending Transaction

Khi Coordinator crash sau trạng thái `READY`, transaction sẽ được lưu vào file:

```text
logs/pending_transactions.json
```

File này dùng để lưu các transaction chưa hoàn tất.

Ví dụ:

```json
{
  "TXN003": {
    "transaction_id": "TXN003",
    "from_account": "A001",
    "to_account": "B001",
    "amount": 1000
  }
}
```

Khi gọi API `/recover`, Coordinator sẽ:

1. Đọc file `pending_transactions.json`.
2. Tìm transaction đang chờ xử lý.
3. Gửi lại `COMMIT` đến Bank A và Bank B.
4. Xóa transaction khỏi pending file nếu recovery thành công.

---

## 18. Failure Scenarios

Project có thể kiểm thử các failure scenario sau:

### Scenario 1: Bank A không đủ tiền

Body:

```json
{
  "transaction_id": "TXN002",
  "from_account": "A001",
  "to_account": "B001",
  "amount": 999999
}
```

Expected Result:

```text
ABORT
```

Lý do:

```text
Bank A không đủ balance để thực hiện giao dịch.
```

---

### Scenario 2: Tài khoản nhận không tồn tại

Body:

```json
{
  "transaction_id": "TXN004",
  "from_account": "A001",
  "to_account": "B999",
  "amount": 1000
}
```

Expected Result:

```text
ABORT
```

Lý do:

```text
Bank B không tìm thấy tài khoản nhận.
```

---

### Scenario 3: Coordinator crash trước COMMIT

Body:

```json
{
  "transaction_id": "TXN003",
  "from_account": "A001",
  "to_account": "B001",
  "amount": 1000
}
```

Expected Result:

```text
INITIAL → PREPARE → READY → CRASH
```

Sau đó recovery:

```text
RECOVERY → COMMIT
```

---

## 19. Success Criteria

Project được xem là thành công khi đạt các tiêu chí sau:

- Coordinator giao tiếp được với Bank A và Bank B.
- Hệ thống thực hiện được normal 2PC transaction.
- Bank A trừ tiền chính xác.
- Bank B cộng tiền chính xác.
- Hệ thống mô phỏng được Coordinator crash sau PREPARE và trước COMMIT.
- Balance không thay đổi trước khi recovery.
- Coordinator có thể recovery transaction sau khi reboot.
- Transaction log thể hiện rõ các trạng thái:
  - INITIAL
  - PREPARE
  - READY
  - COMMIT
  - CRASH
  - RECOVERY
- Dữ liệu cuối cùng vẫn nhất quán sau recovery.

---

## 20. Demo Scenario

Kịch bản demo đề xuất khi quay video 3-5 phút.

---

### Scenario 1: Normal Transaction

1. Run Coordinator, Bank A, Bank B.
2. Gọi API `/all_accounts` để xem balance ban đầu.
3. Gọi API `/transfer`.
4. Gọi lại `/all_accounts`.
5. Kiểm tra:
   - A001 giảm 1000.
   - B001 tăng 1000.
6. Mở `coordinator.log` để xem:
   - INITIAL
   - PREPARE
   - READY
   - COMMIT

---

### Scenario 2: Coordinator Crash and Recovery

1. Reset database bằng `setup_database.py`.
2. Run Coordinator, Bank A, Bank B.
3. Gọi API `/transfer_crash`.
4. Kiểm tra `coordinator.log` có:
   - INITIAL
   - PREPARE
   - READY
   - CRASH
5. Gọi `/all_accounts` để xác nhận balance chưa đổi.
6. Restart Coordinator.
7. Gọi API `/recover`.
8. Gọi lại `/all_accounts`.
9. Kiểm tra:
   - A001 giảm 1000.
   - B001 tăng 1000.
10. Kiểm tra log có thêm:
   - RECOVERY
   - COMMIT

---

## 21. Reset Database

Trong quá trình test, balance có thể thay đổi nhiều lần.  
Để đưa dữ liệu về trạng thái ban đầu, chạy lệnh:

```bash
python setup_database.py
```

Sau khi reset:

```text
A001 = 5000
A002 = 3000
B001 = 2000
B002 = 4000
```

---

## 22. Important Notes

Project này được xây dựng cho mục đích học tập, nhằm mô phỏng cơ chế **Two-Phase Commit**, **transaction logging** và **recovery** trong môi trường distributed database.

Project không phải là hệ thống ngân hàng thực tế. Các account, balance và transaction đều là dữ liệu mẫu để minh họa cách hoạt động của commit protocol.

Trong phạm vi project này, hệ thống chọn mức độ triển khai cơ bản:

- Chạy trên localhost.
- Mỗi node chạy ở một terminal riêng.
- Mỗi bank có database SQLite riêng.
- Coordinator giao tiếp với các bank qua REST API.
- Recovery dựa trên transaction log và pending transaction file.

---

## 23. Author

**Nguyễn Minh Tâm**  
**Team Name:** Mingxin  
**Project:** Distributed Database - Basic 2PC Cross-Bank Transfer