DROP TABLE IF EXISTS items;

CREATE TABLE items (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT,
  category TEXT
);

INSERT INTO items (name, category) VALUES ('Milk', 'Dairy');
INSERT INTO items (name, category) VALUES ('Sausages', 'Meet');
