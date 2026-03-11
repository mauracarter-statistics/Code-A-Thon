DROP TABLE IF EXISTS public.students;
CREATE TABLE IF NOT EXISTS public.students (
	student_id SERIAL PRIMARY KEY,

	-- Personal Info
	first_name TEXT,
	last_name TEXT,
	middle_name TEXT,
	email TEXT,
	phone_number TEXT,
	-- Address
	street_address TEXT,
	city TEXT,
	state TEXT,
	zip_code TEXT,
	-- Academic Info
	major TEXT,
	concentration TEXT,
	department TEXT,
	academic_year TEXT,
	enrollment_status TEXT,
	gpa DECIMAL(3, 2),
	-- Financial Info
	residency TEXT,
	financial_class TEXT,
	-- Demographics
	first_gen BOOLEAN,
	race TEXT,
	ethnicity TEXT,
	gender TEXT,
	disability BOOLEAN,
	military BOOLEAN,
	-- System
	opted_in BOOLEAN
);
SELECT to_regclass('public.students');

DROP TABLE IF EXISTS public.grants;
CREATE TABLE IF NOT EXISTS public.grants (
	grant_id SERIAL PRIMARY KEY,
	-- Grant Info
	grant_name TEXT,
	grantor TEXT,
	amount DECIMAL(10,2),
	due_date DATE,
	-- Eligibility Info
	minimum_gpa REAL,
	academic_year TEXT,
	major_requirement TEXT,
	financial_need BOOLEAN,
	residency TEXT,
	first_gen BOOLEAN,
	race TEXT,
	ethnicity TEXT,
	gender TEXT,
	disability BOOLEAN,
	military BOOLEAN,
	-- Applicant Info
	manual_component TEXT,
	auto_apply BOOLEAN,
	app_email TEXT,
	app_url TEXT
);
SELECT to_regclass('public.grants');