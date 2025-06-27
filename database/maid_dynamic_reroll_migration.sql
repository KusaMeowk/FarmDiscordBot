-- Migration for Dynamic Reroll Cost System
-- Thêm bảng tracking lịch sử reroll để tính dynamic cost

-- Create reroll history table
CREATE TABLE IF NOT EXISTS maid_reroll_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    maid_instance_id TEXT NOT NULL,
    old_buffs TEXT NOT NULL,  -- JSON của buffs cũ
    new_buffs TEXT NOT NULL,  -- JSON của buffs mới
    stardust_cost INTEGER NOT NULL,  -- Chi phí stardust đã trả
    reroll_time TEXT NOT NULL,  -- ISO timestamp
    FOREIGN KEY (maid_instance_id) REFERENCES user_maids(instance_id)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_reroll_history_maid ON maid_reroll_history(maid_instance_id);
CREATE INDEX IF NOT EXISTS idx_reroll_history_user ON maid_reroll_history(user_id);
CREATE INDEX IF NOT EXISTS idx_reroll_history_time ON maid_reroll_history(reroll_time);

-- Add reroll_count column to user_maids for quick access
ALTER TABLE user_maids ADD COLUMN reroll_count INTEGER DEFAULT 0;

-- Add last_reroll_time column to user_maids  
ALTER TABLE user_maids ADD COLUMN last_reroll_time TEXT;

-- Create view for easy access to reroll stats
CREATE VIEW IF NOT EXISTS maid_reroll_stats AS
SELECT 
    m.instance_id,
    m.user_id,
    m.maid_id,
    COUNT(h.id) as total_rerolls,
    MAX(h.reroll_time) as last_reroll_time,
    AVG(h.stardust_cost) as avg_cost,
    SUM(h.stardust_cost) as total_spent
FROM user_maids m
LEFT JOIN maid_reroll_history h ON m.instance_id = h.maid_instance_id
GROUP BY m.instance_id;

-- Performance optimization
ANALYZE maid_reroll_history; 