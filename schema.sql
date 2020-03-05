DROP TABLE IF EXISTS items;

CREATE TABLE items (
  id INTEGER UNIQUE PRIMARY KEY,
  name TEXT,
  category TEXT
);

INSERT INTO items VALUES (12345, 'Milk', 'Dairy');
INSERT INTO items VALUES (324, 'Sausages', 'Meet');
