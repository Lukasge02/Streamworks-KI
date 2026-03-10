-- Seed dropdown options
INSERT INTO dropdown_options (category, label, value, sort_order) VALUES
-- Agents
('agents', 'UC4_UNIX_01', 'UC4_UNIX_01', 1),
('agents', 'UC4_UNIX_02', 'UC4_UNIX_02', 2),
('agents', 'UC4_WIN_01', 'UC4_WIN_01', 3),
('agents', 'UC4_WIN_02', 'UC4_WIN_02', 4),
('agents', 'UC4_SAP_01', 'UC4_SAP_01', 5),
-- Transfer Modes
('transfer_mode', 'Binary', 'binary', 1),
('transfer_mode', 'Text', 'text', 2),
('transfer_mode', 'Auto', 'auto', 3),
-- Schedules
('schedule', 'Täglich', 'täglich', 1),
('schedule', 'Wöchentlich', 'wöchentlich', 2),
('schedule', 'Monatlich', 'monatlich', 3),
('schedule', 'Stündlich', 'stündlich', 4),
('schedule', 'Einmalig', 'einmalig', 5),
-- Job Types
('job_type', 'Standard Job', 'STANDARD', 1),
('job_type', 'Dateitransfer', 'FILE_TRANSFER', 2),
('job_type', 'SAP Job', 'SAP', 3),
-- SAP Systems
('sap_system', 'PA1', 'PA1', 1),
('sap_system', 'P01', 'P01', 2),
('sap_system', 'QA1', 'QA1', 3),
('sap_system', 'DEV', 'DEV', 4),
-- Calendars
('calendar', 'Werktage DE', 'WERKTAGE_DE', 1),
('calendar', 'Alle Tage', 'ALLE_TAGE', 2),
('calendar', 'Monatsende', 'MONATSENDE', 3)
ON CONFLICT (category, value) DO NOTHING;
