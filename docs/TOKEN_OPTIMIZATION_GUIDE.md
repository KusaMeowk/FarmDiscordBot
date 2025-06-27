# Token Optimization Guide - Gemini Game Master

## Tổng Quan

Hệ thống Game Master đã được tích hợp **đầy đủ** các tính năng tối ưu hóa token để giảm thiểu chi phí API và tận dụng tối đa quota hàng ngày.

## 🎯 Các Tính Năng Token Dự Phòng

### 1. **Smart Decision Cache**
```python
# Tự động cache decisions cho game states tương tự
- Pattern Matching: Phân loại game state thành patterns (high-good-low-sunny)
- Reuse Logic: Tái sử dụng decisions cho tình huống tương tự
- Success Filtering: Chỉ cache decisions có success rate > 60%
- Auto Expiry: Cache tự hết hạn sau 14 ngày
- Token Savings: ~2,500 tokens mỗi cache hit
```

### 2. **Context Caching (Gemini API)**
```python
# Tận dụng Context Caching của Gemini
- Base Context: Cache phần prompt cố định (quyền admin, format)
- Variable Data: Chỉ gửi dữ liệu thay đổi (game state)
- Cost Reduction: $0.075/1M tokens thay vì $0.30/1M tokens
- Storage Cost: $1.00/1M tokens/hour
```

### 3. **Multi-API Key Rotation**
```python
# Sử dụng nhiều API keys để tăng quota
"gemini_apis": {
  "primary": { "daily_limit": 1048576 },    # ~1M tokens/ngày
  "secondary": { "daily_limit": 1048576 },  # ~1M tokens/ngày  
  "backup": { "daily_limit": 1048576 }      # ~1M tokens/ngày
}
# Tổng: ~3M tokens/ngày
```

### 4. **Optimized Prompting**
```python
# Tách prompt thành 2 phần
Base Context (cached):     ~800 tokens - chỉ gửi 1 lần
Variable Data (dynamic):   ~400 tokens - gửi mỗi request
Total per request:         ~1200 tokens thay vì ~2500 tokens
Savings:                   ~52% token reduction
```

## 📊 Ước Tính Token Usage Với Optimization

### **Trước Optimization:**
- **96 requests/ngày** × **2,500 tokens** = **240,000 tokens/ngày**
- **Chi phí**: ~$0.228/ngày

### **Sau Optimization:**

#### **Cache Hit Rate 40%** (conservative):
- **Cache Hits**: 38 requests × 0 tokens = **0 tokens**
- **Cache Misses**: 58 requests × 1,200 tokens = **69,600 tokens**
- **Tổng**: **69,600 tokens/ngày**
- **Chi phí**: ~$0.070/ngày (**tiết kiệm 69%**)

#### **Cache Hit Rate 60%** (realistic):
- **Cache Hits**: 58 requests × 0 tokens = **0 tokens**
- **Cache Misses**: 38 requests × 1,200 tokens = **45,600 tokens**
- **Tổng**: **45,600 tokens/ngày**
- **Chi phí**: ~$0.046/ngày (**tiết kiệm 80%**)

## 🚀 Rate Limit Capacity

### **Free Tier:**
- ❌ **Không đủ** - Chỉ 250 RPD, cần 96 RPD

### **Tier 1 (Paid):**
- ✅ **Hoàn toàn đủ**
- **TPM**: 1,000,000 (chỉ dùng ~4.6%)
- **RPD**: 10,000 (chỉ dùng ~1%)
- **Dư thừa**: Có thể tăng tần suất lên 5-10 phút

### **Với Multi-API Keys:**
- **3 keys × 1M tokens** = **3M tokens/ngày**
- **Capacity sử dụng**: 45,600/3,000,000 = **1.5%**
- **Dư thừa khổng lồ**: Có thể chạy 60+ bots cùng lúc

## 💰 Chi Phí Thực Tế

### **Hàng Ngày:**
- **Optimized**: $0.046
- **Tiết kiệm**: $0.182 (80%)

### **Hàng Tháng:**
- **Optimized**: $1.38
- **Tiết kiệm**: $5.46 (80%)

### **Hàng Năm:**
- **Optimized**: $16.79
- **Tiết kiệm**: $66.43 (80%)

## 🎮 Commands Quản Lý

### **Xem Token Stats:**
```
!gm status    # Trạng thái tổng quan với token optimization
!gm tokens    # Chi tiết token usage và projections
!gm cache     # Thông tin smart cache system
```

### **Quản Lý Cache:**
```
!gm cache info     # Xem thông tin cache
!gm cache stats    # Thống kê chi tiết
!gm cache clear    # Xóa cache (reset)
```

## 🔧 Tối Ưu Hóa Nâng Cao

### **1. Batch Processing:**
```python
# Có thể group nhiều decisions nhỏ thành 1 request lớn
# Tiết kiệm overhead tokens
```

### **2. Conditional Analysis:**
```python
# Chỉ phân tích khi có thay đổi đáng kể
# Skip analysis nếu game state stable
```

### **3. Predictive Caching:**
```python
# Pre-cache decisions cho scenarios phổ biến
# Reduce cold start latency
```

## ⚡ Kết Luận

**Hệ thống đã sẵn sàng** với khả năng tối ưu hóa token mạnh mẽ:

✅ **Smart Caching**: Tiết kiệm 60-80% tokens
✅ **Context Optimization**: Giảm 52% prompt size  
✅ **Multi-API Rotation**: Tăng 3x quota capacity
✅ **Cost Effective**: Chỉ ~$1.38/tháng
✅ **Scalable**: Có thể mở rộng 60x mà không vượt quota

**Tận dụng được tối đa** các tính năng dự phòng của Gemini API để đảm bảo hoạt động ổn định và tiết kiệm chi phí. 