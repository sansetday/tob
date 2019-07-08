-- DROP TABLE public.ip_date;

CREATE TABLE public.ip_date
(
  ip text NOT NULL,
  create_date timestamp without time zone DEFAULT (now())::timestamp(0) without time zone,
  update_date timestamp without time zone,
  CONSTRAINT pkey_date_ip PRIMARY KEY (ip)
);
---------------------------------------------------------------------------------------------------------------------------------------------------------------------
-- DROP FUNCTION public.check_ips(text[]);

CREATE OR REPLACE FUNCTION public.check_ips(text[])
  RETURNS void AS
$BODY$
BEGIN
	INSERT INTO public.geoip(ip)
	SELECT u FROM unnest($1) u
	EXCEPT
	SELECT ip FROM public.geoip;

	INSERT INTO public.ip_date (ip)
	SELECT u FROM unnest($1) u
	EXCEPT
	SELECT ip FROM public.ip_date;

END;
$BODY$
  LANGUAGE plpgsql;
---------------------------------------------------------------------------------------------------------------------------------------------------------------------
  -- DROP FUNCTION public.unknown_ips();
  
  
  CREATE OR REPLACE FUNCTION public.unknown_ips()
  RETURNS TABLE(ip text) AS
$BODY$
BEGIN
	RETURN QUERY
	WITH 
		geo AS (
			(SELECT g.ip::text
			FROM public.geoip g
			WHERE g.ip is not null and (country IS NULL OR city IS NULL)
			LIMIT 500) --OR code IS NULL OR latitude IS NULL OR longitude IS NULL
			UNION ALL
			(SELECT d.ip::text
			FROM public.ip_date d
			WHERE d.ip is not null and (d.create_date IS NULL OR d.update_date IS NULL)
			LIMIT 500))
		SELECT g.ip FROM geo g;
END;
$BODY$
  LANGUAGE plpgsql;
---------------------------------------------------------------------------------------------------------------------------------------------------------------------
 -- DROP FUNCTION public.update_ips1(text, text, text, text, text, text, timestamp without time zone);

CREATE OR REPLACE FUNCTION public.update_ips(
    _ip text,
    _country text,
    _code text,
    _city text,
    _lati text,
    _longi text,
    _update_date timestamp without time zone DEFAULT ('now'::text)::timestamp(0) without time zone)
  RETURNS void AS
$BODY$
 DECLARE
	cdate timestamp without time zone;
BEGIN
	UPDATE ONLY public.geoip
	SET country = _country, city = _city, code = _code, latitude = _lati, longitude = _longi
	WHERE ip = _ip;
	
	SELECT create_date FROM public.ip_date
	WHERE ip = _ip INTO cdate;
	
	IF cdate IS NULL
		THEN
			UPDATE public.ip_date
			SET update_date = _update_date, create_date = _update_date
			WHERE ip = _ip;
		ELSE
			UPDATE public.ip_date
			SET update_date = _update_date
			WHERE ip = _ip;
	END IF;
END;
$BODY$
  LANGUAGE plpgsql;
  ---------------------------------------------------------------------------------------------------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION public.update_days()
  RETURNS void AS
$BODY$
BEGIN
	UPDATE public.ip_date
	SET update_date = NULL, create_date = NULL
	WHERE update_date - create_date > interval '3' day;
	
	UPDATE public.ip_date
	SET update_date = NULL, create_date = NULL
	WHERE update_date - create_date < interval '1' day;


END;
$BODY$
  LANGUAGE plpgsql
 