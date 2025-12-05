import pandas as pd
import os
import glob
from pathlib import Path

def find_and_merge_files(pattern, output_filename):
    files = glob.glob(pattern)
    if not files:
        print(f"Không tìm thấy file nào với pattern: {pattern}")
        return None
    
    print(f"Tìm thấy {len(files)} file với pattern: {pattern}")
    for file in files:
        print(f"  - {os.path.basename(file)}")
    
    all_dataframes = []
    successful_files = 0
    
    for file in files:
        try:
            print(f"Đang xử lý file: {os.path.basename(file)}")
            
            df = None
            engines = ['openpyxl', 'xlrd']
            
            for engine in engines:
                try:
                    df = pd.read_excel(file, engine=engine)
                    break
                except Exception as engine_error:
                    print(f"    Lỗi với engine {engine}: {engine_error}")
                    continue
            
            if df is None:
                print(f"Không thể đọc file với bất kỳ engine nào")
                continue
                
            # Bỏ qua file rỗng
            if len(df) == 0:
                print(f"File rỗng, bỏ qua")
                continue
                
            all_dataframes.append(df)
            successful_files += 1
            print(f"Đã đọc thành công: {len(df)} dòng")
            
        except Exception as e:
            print(f"Lỗi khi đọc file {os.path.basename(file)}: {e}")
    
    if not all_dataframes:
        print("Không có file nào được đọc thành công!")
        return None
    
    print(f"\nĐã đọc thành công {successful_files}/{len(files)} file")
    print("Đang gộp dữ liệu...")
    
    # Gộp tất cả dataframe với tùy chọn tối ưu
    merged_df = pd.concat(all_dataframes, ignore_index=True, sort=False)
    
    print(f"Gộp hoàn tất. Tổng số dòng: {len(merged_df)}")
    
    # Kiểm tra kích thước file để quyết định định dạng output
    estimated_size_mb = len(merged_df) * len(merged_df.columns) * 8 / (1024 * 1024)
    
    if estimated_size_mb > 50:
        csv_filename = output_filename.replace('.xlsx', '.csv')
        print(f"File lớn ({estimated_size_mb:.1f}MB ước tính), lưu dưới dạng CSV: {csv_filename}")
        merged_df.to_csv(csv_filename, index=False, encoding='utf-8-sig')
        print(f"Đã lưu thành công: {csv_filename}")
    else:
        print(f"Đang lưu file Excel: {output_filename}")
        try:
            # Tối ưu hóa việc ghi Excel
            with pd.ExcelWriter(output_filename, engine='openpyxl', 
                              options={'remove_timezone': True}) as writer:
                merged_df.to_excel(writer, index=False, sheet_name='Data')
            print(f"Đã lưu thành công: {output_filename}")
        except Exception as save_error:
            # Fallback sang CSV nếu không lưu được Excel
            csv_filename = output_filename.replace('.xlsx', '.csv')
            print(f"Lỗi lưu Excel ({save_error}), chuyển sang CSV: {csv_filename}")
            merged_df.to_csv(csv_filename, index=False, encoding='utf-8-sig')
            print(f"Đã lưu thành công: {csv_filename}")
    
    print(f"  Tổng số dòng: {len(merged_df)}")
    print(f"  Tổng số cột: {len(merged_df.columns)}")
    
    return merged_df

def preprocess_and_save(file_path, column_mapping, output_filename):
    try:
        df = pd.read_csv(file_path, encoding='utf-8')
        print(f"--- Đã tải thành công: {file_path} ---")

        cols_to_keep = list(column_mapping.keys())

        df_selected = df[[col for col in cols_to_keep if col in df.columns]]
        
        current_mapping = {k: v for k, v in column_mapping.items() if k in df_selected.columns}
        df_processed = df_selected.rename(columns=current_mapping)

        df_processed.to_csv(output_filename, index=False, encoding='utf-8')
        print(f"Đã xử lý và lưu thành công vào: {output_filename}")
        print(f"Số lượng cột sau xử lý: {len(df_processed.columns)}")
        print(f"Các cột sau xử lý: {df_processed.columns.tolist()}")
        print("-" * 50)
        return df_processed
    except FileNotFoundError:
        print(f"Lỗi: Không tìm thấy file tại đường dẫn: {file_path}")
        return None
    except Exception as e:
        print(f"Đã xảy ra lỗi trong quá trình xử lý file {file_path}: {e}")
        return None

