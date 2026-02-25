-- Dropdown option values
CREATE TABLE IF NOT EXISTS dropdown_options (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    category TEXT NOT NULL,
    label TEXT NOT NULL,
    value TEXT NOT NULL,
    is_active BOOLEAN DEFAULT true,
    sort_order INT DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_dropdown_category ON dropdown_options(category);
