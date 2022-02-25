--How to update an app name from squid to api in the db
UPDATE django_content_type SET app_label='api' WHERE app_label='squid';

ALTER TABLE squid_appointment_id_seq RENAME TO api_appointment_id_seq;
ALTER TABLE squid_appointmentquestion RENAME TO api_appointmentquestion;
ALTER TABLE squid_appointmentquestion_id_seq RENAME TO api_appointmentquestion_id;
ALTER TABLE squid_oceanuser RENAME TO api_oceanuser;
ALTER TABLE squid_oceanuser_id_seq RENAME TO api_oceanuser_id_seq;
ALTER TABLE squid_question RENAME TO api_question;
ALTER TABLE squid_question_id_seq RENAME TO api_question_id_seq;
ALTER TABLE squid_shop RENAME TO api_shop;
ALTER TABLE squid_shop_id_seq RENAME TO api_shop_id_seq;

UPDATE django_migrations SET app='api' WHERE app='squid';

UPDATE django_content_type set model ='squid' where model = 'oceanuser';

