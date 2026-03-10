DROP TABLE IF EXISTS public.students;

CREATE TABLE IF NOT EXISTS public.students (
	student_id SERIAL PRIMARY KEY,
	first_name TEXT,
	last_name TEXT,
	middle_name TEXT,
	email TEXT,
	phone_number TEXT,
	street_address TEXT,
	city TEXT,
	state TEXT,
	zip_code TEXT,
	enrollment_status TEXT,
	residency TEXT,
	year TEXT,
	major TEXT,
	concentration TEXT,
	department TEXT,
	gpa REAL,
	financial_class TEXT,
	first_gen BOOLEAN,
	race TEXT,
	ethnicity TEXT,
	gender TEXT,
	disability BOOLEAN,
	military BOOLEAN,
	opted_in BOOLEAN
);

SELECT to_regclass('public.students');

DROP TABLE IF EXISTS public.grants;

CREATE TABLE IF NOT EXISTS public.grants (
	grant_id SERIAL PRIMARY KEY,
	grant_name TEXT,
	grantor TEXT,
	due_date DATE,
	amount INTEGER,
	military BOOLEAN,
	disability BOOLEAN,
	minimum_gpa REAL,
	required_year TEXT,
	major_requirement TEXT,
	financial_need BOOLEAN,
	residency TEXT,
	first_gen BOOLEAN,
	race TEXT,
	ethnicity TEXT,
	gender TEXT,
	manual_component TEXT,
	auto_apply BOOLEAN,
	app_email TEXT,
	app_url TEXT
);

SELECT to_regclass('public.grants');
