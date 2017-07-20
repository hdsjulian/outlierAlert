BEGIN TRANSACTION;
CREATE TABLE `telegram_users` (
	`id`	INTEGER,
	`user_name`	INTEGER,
	`user_id`	INTEGER,
	PRIMARY KEY(`id`)
);
CREATE TABLE "telegram_offset" (
	`offset`	INTEGER
);
CREATE TABLE "product_color_size" (
	`product_color_id`	INTEGER,
	`product_color_size_id`	INTEGER,
	`sizes`	TEXT,
	`timestamp`	INTEGER,
	PRIMARY KEY(`product_color_size_id`)
);
CREATE TABLE `product_color_price` (
	`product_color_id`	INTEGER,
	`price`	INTEGER,
	`timestamp`	INTEGER
);
CREATE TABLE "product_color" (
	`color_id`	INTEGER,
	`product_id`	INTEGER,
	`introduction`	INTEGER,
	`product_color_id`	INTEGER,
	PRIMARY KEY(`product_color_id`)
);
CREATE TABLE "color" (
	`color_id`	INTEGER,
	`color_name`	TEXT,
	PRIMARY KEY(`color_id`)
);
CREATE TABLE "Product" (
	`product_id`	INTEGER,
	`product_name`	TEXT,
	`introduction`	TEXT,
	`URL`	TEXT,
	`discontinued`	INTEGER,
	PRIMARY KEY(`product_id`)
);
COMMIT;
