-- WM 2026 Tippspiel – Supabase Setup
-- Ausführen im Supabase SQL Editor

DROP TABLE IF EXISTS tips;
DROP TABLE IF EXISTS matches;

CREATE TABLE matches (
  id SERIAL PRIMARY KEY,
  match_date TEXT NOT NULL,
  home TEXT NOT NULL,
  away TEXT NOT NULL,
  group_name TEXT NOT NULL,
  kickoff_utc TIMESTAMPTZ NOT NULL,
  result TEXT DEFAULT NULL
);

CREATE TABLE tips (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  match_id INT REFERENCES matches(id) ON DELETE CASCADE,
  participant TEXT NOT NULL,
  tip TEXT NOT NULL,
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(match_id, participant)
);

ALTER TABLE matches ENABLE ROW LEVEL SECURITY;
ALTER TABLE tips ENABLE ROW LEVEL SECURITY;

CREATE POLICY "matches_read"   ON matches FOR SELECT USING (true);
CREATE POLICY "matches_update" ON matches FOR UPDATE USING (true);

CREATE POLICY "tips_read"   ON tips FOR SELECT USING (true);
CREATE POLICY "tips_insert" ON tips FOR INSERT
  WITH CHECK ((SELECT kickoff_utc FROM matches WHERE id = match_id) > NOW());
CREATE POLICY "tips_update" ON tips FOR UPDATE
  USING ((SELECT kickoff_utc FROM matches WHERE id = match_id) > NOW());
CREATE POLICY "tips_delete" ON tips FOR DELETE USING (true);

