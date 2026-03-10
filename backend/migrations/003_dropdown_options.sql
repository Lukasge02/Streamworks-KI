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

-- Unique constraint for idempotent seeding
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'uq_dropdown_category_value'
    ) THEN
        ALTER TABLE dropdown_options ADD CONSTRAINT uq_dropdown_category_value UNIQUE (category, value);
    END IF;
END$$;