# 1. Tệp: Danh Sách Chi Tiết Hóa Đơn (Invoice Details)
invoice_details_file = "DanhSachChiTietHoaDon_KV17112025-162223-581.xlsx - DanhSachChiTietHoaDon_KV1711202.csv"
invoice_details_mapping = {
    'Chi nhánh': 'branch_name',
    'Mã hóa đơn': 'invoice_id',
    'Mã vận đơn': 'tracking_id',
    'Địa chỉ lấy hàng': 'pickup_address',
    'Mã đối soát': 'reconciliation_code',
    'Phí trả ĐTGH': 'cod_fee',
    'Thời gian': 'timestamp',
    'Thời gian tạo': 'created_at',
    'Ngày cập nhật': 'updated_at',
    'Mã đặt hàng': 'order_id',
    'Mã YCSC': 'ycsc_code',
    'Mã trả hàng': 'return_code',
    'Mã khách hàng': 'customer_id',
    'Tên khách hàng': 'customer_name',
    'Email': 'email',
    'Điện thoại': 'phone',
    'Địa chỉ (Khách hàng)': 'customer_address',
    'Khu vực (Khách hàng)': 'customer_area',
    'Phường/Xã (Khách hàng)': 'customer_ward',
    'Ngày sinh': 'birthdate',
    'Bảng giá': 'price_list',
    'Người bán': 'salesperson_name',
    'Kênh bán': 'sales_channel',
    'Người tạo': 'created_by',
    'Đối tác giao hàng': 'shipping_partner',
    'Người nhận': 'recipient_name',
    'Điện thoại (Người nhận)': 'recipient_phone',
    'Địa chỉ (Người nhận)': 'recipient_address',
    'Khu vực (Người nhận)': 'recipient_area',
    'Phường/Xã (Người nhận)': 'recipient_ward',
    'Dịch vụ': 'service_type',
    'Trọng lượng (gram)': 'weight_gram',
    'Dài': 'length',
    'Rộng': 'width',
    'Cao': 'height',
    'Ghi chú trạng thái giao hàng': 'shipping_status_note',
    'Ghi chú giao hàng': 'delivery_note',
    'Ghi chú': 'note',
    'Tổng tiền hàng': 'subtotal',
    'Giảm giá hóa đơn': 'invoice_discount',
    'Khách cần trả': 'total_amount',
    'Khách đã trả': 'amount_paid',
    'Tiền mặt': 'cash_amount',
    'Thẻ': 'card_amount',
    'Ví': 'wallet_amount',
    'Chuyển khoản': 'bank_transfer_amount',
    'Voucher': 'voucher',
    'Mã voucher': 'voucher_code',
    'Còn cần thu (COD)': 'cod_remaining',
    'Thời gian giao hàng': 'delivery_time',
    'Trạng thái': 'status',
    'Trạng thái giao hàng': 'shipping_status',
    'Mã hàng': 'product_id',
    'Mã vạch': 'barcode',
    'Tên hàng': 'product_name',
    'Thương hiệu': 'brand',
    'ĐVT': 'unit_of_measure',
    'Ghi chú hàng hóa': 'product_note',
    'Số lượng': 'quantity',
    'Đơn giá': 'unit_price',
    'Giảm giá %': 'item_discount_percent',
    'Giảm giá': 'item_discount_amount',
    'Giá bán': 'sale_price',
    'Thành tiền': 'line_total',
    'Bảo hành': 'warranty',
    'Định kỳ bảo trì': 'maintenance_cycle'
}

output_invoice_details = 'import/Data/processed/processed_invoice_details.csv'

