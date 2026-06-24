-- WM 2026 – KO-Runden einfügen
-- Alle Teams als '?' – werden automatisch per fetch_results.py gefüllt sobald Paarungen feststehen
-- Zeiten in UTC (MESZ = UTC+2)

INSERT INTO matches (home, away, kickoff_utc, group_name) VALUES

-- Runde der 32 (16 Spiele) – 28. Juni bis 4. Juli
('?', '?', '2026-06-28T19:00:00Z', 'Rd. 32'),
('?', '?', '2026-06-29T17:00:00Z', 'Rd. 32'),
('?', '?', '2026-06-29T20:30:00Z', 'Rd. 32'),
('?', '?', '2026-06-30T01:00:00Z', 'Rd. 32'),
('?', '?', '2026-06-30T17:00:00Z', 'Rd. 32'),
('?', '?', '2026-06-30T21:00:00Z', 'Rd. 32'),
('?', '?', '2026-07-01T01:00:00Z', 'Rd. 32'),
('?', '?', '2026-07-01T16:00:00Z', 'Rd. 32'),
('?', '?', '2026-07-01T20:00:00Z', 'Rd. 32'),
('?', '?', '2026-07-02T00:00:00Z', 'Rd. 32'),
('?', '?', '2026-07-02T19:00:00Z', 'Rd. 32'),
('?', '?', '2026-07-02T23:00:00Z', 'Rd. 32'),
('?', '?', '2026-07-03T03:00:00Z', 'Rd. 32'),
('?', '?', '2026-07-03T18:00:00Z', 'Rd. 32'),
('?', '?', '2026-07-03T22:00:00Z', 'Rd. 32'),
('?', '?', '2026-07-04T01:30:00Z', 'Rd. 32'),

-- Achtelfinale (8 Spiele) – 4. bis 7. Juli
('?', '?', '2026-07-04T17:00:00Z', 'Achtelfinale'),
('?', '?', '2026-07-04T21:00:00Z', 'Achtelfinale'),
('?', '?', '2026-07-05T20:00:00Z', 'Achtelfinale'),
('?', '?', '2026-07-06T00:00:00Z', 'Achtelfinale'),
('?', '?', '2026-07-06T19:00:00Z', 'Achtelfinale'),
('?', '?', '2026-07-07T00:00:00Z', 'Achtelfinale'),
('?', '?', '2026-07-07T16:00:00Z', 'Achtelfinale'),
('?', '?', '2026-07-07T20:00:00Z', 'Achtelfinale'),

-- Viertelfinale (4 Spiele) – 9. bis 12. Juli
('?', '?', '2026-07-09T20:00:00Z', 'Viertelfinale'),
('?', '?', '2026-07-10T19:00:00Z', 'Viertelfinale'),
('?', '?', '2026-07-11T21:00:00Z', 'Viertelfinale'),
('?', '?', '2026-07-12T01:00:00Z', 'Viertelfinale'),

-- Halbfinale (2 Spiele) – 14. & 15. Juli
('?', '?', '2026-07-14T19:00:00Z', 'Halbfinale'),
('?', '?', '2026-07-15T19:00:00Z', 'Halbfinale'),

-- Spiel um Platz 3 – 18. Juli
('?', '?', '2026-07-18T21:00:00Z', 'Platz 3'),

-- Finale – 19. Juli
('?', '?', '2026-07-19T19:00:00Z', 'Finale');
