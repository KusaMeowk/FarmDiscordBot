-- Maid System Database Indexes Migration
-- Tăng performance cho hệ thống maid

-- Add indexes for user_maids table
CREATE INDEX IF NOT EXISTS idx_user_maids_user_id ON user_maids(user_id);
CREATE INDEX IF NOT EXISTS idx_user_maids_instance_id ON user_maids(instance_id);  
CREATE INDEX IF NOT EXISTS idx_user_maids_user_active ON user_maids(user_id, is_active);
CREATE INDEX IF NOT EXISTS idx_user_maids_maid_id ON user_maids(maid_id);

-- Add indexes for gacha_history table
CREATE INDEX IF NOT EXISTS idx_gacha_history_user_id ON gacha_history(user_id);
CREATE INDEX IF NOT EXISTS idx_gacha_history_created_at ON gacha_history(created_at);

-- Add indexes for user_stardust table  
CREATE INDEX IF NOT EXISTS idx_user_stardust_user_id ON user_stardust(user_id);

-- Add indexes for maid_trades table
CREATE INDEX IF NOT EXISTS idx_maid_trades_from_user ON maid_trades(from_user_id);
CREATE INDEX IF NOT EXISTS idx_maid_trades_to_user ON maid_trades(to_user_id);
CREATE INDEX IF NOT EXISTS idx_maid_trades_status ON maid_trades(trade_status);

-- Performance improvement queries
ANALYZE user_maids;
ANALYZE gacha_history;
ANALYZE user_stardust;
ANALYZE maid_trades; 