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
    'Trạng thái': 'status',
    'Mã hàng': 'product_id',
    'Tên hàng': 'product_name',
    'ĐVT': 'unit_of_measure',
    'Số lượng': 'quantity',
    'Đơn giá': 'unit_price',
    'Giảm giá': 'item_discount_amount',
    'Giá bán': 'sale_price',
    'Thành tiền': 'line_total'
}
output_invoice_details = 'processed_invoice_details.csv'

# 2. Tệp: Danh Sách Khách Hàng (Customers)
customers_file = "DanhSachKhachHang_KV17112025-170955-526.xlsx - DanhSachKhachHang_KV17112025-17.csv"
customers_mapping = {
    'Mã khách hàng': 'customer_id',
    'Tên khách hàng': 'customer_name',
    'Điện thoại': 'phone',
    'Địa chỉ': 'address',
    'Công ty': 'company_name',
    'Mã số thuế': 'tax_id',
    'Nhóm khách hàng': 'customer_group',
    'Ghi chú': 'note',
    'Ngày tạo': 'created_at',
    'Nợ cần thu hiện tại': 'current_debt',
    'Tổng bán trừ trả hàng': 'net_sales',
    'Trạng thái': 'status'
}
output_customers = 'processed_customers.csv'

# 3. Tệp: Danh Sách Nhà Cung Cấp (Suppliers)
suppliers_file = "DanhSachNhaCungCap_KV17112025-160828-186.xlsx - DanhSachNhaCungCap_KV17112025-1.csv"
suppliers_mapping = {
    'Mã nhà cung cấp': 'supplier_id',
    'Tên nhà cung cấp': 'supplier_name',
    'Điện thoại': 'phone',
    'Địa chỉ': 'address',
    'Tổng mua': 'total_purchased',
    'Nợ cần trả hiện tại': 'current_liability',
    'Mã số thuế': 'tax_id',
    'Ghi chú': 'note',
    'Trạng thái': 'status',
    'Tổng mua trừ trả hàng': 'net_purchased',
    'Ngày tạo': 'created_at'
}
output_suppliers = 'processed_suppliers.csv'

# 4. Tệp: Danh Sách Sản Phẩm (Products)
products_file = "DanhSachSanPham_KV17112025-170911-902.xlsx - DanhSachSanPham_KV17112025-1709.csv"
products_mapping = {
    'Nhóm hàng(3 Cấp)': 'category',
    'Mã hàng': 'product_id',
    'Mã vạch': 'barcode',
    'Tên hàng': 'product_name',
    'Thương hiệu': 'brand',
    'Quy đổi': 'unit',
    'Giá bán': 'sale_price',
    'Giá vốn': 'cost_price',
    'Tồn kho': 'total_stock',
    'ĐVT': 'unit_of_measure',
    'Đang kinh doanh': 'is_for_sale'
}
output_products = 'processed_products.csv'

# BƯỚC 1: GỘP CÁC FILE CÙNG LOẠI

print("=" * 60)
print("BƯỚC 1: GỘP CÁC FILE CÙNG LOẠI")
print("=" * 60)


chitiet_hoadon_pattern = "Data/raw/DanhSachChiTietHoaDon_*.xlsx"
merged_chitiet_hoadon_file = "Data/raw/merged_DanhSachChiTietHoaDon.xlsx"
find_and_merge_files(chitiet_hoadon_pattern, merged_chitiet_hoadon_file)

hoadon_pattern = "Data/raw/DanhSachHoaDon_*.xlsx"
merged_hoadon_file = "Data/raw/merged_DanhSachHoaDon.xlsx"
find_and_merge_files(hoadon_pattern, merged_hoadon_file)

khachhang_pattern = "Data/raw/DanhSachKhachHang_*.xlsx"
merged_khachhang_file = "Data/raw/merged_DanhSachKhachHang.xlsx"
find_and_merge_files(khachhang_pattern, merged_khachhang_file)

nhacungcap_pattern = "Data/raw/DanhSachNhaCungCap_*.xlsx"
merged_nhacungcap_file = "Data/raw/merged_DanhSachNhaCungCap.xlsx"
find_and_merge_files(nhacungcap_pattern, merged_nhacungcap_file)

sanpham_pattern = "Data/raw/DanhSachSanPham_*.xlsx"
merged_sanpham_file = "Data/raw/merged_DanhSachSanPham.xlsx"
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
    ('Data/merged/merged_DanhSachChiTietHoaDon', invoice_details_mapping, 'processed_merged_invoice_details.csv'),
    ('Data/merged/merged_DanhSachKhachHang', customers_mapping, 'processed_merged_customers.csv'),
    ('Data/merged/merged_DanhSachNhaCungCap', suppliers_mapping, 'processed_merged_suppliers.csv'), 
    ('Data/merged/merged_DanhSachSanPham', products_mapping, 'processed_merged_products.csv')
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