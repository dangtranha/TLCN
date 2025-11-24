import pandas as pd

# đọc Excel
df = pd.read_excel("D:\\TLCN\\mongodb\\data\\raw_data\\DanhSachChiTietHoaDon_KV07112025-091342-05.xlsx", sheet_name="Sheet1")

# xuất CSV UTF-8 không BOM
df.to_csv("D:\\TLCN\\mongodb\\import\\sales.csv", index=False, encoding="utf-8")