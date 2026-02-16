-- Adminer 5.3.0 PostgreSQL 17.4 dump

 DROP TABLE IF EXISTS "${table_prefix}service_jobs";
 DROP SEQUENCE IF EXISTS ${table_prefix}service_jobs_job_id_seq;
 CREATE SEQUENCE ${table_prefix}service_jobs_job_id_seq INCREMENT 1 MINVALUE 1 MAXVALUE 9223372036854775807 CACHE 1;

 CREATE TABLE "public"."${table_prefix}service_jobs" (
     "job_id" bigint DEFAULT nextval('${table_prefix}service_jobs_job_id_seq') NOT NULL,
     "command_uri" character varying(250) NOT NULL,
     "job_name" character varying(50) NOT NULL,
     "job_description" character varying(50),
     "update_ts" bigint NOT NULL,
     "ext" character varying(10000),
     CONSTRAINT "${table_prefix}service_jobs_key" PRIMARY KEY ("job_id")
 )
 WITH (oids = false);

 CREATE UNIQUE INDEX ${table_prefix}service_jobs_command_uri ON public.${table_prefix}service_jobs USING btree (command_uri);


DROP TABLE IF EXISTS "${table_prefix}dt_info";
DROP SEQUENCE IF EXISTS ${table_prefix}dt_info_id_seq;
CREATE SEQUENCE ${table_prefix}dt_info_id_seq INCREMENT 1 MINVALUE 1 MAXVALUE 9223372036854775807 CACHE 1;

CREATE TABLE "public"."${table_prefix}dt_info" (
    "dt_id" bigint DEFAULT nextval('${table_prefix}dt_info_id_seq') NOT NULL,
    "dt_uri" character varying(250) NOT NULL,
    "job_id" bigint,
    "market_id" bigint,
    "update_ts" bigint NOT NULL,
    "ext" character varying(10000),
    CONSTRAINT "${table_prefix}dt_info_key" PRIMARY KEY ("dt_id")
)
WITH (oids = false);

CREATE UNIQUE INDEX ${table_prefix}dt_info_dt_uri ON public.${table_prefix}dt_info USING btree (dt_uri,market_id);



DROP TABLE IF EXISTS "${table_prefix}consumption_range";
DROP SEQUENCE IF EXISTS ${table_prefix}consumption_range_range_id_seq;
CREATE SEQUENCE ${table_prefix}consumption_range_range_id_seq INCREMENT 1 MINVALUE 1 MAXVALUE 9223372036854775807 CACHE 1;

CREATE TABLE "public"."${table_prefix}consumption_range" (
    "range_id" integer DEFAULT nextval('${table_prefix}consumption_range_range_id_seq') NOT NULL,
    "min_value" double precision,
    "max_value" double precision,
    CONSTRAINT "${table_prefix}consumption_range_range_id" PRIMARY KEY ("range_id")
)
WITH (oids = false);

CREATE UNIQUE INDEX ${table_prefix}consumption_range_min_value_max_value ON public.${table_prefix}consumption_range USING btree (min_value, max_value);


DROP TABLE IF EXISTS "${table_prefix}forecast_details";
DROP SEQUENCE IF EXISTS ${table_prefix}forecast_details_forecast_id_seq;
CREATE SEQUENCE ${table_prefix}forecast_details_forecast_id_seq INCREMENT 1 MINVALUE 1 MAXVALUE 9223372036854775807 CACHE 1;

CREATE TABLE "public"."${table_prefix}forecast_details" (
    "forecast_id" bigint DEFAULT nextval('${table_prefix}forecast_details_forecast_id_seq') NOT NULL,
    "offer_id" bigint NOT NULL,
    "model_id" bigint NOT NULL,
    "ts" bigint NOT NULL,
    "isp_len" integer DEFAULT '1' NOT NULL,
    "isp_unit" integer NOT NULL,
    "update_ts" bigint NOT NULL,
    CONSTRAINT "${table_prefix}forecast_details_forecast_id" PRIMARY KEY ("forecast_id")
)
WITH (oids = false);

CREATE UNIQUE INDEX ${table_prefix}forecast_details_ts_model_id ON public.${table_prefix}forecast_details USING btree (ts, model_id,offer_id);

CREATE INDEX ${table_prefix}forecast_details_model_id ON public.${table_prefix}forecast_details USING btree (model_id);
CREATE INDEX ${table_prefix}forecast_details_offer_id ON public.${table_prefix}forecast_details USING btree (offer_id);


