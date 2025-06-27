# Hướng Dẫn Crop Ảnh Maid Về Tỷ Lệ 3:4

## 📐 Tổng Quan

Tất cả 50 ảnh maid trong hệ thống đã được crop về tỷ lệ 3:4 để đảm bảo:
- **Hiển thị nhất quán** trong Discord embeds
- **Kích thước chuẩn**: 450x600 pixels (3:4 ratio)
- **Chất lượng cao** với JPEG quality 95%
- **Crop từ center** để giữ phần quan trọng nhất của ảnh

## 📂 Cấu Trúc File

```
Bot/
├── art/
│   └── maids_cropped/          # 🆕 Thư mục chứa ảnh đã crop
│       ├── rem-ur.jpg          # UR Maids
│       ├── saber-ur.jpg
│       ├── ...
│       ├── mikasa-ssr.jpg      # SSR Maids  
│       ├── asuna-ssr.jpg
│       ├── ...
│       ├── usagi-sr.jpg        # SR Maids
│       ├── hinata-sr.jpg
│       ├── ...
│       ├── android18-r.jpg     # R Maids
│       └── tsunade-r.jpg
└── features/
    └── maid_config.py          # ✅ Đã cập nhật URLs
```

## 🔄 Quy Trình Đã Thực Hiện

### Bước 1: Crop Ảnh
- ✅ Download 50 ảnh từ Discord CDN URLs
- ✅ Crop từ center về tỷ lệ 3:4
- ✅ Resize về 450x600 pixels
- ✅ Lưu với chất lượng JPEG 95%

### Bước 2: Cập Nhật Config
- ✅ Backup `maid_config.py` → `maid_config_backup.py`
- ✅ Cập nhật tất cả 50 `art_url` với đường dẫn local
- ✅ Format: `art/maids_cropped/{maid-name}.jpg`

## 📊 Thống Kê

| Rarity | Số Lượng | Kích Thước Mỗi File | Tổng Dung Lượng |
|--------|----------|-------------------|------------------|
| UR     | 6 maids  | ~80-130 KB        | ~600 KB          |
| SSR    | 10 maids | ~60-120 KB        | ~900 KB          |
| SR     | 15 maids | ~70-150 KB        | ~1.5 MB          |
| R      | 19 maids | ~50-150 KB        | ~1.8 MB          |
| **Total** | **50 maids** | **~4.8 MB** | **Tiết kiệm băng thông** |

## 🎨 Lợi Ích

### 1. **Hiển Thị Nhất Quán**
- Tất cả ảnh có cùng tỷ lệ 3:4
- Không bị méo hay stretch trong embeds
- Layout đẹp và professional

### 2. **Hiệu Suất Tối Ưu**
- File size nhỏ gọn (~50-150 KB mỗi ảnh)
- Sử dụng local files thay vì download từ Discord CDN
- Tải nhanh hơn cho người dùng

### 3. **Dễ Bảo Trì**
- Tất cả ảnh trong cùng folder `art/maids_cropped/`
- Naming convention nhất quán: `{maid-key}.jpg`
- Backup config để rollback nếu cần

## 🔧 Cấu Hình Hiện Tại

```python
# Ví dụ URLs sau khi cập nhật
MAID_TEMPLATES = {
    "rem_ur": {
        "art_url": "art/maids_cropped/rem-ur.jpg",     # ✅ Local
        # ... other properties
    },
    "saber_ur": {
        "art_url": "art/maids_cropped/saber-ur.jpg",   # ✅ Local
        # ... other properties  
    },
    # ... tất cả 50 maids
}
```

## 💡 Lưu Ý Quan Trọng

### ✅ Đã Hoàn Thành
- [x] 50/50 ảnh đã crop thành công
- [x] Tất cả URLs đã cập nhật
- [x] Backup config đã tạo
- [x] Files tạm thời đã dọn dẹp

### 🚀 Sẵn Sàng Deploy
- Hệ thống maid có thể sử dụng ngay
- Ảnh hiển thị đẹp và nhất quán
- Performance tối ưu

### 🔄 Rollback (Nếu Cần)
```bash
# Khôi phục config cũ
cp features/maid_config_backup.py features/maid_config.py
```

## 🎯 Kết Luận

Việc crop ảnh về tỷ lệ 3:4 đã:
- ✅ Cải thiện UX với hiển thị nhất quán
- ✅ Tối ưu performance với local files
- ✅ Chuẩn hóa asset management
- ✅ Sẵn sàng cho production

Hệ thống maid giờ đây có ảnh đẹp, nhất quán và tối ưu! 