-- 72 Vorrundenspiele mit Anstoßzeiten (UTC)
INSERT INTO matches (match_date, home, away, group_name, kickoff_utc) VALUES
-- Spieltag 1
('11.06.', 'Mexiko',          'Südafrika',      'A', '2026-06-11T19:00:00Z'),
('12.06.', 'Südkorea',        'Tschechien',     'A', '2026-06-12T02:00:00Z'),
('12.06.', 'Kanada',          'Bosnien-Herz.',  'B', '2026-06-12T19:00:00Z'),
('13.06.', 'USA',             'Paraguay',       'D', '2026-06-13T01:00:00Z'),
('13.06.', 'Katar',           'Schweiz',        'B', '2026-06-13T19:00:00Z'),
('13.06.', 'Brasilien',       'Marokko',        'C', '2026-06-13T22:00:00Z'),
('14.06.', 'Haiti',           'Schottland',     'C', '2026-06-14T01:00:00Z'),
('14.06.', 'Australien',      'Türkei',         'D', '2026-06-14T04:00:00Z'),
('14.06.', 'Deutschland',     'Curaçao',        'E', '2026-06-14T17:00:00Z'),
('14.06.', 'Niederlande',     'Japan',          'F', '2026-06-14T20:00:00Z'),
('14.06.', 'Elfenbeinküste',  'Ecuador',        'E', '2026-06-14T23:00:00Z'),
('15.06.', 'Schweden',        'Tunesien',       'F', '2026-06-15T02:00:00Z'),
('15.06.', 'Spanien',         'Kap Verde',      'H', '2026-06-15T16:00:00Z'),
('15.06.', 'Belgien',         'Ägypten',        'G', '2026-06-15T19:00:00Z'),
('15.06.', 'Saudi-Arabien',   'Uruguay',        'H', '2026-06-15T22:00:00Z'),
('16.06.', 'Iran',            'Neuseeland',     'G', '2026-06-16T01:00:00Z'),
('16.06.', 'Frankreich',      'Senegal',        'I', '2026-06-16T19:00:00Z'),
('16.06.', 'Irak',            'Norwegen',       'I', '2026-06-16T22:00:00Z'),
('17.06.', 'Argentinien',     'Algerien',       'J', '2026-06-17T01:00:00Z'),
('17.06.', 'Österreich',      'Jordanien',      'J', '2026-06-17T04:00:00Z'),
('17.06.', 'Portugal',        'DR Kongo',       'K', '2026-06-17T17:00:00Z'),
('17.06.', 'England',         'Kroatien',       'L', '2026-06-17T20:00:00Z'),
('17.06.', 'Ghana',           'Panama',         'L', '2026-06-17T23:00:00Z'),
('18.06.', 'Usbekistan',      'Kolumbien',      'K', '2026-06-18T02:00:00Z'),
-- Spieltag 2
('18.06.', 'Tschechien',      'Südafrika',      'A', '2026-06-18T16:00:00Z'),
('18.06.', 'Mexiko',          'Südkorea',       'A', '2026-06-18T19:00:00Z'),
('18.06.', 'Schweiz',         'Bosnien-Herz.',  'B', '2026-06-18T22:00:00Z'),
('19.06.', 'Kanada',          'Katar',          'B', '2026-06-19T01:00:00Z'),
('19.06.', 'Schottland',      'Marokko',        'C', '2026-06-19T16:00:00Z'),
('19.06.', 'Brasilien',       'Haiti',          'C', '2026-06-19T19:00:00Z'),
('19.06.', 'USA',             'Australien',     'D', '2026-06-19T22:00:00Z'),
('20.06.', 'Türkei',          'Paraguay',       'D', '2026-06-20T01:00:00Z'),
('20.06.', 'Niederlande',     'Schweden',       'F', '2026-06-20T16:00:00Z'),
('20.06.', 'Deutschland',     'Elfenbeinküste', 'E', '2026-06-20T19:00:00Z'),
('20.06.', 'Ecuador',         'Curaçao',        'E', '2026-06-20T22:00:00Z'),
('21.06.', 'Tunesien',        'Japan',          'F', '2026-06-21T01:00:00Z'),
('21.06.', 'Spanien',         'Saudi-Arabien',  'H', '2026-06-21T16:00:00Z'),
('21.06.', 'Belgien',         'Iran',           'G', '2026-06-21T19:00:00Z'),
('21.06.', 'Uruguay',         'Kap Verde',      'H', '2026-06-21T22:00:00Z'),
('22.06.', 'Neuseeland',      'Ägypten',        'G', '2026-06-22T01:00:00Z'),
('22.06.', 'Frankreich',      'Irak',           'I', '2026-06-22T16:00:00Z'),
('22.06.', 'Norwegen',        'Senegal',        'I', '2026-06-22T19:00:00Z'),
('22.06.', 'Argentinien',     'Österreich',     'J', '2026-06-22T22:00:00Z'),
('23.06.', 'Jordanien',       'Algerien',       'J', '2026-06-23T01:00:00Z'),
('23.06.', 'Portugal',        'Usbekistan',     'K', '2026-06-23T16:00:00Z'),
('23.06.', 'England',         'Ghana',          'L', '2026-06-23T19:00:00Z'),
('23.06.', 'Panama',          'Kroatien',       'L', '2026-06-23T22:00:00Z'),
('24.06.', 'Kolumbien',       'DR Kongo',       'K', '2026-06-24T01:00:00Z'),
-- Spieltag 3 (je 2 Spiele pro Gruppe gleichzeitig)
('24.06.', 'Tschechien',      'Mexiko',         'A', '2026-06-24T16:00:00Z'),
('24.06.', 'Südafrika',       'Südkorea',       'A', '2026-06-24T16:00:00Z'),
('24.06.', 'Schweiz',         'Kanada',         'B', '2026-06-24T19:00:00Z'),
('24.06.', 'Bosnien-Herz.',   'Katar',          'B', '2026-06-24T19:00:00Z'),
('24.06.', 'Schottland',      'Brasilien',      'C', '2026-06-24T22:00:00Z'),
('24.06.', 'Marokko',         'Haiti',          'C', '2026-06-24T22:00:00Z'),
('25.06.', 'Ecuador',         'Deutschland',    'E', '2026-06-25T01:00:00Z'),
('25.06.', 'Curaçao',         'Elfenbeinküste', 'E', '2026-06-25T01:00:00Z'),
('25.06.', 'Japan',           'Schweden',       'F', '2026-06-25T16:00:00Z'),
('25.06.', 'Tunesien',        'Niederlande',    'F', '2026-06-25T16:00:00Z'),
('25.06.', 'Türkei',          'USA',            'D', '2026-06-25T19:00:00Z'),
('25.06.', 'Paraguay',        'Australien',     'D', '2026-06-25T19:00:00Z'),
('26.06.', 'Norwegen',        'Frankreich',     'I', '2026-06-26T16:00:00Z'),
('26.06.', 'Senegal',         'Irak',           'I', '2026-06-26T16:00:00Z'),
('26.06.', 'Kap Verde',       'Saudi-Arabien',  'H', '2026-06-26T19:00:00Z'),
('26.06.', 'Uruguay',         'Spanien',        'H', '2026-06-26T19:00:00Z'),
('26.06.', 'Ägypten',         'Iran',           'G', '2026-06-26T22:00:00Z'),
('26.06.', 'Neuseeland',      'Belgien',        'G', '2026-06-26T22:00:00Z'),
('27.06.', 'Panama',          'England',        'L', '2026-06-27T16:00:00Z'),
('27.06.', 'Kroatien',        'Ghana',          'L', '2026-06-27T16:00:00Z'),
('27.06.', 'Kolumbien',       'Portugal',       'K', '2026-06-27T19:00:00Z'),
('27.06.', 'DR Kongo',        'Usbekistan',     'K', '2026-06-27T19:00:00Z'),
('27.06.', 'Algerien',        'Österreich',     'J', '2026-06-27T22:00:00Z'),
('27.06.', 'Jordanien',       'Argentinien',    'J', '2026-06-27T22:00:00Z');