# 2. Tệp: Danh Sách Khách Hàng (Customers)
customers_file = "DanhSachKhachHang_KV17112025-170955-526.xlsx - DanhSachKhachHang_KV17112025-17.csv"
customers_mapping = {
    'Loại khách': 'customer_type',
    'Chi nhánh tạo': 'created_branch',
    'Mã khách hàng': 'customer_id',
    'Tên khách hàng': 'customer_name',
    'Điện thoại': 'phone',
    'Địa chỉ': 'address',
    'Khu vực giao hàng': 'shipping_area',
    'Phường/Xã': 'ward_commune',
    'Công ty': 'company_name',
    'Mã số thuế': 'tax_id',
    'Số CMND/CCCD': 'identity_card_number',
    'Ngày sinh': 'dob',
    'Giới tính': 'gender',
    'Email': 'email',
    'Facebook': 'facebook_url',
    'Nhóm khách hàng': 'customer_group',
    'Ghi chú': 'note',
    'Người tạo': 'created_by',
    'Ngày tạo': 'created_at',
    'Ngày giao dịch cuối': 'last_transaction_date',
    'Nợ cần thu hiện tại': 'current_debt',
    'Tổng bán': 'total_sales',
    'Tổng bán trừ trả hàng': 'net_sales',
    'Trạng thái': 'status'
}
output_customers = "import/Data/processed/processed_customers.csv"
# 3. Tệp: Danh Sách Nhà Cung Cấp (Suppliers)
suppliers_file = "DanhSachNhaCungCap_KV17112025-160828-186.xlsx - DanhSachNhaCungCap_KV17112025-1.csv"
suppliers_mapping = {
    'Mã nhà cung cấp': 'supplier_id',
    'Tên nhà cung cấp': 'supplier_name',
    'Email': 'email',
    'Điện thoại': 'phone',
    'Địa chỉ': 'address',
    'Khu vực': 'area',
    'Phường/Xã': 'ward_commune',
    'Tổng mua': 'total_purchased',
    'Nợ cần trả hiện tại': 'current_liability',
    'Mã số thuế': 'tax_id',
    'Ghi chú': 'note',
    'Nhóm nhà cung cấp': 'supplier_group',
    'Trạng thái': 'status',
    'Tổng mua trừ trả hàng': 'net_purchased',
    'Chi nhánh': 'branch_name',
    'Công ty': 'company_name',
    'Người tạo': 'created_by',
    'Ngày tạo': 'created_at'
}

output_suppliers = "import/Data/processed/processed_suppliers.csv"

# 4. Tệp: Danh Sách Sản Phẩm (Products)
products_file = "DanhSachSanPham_KV17112025-170911-902.xlsx - DanhSachSanPham_KV17112025-1709.csv"
products_mapping = {
    'Loại hàng': 'product_type',
    'Nhóm hàng(3 Cấp)': 'category_3_level',
    'Mã hàng': 'product_id',
    'Mã vạch': 'barcode',
    'Tên hàng': 'product_name',
    'Thương hiệu': 'brand',
    'Giá bán': 'sale_price',
    'Giá vốn': 'cost_price',
    'Tồn kho': 'stock_quantity',
    'KH đặt': 'reserved_quantity',
    'Dự kiến hết hàng': 'estimated_oos_date',
    'Tồn nhỏ nhất': 'min_stock_threshold',
    'Tồn lớn nhất': 'max_stock_threshold',
    'ĐVT': 'unit_of_measure',
    'Mã ĐVT Cơ bản': 'base_unit_code',
    'Quy đổi': 'conversion_rate',
    'Thuộc tính': 'attributes',
    'Mã HH Liên quan': 'related_product_code',
    'Hình ảnh (url1,url2...)': 'image_urls',
    'Trọng lượng': 'weight_gram',
    'Đang kinh doanh': 'is_active',
    'Được bán trực tiếp': 'is_direct_sale',
    'Mô tả': 'description',
    'Mẫu ghi chú': 'note_template',
    'Vị trí': 'location',
    'Hàng thành phần': 'component_items',
    'Bảo hành': 'warranty_period',
    'Bảo trì định kỳ': 'maintenance_cycle'
}

output_products = "import/Data/processed/processed_products.csv"

# BƯỚC 1: GỘP CÁC FILE CÙNG LOẠI

print("=" * 60)
print("BƯỚC 1: GỘP CÁC FILE CÙNG LOẠI")
print("=" * 60)


