# Data Warehouse & Analytics Pipeline  
(Postgres – Spark – MinIO – Airflow – Grafana)

---

## 1. Tổng quan dự án

Dự án xây dựng một hệ thống **Data Warehouse & Analytics end-to-end** theo kiến trúc hiện đại **Bronze – Silver – Gold – Serving**, sử dụng các công nghệ mã nguồn mở phổ biến trong thực tế.

Hệ thống cho phép:
- Thu thập dữ liệu giao dịch từ PostgreSQL
- Lưu trữ dữ liệu thô trong Data Lake
- Xử lý dữ liệu batch bằng Spark
- Orchestrate pipeline bằng Airflow
- Phân tích & trực quan hóa dữ liệu bằng Grafana

---

## 2. Kiến trúc hệ thống

Luồng dữ liệu tổng quát:

PostgreSQL (Source)  
→ Bronze Layer (MinIO)  
→ Silver Layer (MinIO)  
→ Gold Layer (MinIO)  
→ PostgreSQL (erp_serving)  
→ Grafana Dashboard

### Vai trò từng layer

- **Bronze layer**
  - Dữ liệu thô, gần như nguyên bản từ hệ thống nguồn
  - Lưu toàn bộ lịch sử để dễ truy vết và replay

- **Silver layer**
  - Dữ liệu đã được làm sạch
  - Chuẩn hóa kiểu dữ liệu, tên cột, loại bỏ dữ liệu lỗi

- **Gold layer**
  - Dữ liệu phân tích
  - Mô hình hóa theo Star Schema (Fact & Dimension)

- **Serving layer**
  - PostgreSQL `erp_serving`
  - Tối ưu cho truy vấn BI và dashboard

---

## 3. Công nghệ sử dụng

- Docker & Docker Compose
- Apache Airflow
- Apache Spark + Delta Lake
- PostgreSQL
- MinIO (S3 compatible)
- Grafana

---

## 4. Hướng dẫn chạy project (Quick Start)

### Bước 1: Khởi động toàn bộ hệ thống

Tại thư mục gốc của project, chạy:

```bash
docker compose up -d
```
### Bước 2: Chạy pipeline ETL trên Airflow

Truy cập Airflow UI:  
URL: [http://localhost:8081](http://localhost:8081)  
Username: `airflow`  
Password: `airflow`

#### Các bước thực hiện
1. Vào Airflow UI  
2. Chạy DAG **init_project** để khởi tạo metadata / cấu trúc ban đầu  
3. Chạy DAG **ETL_process** theo thứ tự:
   - PostgreSQL → Bronze  
   - Bronze → Silver  
   - Silver → Gold  
4. Đảm bảo tất cả task đều ở trạng thái **Success ✔**

Sau khi hoàn tất, dữ liệu **Gold layer** sẽ được load vào database `erp_serving`.

---

### Bước 3: Kết nối Grafana với PostgreSQL (erp_serving)

Truy cập Grafana:  
URL: [http://localhost:3000](http://localhost:3000)  
Username: `admin`  
Password: `admin`

#### Thêm Data Source
1. Vào **Configuration → Data sources**  
2. Chọn **PostgreSQL**  
3. Điền thông tin kết nối:
   - Host URL: `postgres_source:5432`  
   - Database name: `erp_serving`  
   - Username: `admin`  
   - Password: `admin`  
   - TLS/SSL Mode: `Disable`  
4. Nhấn **Save & Test**

Nếu kết nối thành công, Grafana sẵn sàng để tạo dashboard.
---

### Bước 4: Import Dashboard & Visualization

Hệ thống đã chuẩn bị sẵn file dashboard mẫu: **Overview-1765867688236.json**

#### Các bước thực hiện
1. Truy cập Grafana: [http://localhost:3000](http://localhost:3000)  
   Username: `admin`  
   Password: `admin`  

2. Vào menu **Dashboards → Create dashboard → Import a dashboard**  

3. Chọn **Upload JSON file** và import file: `Overview-1765867688236.json`
---

### Kết quả mong đợi

- Pipeline ETL chạy tự động trên **Airflow**  
- Dữ liệu được xử lý theo mô hình **Bronze → Silver → Gold**  
- PostgreSQL `erp_serving` chứa dữ liệu phân tích  
- Grafana hiển thị dashboard realtime phục vụ phân tích và báo cáo 