DROP TABLE IF EXISTS "${table_prefix}forecast_model";
DROP SEQUENCE IF EXISTS ${table_prefix}forecast_model_model_id_seq;
CREATE SEQUENCE ${table_prefix}forecast_model_model_id_seq INCREMENT 1 MINVALUE 1 MAXVALUE 2147483647 CACHE 1;

CREATE TABLE "public"."${table_prefix}forecast_model" (
    "model_id" integer DEFAULT nextval('${table_prefix}forecast_model_model_id_seq') NOT NULL,
    "market_id" bigint NOT NULL,
    "job_id" bigint NOT NULL,
    "model_uri" character varying(300),
    "model_name" character varying(30),
    "model_description" character varying(1000),
    "isp_len" integer DEFAULT '1' NOT NULL,
    "isp_unit" integer NOT NULL,
    "update_ts" bigint NOT NULL,
    "ext" character varying(1000),
    CONSTRAINT "${table_prefix}forecast_model_pkey" PRIMARY KEY ("model_id")
)
WITH (oids = false);
CREATE UNIQUE INDEX ${table_prefix}forecast_model_model_uri ON public.${table_prefix}forecast_model USING btree (model_uri);



DROP TABLE IF EXISTS "${table_prefix}market_details";
DROP SEQUENCE IF EXISTS ${table_prefix}market_details_market_id_seq;
CREATE SEQUENCE ${table_prefix}market_details_market_id_seq INCREMENT 1 MINVALUE 1 MAXVALUE 9223372036854775807 CACHE 1;

CREATE TABLE "public"."${table_prefix}market_details" (
    "market_id" bigint DEFAULT nextval('${table_prefix}market_details_market_id_seq') NOT NULL,
    "market_uri" character varying(250) NOT NULL,
    "market_name" character varying(50) NOT NULL,
    "market_type" character varying(30) NOT NULL,
    "market_description" character varying(50),
    "market_location" character varying(250),
    "subscribe" 	boolean  ,
    "isp_unit" integer NULL,
    "isp_len" integer NULL,
    "update_ts" bigint NOT NULL,
    "ext" character varying(10000),
    CONSTRAINT "${table_prefix}market_details_key" PRIMARY KEY ("market_id")
)
WITH (oids = false);

CREATE UNIQUE INDEX ${table_prefix}market_details_market_uri ON public.${table_prefix}market_details USING btree (market_uri);


DROP TABLE IF EXISTS "${table_prefix}market_offer";
CREATE TABLE "public"."${table_prefix}market_offer" (
    "offer_id" bigint NOT NULL,
    "isp_start" integer NOT NULL,
    "range_id" integer NOT NULL,
    "cost_mwh" double precision,
    "ts" bigint NOT NULL,
    "isp_len" integer NOT NULL,
    CONSTRAINT "${table_prefix}market_offer_market_id_offer_id_isp_start_range_id" PRIMARY KEY (  "offer_id", "isp_start", "range_id")
)
WITH (oids = false);

CREATE INDEX ${table_prefix}market_offer_offer_id ON public.${table_prefix}market_offer USING btree (offer_id);


DROP TABLE IF EXISTS "${table_prefix}market_offer_forecast";
CREATE TABLE "public"."${table_prefix}market_offer_forecast" (
    "forecast_id" bigint NOT NULL,
    "model_id" bigint NOT NULL,
    "isp_start" integer NOT NULL,
    "range_id" integer NOT NULL,
    "cost_mwh" double precision,
    "ts" bigint NOT NULL,
    "isp_len" integer NOT NULL,
    CONSTRAINT "${table_prefix}market_offer_forecast_market_id_forecast_id_isp_start_rang" PRIMARY KEY (  "forecast_id", "isp_start", "range_id")
)
WITH (oids = false);

CREATE INDEX ${table_prefix}market_offer_forecast_forecast_id ON public.${table_prefix}market_offer_forecast USING btree (forecast_id);

DROP TABLE IF EXISTS "${table_prefix}offer_details";
DROP SEQUENCE IF EXISTS ${table_prefix}offer_details_offer_id_seq;
CREATE SEQUENCE ${table_prefix}offer_details_offer_id_seq INCREMENT 1 MINVALUE 1 MAXVALUE 9223372036854775807 CACHE 1;