chitiet_hoadon_pattern = "import/Data/raw/DanhSachChiTietHoaDon_*.xlsx"
merged_chitiet_hoadon_file = "import/Data/merged/merged_DanhSachChiTietHoaDon.xlsx"
find_and_merge_files(chitiet_hoadon_pattern, merged_chitiet_hoadon_file)

hoadon_pattern = "import/Data/raw/DanhSachHoaDon_*.xlsx"
merged_hoadon_file = "import/Data/merged/merged_DanhSachHoaDon.xlsx"
find_and_merge_files(hoadon_pattern, merged_hoadon_file)

khachhang_pattern = "import/Data/raw/DanhSachKhachHang_*.xlsx"
merged_khachhang_file = "import/Data/merged/merged_DanhSachKhachHang.xlsx"
find_and_merge_files(khachhang_pattern, merged_khachhang_file)

nhacungcap_pattern = "import/Data/raw/DanhSachNhaCungCap_*.xlsx"
merged_nhacungcap_file = "import/Data/merged/merged_DanhSachNhaCungCap.xlsx"
find_and_merge_files(nhacungcap_pattern, merged_nhacungcap_file)

sanpham_pattern = "import/Data/raw/DanhSachSanPham_*.xlsx"
merged_sanpham_file = "import/Data/merged/merged_DanhSachSanPham.xlsx"
find_and_merge_files(sanpham_pattern, merged_sanpham_file)

print("\n" + "=" * 60)
print("BƯỚC 2: XỬ LÝ DỮ LIỆU SAU KHI ĐÃ GỘP")
print("=" * 60)

def preprocess_merged_file(input_file, column_mapping, output_filename):
    try:
        if input_file.endswith('.csv'):
            df = pd.read_csv(input_file, encoding='utf-8')
        else:
            df = pd.read_excel(input_file)
            
        print(f"--- Đã tải thành công: {input_file} ---")
        print(f"Số lượng dòng: {len(df)}")
        print(f"Số lượng cột: {len(df.columns)}")

        cols_to_keep = list(column_mapping.keys())

        available_cols = [col for col in cols_to_keep if col in df.columns]
        df_selected = df[available_cols]
        
        print(f"Các cột có sẵn: {available_cols}")
        
        current_mapping = {k: v for k, v in column_mapping.items() if k in df_selected.columns}
        df_processed = df_selected.rename(columns=current_mapping)

        csv_output = output_filename.replace('.xlsx', '.csv')
        df_processed.to_csv(csv_output, index=False, encoding='utf-8-sig')
        print(f"Đã xử lý và lưu thành công vào: {csv_output}")
        print(f"Số lượng cột sau xử lý: {len(df_processed.columns)}")
        print(f"Các cột sau xử lý: {df_processed.columns.tolist()}")
        print("-" * 50)
        return df_processed
    except FileNotFoundError:
        print(f"Lỗi: Không tìm thấy file tại đường dẫn: {input_file}")
        return None
    except Exception as e:
        print(f"Đã xảy ra lỗi trong quá trình xử lý file {input_file}: {e}")
        return None

for base_name, mapping, output in [
    ('import/Data/merged/merged_DanhSachChiTietHoaDon', invoice_details_mapping, 'import/Data/processed/processed_merged_invoice_details.csv'),
    ('import/Data/merged/merged_DanhSachKhachHang', customers_mapping, 'import/Data/processed/processed_merged_customers.csv'),
    ('import/Data/merged/merged_DanhSachNhaCungCap', suppliers_mapping, 'import/Data/processed/processed_merged_suppliers.csv'), 
    ('import/Data/merged/merged_DanhSachSanPham', products_mapping, 'import/Data/processed/processed_merged_products.csv')
]:
    xlsx_file = f"{base_name}.xlsx"
    csv_file = f"{base_name}.csv"
    if os.path.exists(xlsx_file):
        preprocess_merged_file(xlsx_file, mapping, output)
    elif os.path.exists(csv_file):
        preprocess_merged_file(csv_file, mapping, output)

