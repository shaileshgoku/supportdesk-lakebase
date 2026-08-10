-- SupportDesk Sample Data

-- Insert support tickets
INSERT INTO tickets
(title, status, created_by)
VALUES
('Unable to login to sales dashboard', 'open', 'Arun'),
('Daily data refresh failed', 'in_progress', 'Priya'),
('Access request for finance dashboard', 'resolved', 'Rahul');

-- Insert ticket messages
INSERT INTO ticket_messages
(ticket_id, message_text, author)
VALUES
(1, 'I am unable to login to the sales dashboard since this morning.', 'Arun'),
(1, 'I have tried resetting my password, but I am still unable to login.', 'Support'),

(2, 'The daily dashboard refresh failed at 7 AM today.', 'Priya'),
(2, 'We are investigating the data pipeline failure.', 'Support'),

(3, 'I need access to the finance dashboard for the monthly reporting process.', 'Rahul'),
(3, 'Access has been granted successfully.', 'Support');
