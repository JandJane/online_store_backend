-- CREATE DATABASE my_db;
USE my_db;

CREATE TABLE items (
  id INT PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(100),
  category VARCHAR(100)
);

INSERT INTO items (name, category) VALUES ('Milk', 'Dairy');
INSERT INTO items (name, category) VALUES ('Sausages', 'Meet');