CREATE TABLE "public"."${table_prefix}offer_details" (
    "offer_id" bigint DEFAULT nextval('${table_prefix}offer_details_offer_id_seq') NOT NULL,
    "market_id" bigint NOT NULL,
    "ts" bigint NOT NULL,
	"date_str"  character varying(10) NOT NULL,
    "offer_uri" character varying(250),
    "sequence" character varying(10),
    "isp_unit" integer NOT NULL,
    "isp_len" integer NOT NULL,
    "update_ts" bigint NOT NULL,
    "ext" character varying(1000),
    CONSTRAINT "${table_prefix}offer_details_key" PRIMARY KEY ("offer_id")
)
WITH (oids = false);

CREATE UNIQUE INDEX ${table_prefix}offer_details_market_id_ts ON public.${table_prefix}offer_details USING btree (market_id,sequence, ts);
CREATE UNIQUE INDEX ${table_prefix}offer_details_offer_uri ON public.${table_prefix}offer_details USING btree (offer_uri);



ALTER TABLE ONLY "public"."${table_prefix}forecast_details" ADD CONSTRAINT "${table_prefix}forecast_details_model_id_fkey" FOREIGN KEY (model_id) REFERENCES ${table_prefix}forecast_model(model_id) ON UPDATE RESTRICT ON DELETE RESTRICT NOT DEFERRABLE;
ALTER TABLE ONLY "public"."${table_prefix}forecast_details" ADD CONSTRAINT "${table_prefix}forecast_details_offer_id_fkey" FOREIGN KEY (offer_id) REFERENCES ${table_prefix}offer_details(offer_id) ON UPDATE RESTRICT ON DELETE RESTRICT NOT DEFERRABLE;


ALTER TABLE ONLY "public"."${table_prefix}market_offer" ADD CONSTRAINT "${table_prefix}market_offer_offer_id_fkey" FOREIGN KEY (offer_id) REFERENCES ${table_prefix}offer_details(offer_id) ON UPDATE CASCADE ON DELETE CASCADE NOT DEFERRABLE;
ALTER TABLE ONLY "public"."${table_prefix}market_offer" ADD CONSTRAINT "${table_prefix}market_offer_range_id_fkey" FOREIGN KEY (range_id) REFERENCES ${table_prefix}consumption_range(range_id) ON UPDATE RESTRICT ON DELETE RESTRICT NOT DEFERRABLE;

ALTER TABLE ONLY "public"."${table_prefix}market_offer_forecast" ADD CONSTRAINT "${table_prefix}market_offer_forecast_forecast_id_fkey" FOREIGN KEY (forecast_id) REFERENCES ${table_prefix}forecast_details(forecast_id) ON UPDATE CASCADE ON DELETE CASCADE NOT DEFERRABLE;
ALTER TABLE ONLY "public"."${table_prefix}market_offer_forecast" ADD CONSTRAINT "${table_prefix}market_offer_forecast_range_id_fkey" FOREIGN KEY (range_id) REFERENCES ${table_prefix}consumption_range(range_id) ON UPDATE SET NULL ON DELETE SET NULL NOT DEFERRABLE;

ALTER TABLE ONLY "public"."${table_prefix}offer_details" ADD CONSTRAINT "${table_prefix}offer_details_market_id_fkey" FOREIGN KEY (market_id) REFERENCES ${table_prefix}market_details(market_id) ON UPDATE RESTRICT ON DELETE RESTRICT NOT DEFERRABLE;

INSERT INTO   "public"."${table_prefix}consumption_range" ("min_value" , "max_value"  ) VALUES (NULL,NULL);



ALTER TABLE ONLY "public"."${table_prefix}dt_info" ADD CONSTRAINT "${table_prefix}dt_info_market_details_fkey" FOREIGN KEY (market_id) REFERENCES ${table_prefix}market_details(market_id) ON UPDATE CASCADE ON DELETE CASCADE NOT DEFERRABLE;
ALTER TABLE ONLY "public"."${table_prefix}dt_info" ADD CONSTRAINT "${table_prefix}dt_info_service_jobs_fkey" FOREIGN KEY (market_id) REFERENCES ${table_prefix}service_jobs(job_id) ON UPDATE CASCADE ON DELETE CASCADE NOT DEFERRABLE;
-- 2025-11-28 12:49:20 UTC