hoadon_mapping = {
    'Chi nhánh': 'branch_name',
    'Mã hóa đơn': 'invoice_id', 
    'Thời gian tạo': 'created_at',
    'Mã khách hàng': 'customer_id',
    'Tên khách hàng': 'customer_name',
    'Người bán': 'salesperson_name',
    'Kênh bán': 'sales_channel',
    'Người tạo': 'created_by',
    'Ghi chú': 'note',
    'Tổng tiền hàng': 'subtotal',
    'Giảm giá hóa đơn': 'invoice_discount', 
    'Khách cần trả': 'total_amount',
    'Khách đã trả': 'amount_paid',
    'Trạng thái': 'status'
}

xlsx_hoadon = "merged_DanhSachHoaDon.xlsx"
csv_hoadon = "merged_DanhSachHoaDon.csv"

if os.path.exists(xlsx_hoadon):
    preprocess_merged_file(xlsx_hoadon, hoadon_mapping, 'processed_merged_invoices.csv')
elif os.path.exists(csv_hoadon):
    preprocess_merged_file(csv_hoadon, hoadon_mapping, 'processed_merged_invoices.csv')



branch_mapping = {
    "Chi nhánh trung tâm": "CN_MAIN",
    "HỆ THỐNG PTK 06 - CHỢ KINH LAI PHỤNG": "PTK06",
    "HÊ THỐNG PTK 08 -SƠN ĐỊNH": "PTK08"
}

customer_file = "import/Data/processed/processed_merged_customers.csv"
df_cus = pd.read_csv(customer_file)
df_cus["created_branch"] = df_cus["created_branch"].astype(str).str.strip()
df_cus["created_branch_id"] = df_cus["created_branch"].map(branch_mapping)
df_cus = df_cus[["created_branch_id"] + [c for c in df_cus.columns if c != "created_branch_id"]]
df_cus.drop(columns=["created_branch"], inplace=True)
df_cus.to_csv(customer_file, index=False, encoding="utf-8-sig")
print("✔ Đã xử lý xong customers →", customer_file)


supplier_file = "import/Data/processed/processed_merged_suppliers.csv"
df_sup = pd.read_csv(supplier_file)
df_sup["branch_name"] = df_sup["branch_name"].astype(str).str.strip()
df_sup["branch_id"] = df_sup["branch_name"].map(branch_mapping)
df_sup = df_sup[["branch_id"] + [c for c in df_sup.columns if c != "branch_id"]]
df_sup.drop(columns=["branch_name"], inplace=True)
df_sup.to_csv(supplier_file, index=False, encoding="utf-8-sig")
print("✔ Đã xử lý xong suppliers →", supplier_file)


invoice_file = "import/Data/processed/processed_merged_invoice_details.csv"
df_invoice = pd.read_csv(invoice_file,low_memory=False)

df_invoice["branch_name"] = df_invoice["branch_name"].astype(str).str.strip()
df_invoice["branch_id"] = df_invoice["branch_name"].map(branch_mapping)
df_invoice.drop(columns=["branch_name"], inplace=True)

invoice_cols = [
    "invoice_id", "branch_id", "created_at", "updated_at",
    "status", "shipping_status", "subtotal", "invoice_discount",
    "total_amount", "amount_paid", "salesperson_name", "customer_id", "note"
]
for col in ["created_at", "updated_at"]:
    df_invoice[col] = pd.to_datetime(df_invoice[col], dayfirst=True).dt.strftime("%Y-%m-%d %H:%M:%S")


df_invoices = df_invoice[invoice_cols].drop_duplicates(subset=["invoice_id"])
df_invoices.to_csv("import/Data/processed/invoices.csv", index=False, encoding="utf-8-sig")
print("✔ Đã tạo file invoices.csv")

item_cols = [
    "invoice_id", "product_id", "barcode", "product_name", "brand",
    "unit_of_measure", "quantity", "unit_price", "item_discount_amount",
    "sale_price", "line_total", "warranty", "maintenance_cycle"
]

df_items = df_invoice[item_cols].copy()
df_items.to_csv("import/Data/processed/invoice_items.csv", index=False, encoding="utf-8-sig")
print("✔ Đã tạo file invoice_items.csv")